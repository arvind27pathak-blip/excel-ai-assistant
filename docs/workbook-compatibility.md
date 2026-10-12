# Workbook compatibility and installation evidence

Reviewed 2026-10-11. The supported operation is reviewing and replacing scalar data cells in an existing worksheet. This does not provide a complete Excel calculation or automation engine.

## Save design

The application loads a worksheet for selection and review, then saves by patching cell XML in the original ZIP package. It does not save the original workbook through openpyxl. XML outside the replaced cells remains verbatim, including namespace prefixes and extension markup. Unchanged package members retain their original uncompressed bytes and ZIP metadata. Worksheet names resolve through workbook relationships rather than assuming `sheet1.xml`.

Calculation properties request recalculation in Excel, and stale calculation-chain parts and their references are removed on edits. Existing manual calculation mode is retained. Microsoft documents the calculation chain as optional in [Working with the calculation chain](https://learn.microsoft.com/en-us/office/open-xml/spreadsheet/working-with-the-calculation-chain). Formula results and chart/pivot caches may remain stale until Excel recalculates or refreshes them.

Generated text is written as an inline string, including text starting with `=`. Whitespace is preserved and XML characters are escaped. Microsoft describes inline/shared string representations and whitespace in [Working with the shared string table](https://learn.microsoft.com/en-us/office/open-xml/spreadsheet/working-with-the-shared-string-table?tabs=cs).

## Tested support contract

| Feature | Behavior and evidence |
| --- | --- |
| Multiple worksheets, including hidden sheets and names with commas | Select a worksheet; save only that sheet's changed cells. Tests verify other sheet bytes and unsaved-edit cancellation. |
| Scalar text, numeric, boolean and date cells | Existing cell styles remain attached; text identifiers retain leading zeros. Tests include dates, Unicode, XML characters, whitespace and formula-looking text. |
| Ordinary formulas | Unchanged formulas are preserved; replacing an ordinary formula writes reviewed text. The app does not evaluate formulas. |
| Charts, images, tables, styles, comments, hyperlinks, validation, conditional formatting, print settings, names, merged ranges | Real generated chart/image/table fixture; all unrelated package payloads compared before/after; the edited workbook is reopened with openpyxl. Tables are not resized. |
| Slicers, pivot caches, ActiveX, embedded objects, custom XML and unknown extensions | Package payload preservation tested with synthetic opaque parts and worksheet extensions. This is not proof of valid Excel runtime behavior for each feature. |
| VBA project and project-signature binaries | Copied unchanged in `.xlsm` packages. Tests use synthetic binary payloads, not executable macros. VBA is neither executed nor validated. |
| Shared, array, spilled and data-table formula groups | Overlapping edits are refused; edit input cells. Array and shared-formula guard tests cover masters, followers and ranges. Rich/dynamic metadata on the edited cell is also refused. |
| Pivot output cells | Refused using pivot location relationships. Synthetic pivot-location fixture verifies the guard and preserves the pivot part when source cells change. Refresh in Excel. |
| Protected worksheets, non-anchor merged cells | Save refused; original file and pending edits retained. Unprotect in Excel or edit the merged anchor. |
| Document-signed workbook | Save refused to avoid invalidating signatures, consistent with Microsoft's [signature troubleshooting guidance](https://learn.microsoft.com/en-us/troubleshoot/microsoft-365-apps/excel/document-contains-invalid-signatures-error). A VBA project signature is a distinct package part. |
| Malformed, encrypted, oversized, Strict OOXML or unsupported XML-encoding packages | Refused. DTD/entity declarations and duplicate ZIP parts are rejected. Legacy `.xls` must be converted first. |

The worksheet's first row is its header row; the application does not discover arbitrary tables farther down a sheet. No row/column insertion, table expansion, advanced feature authoring, connection refresh, macro execution or Excel calculation is offered. Changing an input may require reopening/recalculating or refreshing in Excel before dependent displays update. Existing external links and active content are preserved, not sanitized. Very large workbooks are outside the release scope even below the package size limits.

## Reproduce representative workbook evidence

```powershell
python -m pip install . -r requirements-test.txt
python -m unittest discover -s tests -v
python scripts/generate_workbook_samples.py
```

The generator creates `.artifacts/workbooks/representative-advanced.xlsx`, `representative-edited.xlsx` and `preservation-report.json`. Only `xl/worksheets/sheet1.xml` and `xl/workbook.xml` should differ for that fixture. Test fixtures contain non-sensitive generated data. Genuine customer workbooks, executable VBA and opening the result in Microsoft Excel remain release checks.

## Installation evidence

Local validation uses Windows and an isolated Python 3.14 virtual environment with system site packages disabled. The application wheel is built with the declared setuptools backend and installed with runtime dependencies from original locally cached wheels using `--no-index`. Package imports resolve to the environment's `site-packages`, verified from outside the source directory with `-I`. Both `python -I -m app --check-install` and `excel-ai-assistant --check-install` create a real Tk root successfully; `pip check` reports no broken requirements. Automated tests also run against this installed package.

This managed environment makes Python-created restricted temporary directories inaccessible. Local build/install verification therefore uses a workspace-only temporary-directory adapter; it does not change the shipped wheel or dependencies. Network installation from PyPI and an unmodified clean OS installation were not tested. Python 3.13 native wheels are absent from the local cache, so that isolated installation is not claimed. CI defines normal wheel builds/installations for Windows/Linux on Python 3.13/3.14; it has not executed here. macOS, real-provider calls and vulnerability scanning remain unverified. The historical uv lock needs tool-based regeneration/validation before it is recommended for Python 3.14.
