"""Create a real workbook and an edited copy with package preservation evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from workbook_fixtures import create_representative_workbook
from app.services.excel_package import save_patched_workbook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.artifacts/workbooks'))
    directory = parser.parse_args().output.resolve()
    source = create_representative_workbook(directory)
    target = directory / 'representative-edited.xlsx'
    save_patched_workbook(source, target, 'Sales', {'B2': 'Reviewed description'})
    with ZipFile(source) as before, ZipFile(target) as after:
        inventory = [{'part': name,
                      'before_sha256': hashlib.sha256(before.read(name)).hexdigest(),
                      'after_sha256': hashlib.sha256(after.read(name)).hexdigest(),
                      'unchanged': before.read(name) == after.read(name)}
                     for name in before.namelist()]
    report = {'source': source.name, 'edited': target.name, 'parts': inventory,
              'changed_parts': [item['part'] for item in inventory if not item['unchanged']],
              'limitations': 'Generated real chart/image/table fixture; no Excel runtime or real VBA execution validation.'}
    (directory / 'preservation-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(directory)


if __name__ == '__main__':
    main()
