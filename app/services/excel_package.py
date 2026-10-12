"""Patch worksheet cells without round-tripping unrelated Excel package parts.

Only cell XML and calculation metadata are changed. Unknown drawing, VBA,
extension, relationship and cache parts are copied with their original payloads.
This module does not execute macros, refresh connections, or calculate formulas.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
import math
from numbers import Integral, Real
import posixpath
import re
from xml.parsers import expat
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZipFile

from openpyxl.utils.cell import coordinate_to_tuple, range_boundaries


MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


class WorkbookEditError(ValueError):
    """An edit cannot be applied safely to this workbook."""


@dataclass
class XMLNode:
    name: str
    attrs: dict
    start: int
    open_end: int
    qname: str
    self_closed: bool
    close_start: int = 0
    end: int = 0
    children: list = field(default_factory=list)

    @property
    def local(self):
        return self.name.rsplit("}", 1)[-1]

    @property
    def prefix(self):
        return self.qname.rsplit(":", 1)[0] + ":" if ":" in self.qname else ""


def _tag_end(data, start):
    quote = None
    for index in range(start, len(data)):
        char = data[index]
        if quote:
            if char == quote:
                quote = None
        elif char in (34, 39):
            quote = char
        elif char == 62:
            return index + 1
    raise WorkbookEditError("Incomplete XML markup in the workbook.")


def parse_xml(data):
    # Byte offsets allow every XML fragment outside the edit to stay verbatim,
    # including namespace prefixes referenced by mc:Ignorable and extensions.
    if data.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in data:
        raise WorkbookEditError("This workbook uses an unsupported XML encoding. Resave it as XLSX in Excel.")
    declaration = re.match(br"\s*(?:\xef\xbb\xbf)?<\?xml[^?]*encoding=['\"]([^'\"]+)", data)
    if declaration and declaration.group(1).lower() not in (b"utf-8", b"utf8", b"us-ascii"):
        raise WorkbookEditError("Only UTF-8 workbook XML can be edited safely.")
    parser = expat.ParserCreate(namespace_separator="}")
    stack, roots = [], []

    def refuse(*args):
        raise WorkbookEditError("DTD and entity declarations are not allowed in workbook XML.")

    def start(name, attrs):
        offset = parser.CurrentByteIndex
        end = _tag_end(data, offset)
        token = data[offset:end]
        qname = re.match(br"<([^\s/>]+)", token).group(1).decode("utf-8")
        node = XMLNode(name, attrs, offset, end, qname, token.rstrip().endswith(b"/>"))
        (stack[-1].children if stack else roots).append(node)
        stack.append(node)

    def finish(name):
        node = stack.pop()
        node.close_start = node.open_end if node.self_closed else parser.CurrentByteIndex
        node.end = node.open_end if node.self_closed else _tag_end(data, node.close_start)

    parser.StartElementHandler = start
    parser.EndElementHandler = finish
    parser.StartDoctypeDeclHandler = refuse
    parser.EntityDeclHandler = refuse
    parser.ExternalEntityRefHandler = refuse
    try:
        parser.Parse(data, True)
    except expat.ExpatError as error:
        raise WorkbookEditError(f"Invalid workbook XML: {error}") from error
    if len(roots) != 1:
        raise WorkbookEditError("Workbook XML must have one root element.")
    return roots[0]


def _children(node, local):
    return [child for child in node.children if child.local == local]


def _replace(data, edits):
    previous = len(data) + 1
    for start, end, replacement in sorted(edits, key=lambda edit: (edit[0], edit[1]), reverse=True):
        if end > previous:
            raise WorkbookEditError("Overlapping XML edits were refused.")
        data = data[:start] + replacement + data[end:]
        previous = start
    return data


def _set_attrs(tag, attrs):
    for key, value in attrs.items():
        pattern = rb"(?<![\w:.-])" + key.encode() + rb"\s*=\s*(['\"])[^'\"]*\1"
        tag = re.sub(pattern, b"", tag)
        if value is not None:
            offset = tag.rfind(b"/>") if tag.rstrip().endswith(b"/>") else tag.rfind(b">")
            tag = tag[:offset] + f" {key}={quoteattr(str(value))}".encode("utf-8") + tag[offset:]
    return tag


def _target(part, target):
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(part), target))
    if target.startswith("/"):
        resolved = target.lstrip("/")
    if resolved.startswith("../") or resolved in ("..", ".") or "\\" in resolved:
        raise WorkbookEditError("Invalid internal workbook relationship.")
    return resolved


def _relationships_path(part):
    return posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")


def _validate_archive(archive):
    infos = archive.infolist()
    names = [info.filename for info in infos]
    if len(names) != len(set(names)):
        raise WorkbookEditError("The workbook contains duplicate package parts.")
    if len(infos) > 50000 or sum(info.file_size for info in infos) > 512 * 1024 * 1024:
        raise WorkbookEditError("Workbook exceeds the supported package size (512 MiB / 50,000 parts).")
    if any(info.file_size > 128 * 1024 * 1024 or info.flag_bits & 1 for info in infos):
        raise WorkbookEditError("Encrypted or oversized workbook parts cannot be edited.")


def _workbook(archive):
    root_rels = parse_xml(archive.read("_rels/.rels"))
    relation = next((node for node in root_rels.children
                     if node.attrs.get("Type", "").endswith("/officeDocument")
                     and node.attrs.get("TargetMode") != "External"), None)
    if relation is None:
        raise WorkbookEditError("No spreadsheet workbook relationship was found.")
    workbook_part = _target("", relation.attrs["Target"])
    workbook_xml = archive.read(workbook_part)
    workbook = parse_xml(workbook_xml)
    if workbook.name != MAIN + "}workbook":
        raise WorkbookEditError("This spreadsheet format is unsupported. Resave it as an Excel XLSX workbook.")
    rels_part = _relationships_path(workbook_part)
    rels_xml = archive.read(rels_part)
    relationships = parse_xml(rels_xml)
    by_id = {node.attrs.get("Id"): node for node in relationships.children}
    sheets = []
    for container in _children(workbook, "sheets"):
        for sheet in container.children:
            relation = by_id.get(sheet.attrs.get(REL + "}id"))
            if relation is not None and relation.attrs.get("Type", "").endswith("/worksheet"):
                if relation.attrs.get("TargetMode") == "External":
                    raise WorkbookEditError("External worksheet parts cannot be edited.")
                sheets.append({"name": sheet.attrs["name"],
                               "state": sheet.attrs.get("state", "visible"),
                               "part": _target(workbook_part, relation.attrs["Target"])})
    if not sheets:
        raise WorkbookEditError("The workbook has no editable worksheets.")
    return workbook_part, workbook_xml, workbook, rels_part, rels_xml, relationships, sheets


def inspect_workbook(path):
    with ZipFile(path) as archive:
        _validate_archive(archive)
        return _workbook(archive)[-1]


def _contains(reference, coordinate):
    try:
        left, top, right, bottom = range_boundaries(reference.replace("$", ""))
        row, col = coordinate_to_tuple(coordinate)
        return left <= col <= right and top <= row <= bottom
    except (TypeError, ValueError) as error:
        raise WorkbookEditError("An invalid merged/formula/pivot range prevents safe editing.") from error


def _cell_xml(data, node, coordinate, value, prefix):
    if node:
        if any(key in node.attrs for key in ("cm", "vm")):
            raise WorkbookEditError(f"{coordinate} is a rich/dynamic value. Edit a plain data cell instead.")
        if any(child.local not in ("f", "v", "is") for child in node.children):
            raise WorkbookEditError(f"{coordinate} contains extended cell data that cannot be safely replaced.")
        prefix = node.prefix
        opening = data[node.start:node.open_end]
        if node.self_closed:
            opening = opening.rstrip()[:-2] + b">"
    else:
        opening = f'<{prefix}c r="{coordinate}">'.encode()
    opening = _set_attrs(opening, {"t": None})
    if value is None:
        content = b""
    elif isinstance(value, str):
        if len(value.encode("utf-16-le")) // 2 > 32767:
            raise WorkbookEditError(f"{coordinate} exceeds Excel's 32,767-character cell limit.")
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]", value):
            raise WorkbookEditError(f"{coordinate} contains characters that cannot be written to Excel XML.")
        # Escape Excel's own _xNNNN_ syntax so literal user text stays literal.
        value = re.sub(r"_x[0-9a-fA-F]{4}_", lambda match: "_x005F_" + match.group()[1:], value)
        opening = _set_attrs(opening, {"t": "inlineStr"})
        escaped = escape(value).replace('\r', '&#13;')
        content = (f'<{prefix}is><{prefix}t xml:space="preserve">{escaped}</{prefix}t>'
                   f'</{prefix}is>').encode("utf-8")
    elif isinstance(value, bool):
        opening = _set_attrs(opening, {"t": "b"})
        content = f"<{prefix}v>{int(value)}</{prefix}v>".encode()
    elif isinstance(value, (datetime, date)):
        if isinstance(value, datetime) and value.tzinfo is not None:
            raise WorkbookEditError("Excel does not support timezone-aware cell dates.")
        opening = _set_attrs(opening, {"t": "d"})
        content = f"<{prefix}v>{value.isoformat()}</{prefix}v>".encode()
    elif isinstance(value, (Integral, Real)):
        if not math.isfinite(value):
            raise WorkbookEditError(f"{coordinate} contains a non-finite number.")
        content = f"<{prefix}v>{value}</{prefix}v>".encode()
    else:
        raise WorkbookEditError(f"{coordinate} contains an unsupported cell value type.")
    return opening + content + f"</{prefix}c>".encode()


def _patch_sheet(data, updates):
    root = parse_xml(data)
    if root.name != MAIN + "}worksheet":
        raise WorkbookEditError("This worksheet XML format cannot be edited safely.")
    for protection in _children(root, "sheetProtection"):
        if protection.attrs.get("sheet", "1") not in ("0", "false"):
            raise WorkbookEditError("This worksheet is protected. Unprotect it in Excel before editing.")
    sheet_data = next(iter(_children(root, "sheetData")), None)
    if sheet_data is None or sheet_data.self_closed:
        raise WorkbookEditError("The worksheet has no existing data rows to edit.")
    rows = {int(row.attrs["r"]): row for row in _children(sheet_data, "row")}
    cells = {cell.attrs.get("r"): cell for row in rows.values() for cell in _children(row, "c")}
    for row in rows.values():
        for cell in _children(row, "c"):
            for formula in _children(cell, "f"):
                if formula.attrs.get("t") in ("shared", "array", "dataTable"):
                    if cell.attrs.get("r") in updates or any(
                            _contains(formula.attrs.get("ref", cell.attrs["r"]), coord) for coord in updates):
                        raise WorkbookEditError("An edit overlaps a shared, array, spilled or data-table formula. Edit its input cells instead.")
    for container in _children(root, "mergeCells"):
        for merged in container.children:
            reference = merged.attrs["ref"]
            anchor = reference.split(":")[0].replace("$", "")
            if any(coord != anchor and _contains(reference, coord) for coord in updates):
                raise WorkbookEditError("Only the top-left cell of a merged range can be edited.")
    edits, insertions, missing_rows = [], {}, {}
    for coordinate, value in updates.items():
        row_number, col_number = coordinate_to_tuple(coordinate)
        if coordinate in cells:
            node = cells[coordinate]
            edits.append((node.start, node.end, _cell_xml(data, node, coordinate, value, node.prefix)))
        elif row_number in rows:
            row = rows[row_number]
            xml = _cell_xml(data, None, coordinate, value, row.prefix)
            if row.self_closed:
                missing_rows.setdefault(row_number, []).append((col_number, xml))
            else:
                following = next((cell for cell in _children(row, "c")
                                  if coordinate_to_tuple(cell.attrs["r"])[1] > col_number), None)
                offset = following.start if following else row.close_start
                insertions.setdefault(offset, []).append((col_number, xml))
        else:
            xml = _cell_xml(data, None, coordinate, value, sheet_data.prefix)
            missing_rows.setdefault(row_number, []).append((col_number, xml))
    for row_number, values in missing_rows.items():
        row = rows.get(row_number)
        opening = data[row.start:row.open_end].rstrip()[:-2] + b">" if row else (
            f'<{sheet_data.prefix}row r="{row_number}">'.encode())
        prefix = row.prefix if row else sheet_data.prefix
        xml = opening + b"".join(value for _, value in sorted(values)) + f"</{prefix}row>".encode()
        if row:
            edits.append((row.start, row.end, xml))
        else:
            following = next((item for number, item in sorted(rows.items()) if number > row_number), None)
            offset = following.start if following else sheet_data.close_start
            insertions.setdefault(offset, []).append((row_number, xml))
    for offset, values in insertions.items():
        edits.append((offset, offset, b"".join(value for _, value in sorted(values))))
    result = _replace(data, edits)
    parse_xml(result)
    return result


def _recalculation(data, workbook):
    nodes = _children(workbook, "calcPr")
    values = {"fullCalcOnLoad": "1", "forceFullCalc": "1", "calcCompleted": "0"}
    if nodes:
        node = nodes[0]
        return _replace(data, [(node.start, node.open_end, _set_attrs(data[node.start:node.open_end], values))])
    # calcPr precedes these optional workbook children in the schema.
    after = {"oleSize", "customWorkbookViews", "pivotCaches", "smartTagPr", "smartTagTypes",
             "webPublishing", "fileRecoveryPr", "webPublishObjects", "extLst"}
    offset = next((node.start for node in workbook.children if node.local in after), workbook.close_start)
    return _replace(data, [(offset, offset,
        f'<{workbook.prefix}calcPr fullCalcOnLoad="1" forceFullCalc="1" calcCompleted="0"/>'.encode())])


def save_patched_workbook(source, destination, sheet_name, updates):
    """Copy a package, replacing only reviewed scalar data cells and calc metadata."""
    with ZipFile(source) as archive:
        _validate_archive(archive)
        if any(name.startswith("_xmlsignatures/") for name in archive.namelist()):
            raise WorkbookEditError("This workbook has a document signature. Editing would invalidate it; save an unsigned copy in Excel first.")
        book_part, book_xml, book, rels_part, rels_xml, rels, sheets = _workbook(archive)
        sheet = next((sheet for sheet in sheets if sheet["name"] == sheet_name), None)
        if sheet is None:
            raise WorkbookEditError("The selected worksheet is no longer present.")
        changed, removed = {}, set()
        if updates:
            # Pivot output is computed data. Preserve the pivot and edit its source instead.
            sheet_rels = _relationships_path(sheet["part"])
            if sheet_rels in archive.namelist():
                for relation in parse_xml(archive.read(sheet_rels)).children:
                    if relation.attrs.get("Type", "").endswith("/pivotTable"):
                        pivot = parse_xml(archive.read(_target(sheet["part"], relation.attrs["Target"])))
                        for location in _children(pivot, "location"):
                            if any(_contains(location.attrs["ref"], coord) for coord in updates):
                                raise WorkbookEditError("Pivot-table output cells cannot be edited. Transform source data and refresh the pivot in Excel.")
            changed[sheet["part"]] = _patch_sheet(archive.read(sheet["part"]), updates)
            changed[book_part] = _recalculation(book_xml, book)
            # An edited formula must not remain in a stale calculation chain.
            chain_rels = [node for node in rels.children if node.attrs.get("Type", "").endswith("/calcChain")]
            if chain_rels:
                removed = {_target(book_part, node.attrs["Target"]) for node in chain_rels}
                changed[rels_part] = _replace(rels_xml, [(node.start, node.end, b"") for node in chain_rels])
                types_xml = archive.read("[Content_Types].xml")
                types = parse_xml(types_xml)
                changed["[Content_Types].xml"] = _replace(types_xml, [
                    (node.start, node.end, b"") for node in types.children
                    if node.attrs.get("PartName", "").lstrip("/") in removed])
        for data in changed.values():
            parse_xml(data)
        with ZipFile(destination, "w") as output:
            output.comment = archive.comment
            for info in archive.infolist():
                if info.filename not in removed:
                    output.writestr(info, changed.get(info.filename, archive.read(info.filename)))
    with ZipFile(destination) as output:
        if output.testzip() is not None:
            raise WorkbookEditError("Workbook package verification failed; no source changes were saved.")
