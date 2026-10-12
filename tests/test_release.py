"""Release guard tests: prevent wrong versions, private files and unsafe archives."""

import io
from pathlib import Path
import tarfile
import unittest
import uuid
from zipfile import ZipFile
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release_checks', ROOT / 'scripts/check_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(__file__).resolve().parent / ('fixtures-' + uuid.uuid4().hex)
        self.directory.mkdir()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        for path in self.directory.iterdir():
            path.unlink()
        self.directory.rmdir()

    def test_release_tag_must_match_package_version(self):
        from app import __version__
        self.assertEqual(release.project_version(ROOT, 'v' + __version__), __version__)
        with self.assertRaisesRegex(ValueError, 'Tag must be'):
            release.project_version(ROOT, 'v9.9.9')

    def test_distribution_scan_rejects_private_and_generated_files(self):
        for name in ('.env', 'app/.env.production', 'config.json', 'templates.json',
                     'source.xlsx.bak', '.venv/lib/module.py', '.artifacts/data.xlsx',
                     'tests/fixtures-run/data.csv', 'app/__pycache__/file.pyc'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                release.check_member(name, b'')

    def test_distribution_scan_rejects_credentials_without_printing_them(self):
        secret = b'sk-' + b'a' * 30
        with self.assertRaisesRegex(ValueError, 'Potential API credential') as raised:
            release.check_member('app/settings.py', secret)
        self.assertNotIn(secret.decode(), str(raised.exception))

    def test_distribution_scan_rejects_traversal_paths(self):
        for name in ('../secret', '/absolute', 'app/../../secret', 'app\\secret'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                release.check_member(name, b'')

    def test_source_archive_links_are_refused_without_extraction(self):
        path = self.directory / 'unsafe.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            member = tarfile.TarInfo('package/link')
            member.type = tarfile.SYMTYPE
            member.linkname = '../../private'
            archive.addfile(member)
        with self.assertRaisesRegex(ValueError, 'links'):
            release.distribution_contents(path)

    def test_source_archive_rejects_multiple_roots_and_preserves_payload(self):
        path = self.directory / 'source.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            member = tarfile.TarInfo('package/README.md')
            member.size = len(b'example')
            archive.addfile(member, io.BytesIO(b'example'))
        self.assertEqual(release.distribution_contents(path), {'README.md': b'example'})
        with tarfile.open(path, 'w:gz') as archive:
            for name in ('one/file.py', 'two/file.py'):
                archive.addfile(tarfile.TarInfo(name), io.BytesIO(b''))
        with self.assertRaisesRegex(ValueError, 'top-level'):
            release.distribution_contents(path)

    def test_incomplete_release_artifacts_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            release.check_distributions(ROOT, self.directory, '1.0.0b1')


if __name__ == '__main__':
    unittest.main()
