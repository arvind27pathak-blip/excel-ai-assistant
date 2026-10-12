"""Check version/tag consistency and distribution contents before a release."""

import argparse
import ast
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib
from zipfile import ZipFile


def project_version(root, tag=None):
    project = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))['project']
    tree = ast.parse((root / 'app/__init__.py').read_text(encoding='utf-8'))
    versions = [ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == '__version__' for target in node.targets)]
    if versions != [project['version']]:
        raise ValueError('Application and package versions disagree.')
    if tag is not None and tag != 'v' + project['version']:
        raise ValueError(f'Tag must be v{project["version"]}.')
    if not re.fullmatch(r'\d+\.\d+\.\d+b\d+', project['version']):
        raise ValueError('This release path is for beta versions; stable releases require a new readiness review.')
    return project['version']


def check_member(name, payload):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name:
        raise ValueError(f'Unsafe archive path: {name}')
    forbidden = {'.git', '.artifacts', 'wheelhouse', 'node_modules', '__pycache__'}
    if any(part in forbidden or part.startswith(('.venv', 'fixtures-', 'tmp')) for part in path.parts):
        raise ValueError(f'Local artifacts found in distribution: {name}')
    if path.name.startswith('.env') or path.name in {'config.json', 'templates.json'} or path.suffix in {'.bak', '.log', '.pyc', '.pyo', '.pem', '.key'}:
        raise ValueError(f'Private or generated file found in distribution: {name}')
    if re.search(rb'sk-(?:proj-)?[A-Za-z0-9_-]{20,}', payload):
        raise ValueError(f'Potential API credential found in distribution: {name}')


def distribution_contents(path):
    if path.name.endswith('.whl'):
        with ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('Duplicate wheel members.')
            return {name: archive.read(name) for name in names if not name.endswith('/')}
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        if any(not (member.isfile() or member.isdir()) for member in members):
            raise ValueError('Source archives must not contain links or special files.')
        names = [member.name for member in members if member.isfile()]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate source archive members.')
        roots = {PurePosixPath(name).parts[0] for name in names}
        if len(roots) != 1:
            raise ValueError('Source archives must have exactly one top-level directory.')
        result = {}
        for member in members:
            if member.isfile():
                check_member(member.name, b'')
                result[str(PurePosixPath(member.name).relative_to(next(iter(roots))))] = archive.extractfile(member).read()
        return result


def check_distributions(root, directory, version):
    wheels = list(directory.glob('*.whl'))
    sources = list(directory.glob('*.tar.gz'))
    if len(wheels) != 1 or len(sources) != 1:
        raise ValueError('Expected exactly one wheel and one source distribution in a fresh output directory.')
    expected_modules = {path.relative_to(root).as_posix() for path in (root / 'app').rglob('*.py')}
    report = []
    for path in wheels + sources:
        contents = distribution_contents(path)
        for name, payload in contents.items():
            check_member(name, payload)
        required = set(expected_modules)
        if path.suffix == '.whl':
            prefix = f'excel_ai_assistant-{version}.dist-info/'
            required.update(prefix + name for name in ('METADATA', 'WHEEL', 'RECORD', 'entry_points.txt', 'licenses/LICENSE'))
            metadata_name = prefix + 'METADATA'
            if any(not (name.startswith('app/') or name.startswith(prefix)) for name in contents):
                raise ValueError('Application wheel includes unexpected top-level files.')
            if 'excel-ai-assistant = app.__main__:main' not in contents.get(prefix + 'entry_points.txt', b'').decode():
                raise ValueError('Installed launcher is missing.')
        else:
            required.update({'pyproject.toml', 'README.md', 'LICENSE', 'MANIFEST.in', 'CHANGELOG.md',
                             'SECURITY.md', 'CONTRIBUTING.md', 'requirements-test.txt',
                             'tests/workbook_fixtures.py', 'scripts/check_release.py'})
            required.update(path.relative_to(root).as_posix() for path in (root / 'tests').glob('test_*.py'))
            metadata_name = 'PKG-INFO'
        if required - contents.keys():
            raise ValueError(f'{path.name} is missing required files: {sorted(required - contents.keys())}')
        metadata = BytesParser().parsebytes(contents[metadata_name])
        if metadata['Name'] != 'excel-ai-assistant' or metadata['Version'] != version or metadata['License-Expression'] != 'MIT':
            raise ValueError(f'{path.name} has incorrect name, version or license metadata.')
        report.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'members': len(contents)})
    (directory / 'SHA256SUMS').write_text(''.join(f'{item["sha256"]}  {item["file"]}\n' for item in report), encoding='utf-8')
    (directory / 'release-check.json').write_text(json.dumps({'version': version, 'artifacts': report}, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag')
    parser.add_argument('--dist', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        version = project_version(root, args.tag)
        if args.dist:
            check_distributions(root, args.dist, version)
        print(f'Release checks passed for {version}')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Release check failed: {error}\n')


if __name__ == '__main__':
    main()
