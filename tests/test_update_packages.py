import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('updater', Path(__file__).parents[1] / 'scripts/update-packages.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UpdateTests(unittest.TestCase):
    def test_version_parsing(self):
        self.assertEqual(updater.parse_version('baidunetdisk', json.dumps({'results': [{'Version': '8.9.8-1'}]})), '8.9.8')
        self.assertEqual(updater.parse_version('lceda-pro', 'lceda-pro-linux-x64-4.2.1.zip ' * 2), '4.2.1')
        with self.assertRaises(ValueError):
            updater.parse_version('lceda-pro', 'lceda-pro-linux-x64-4.2.1.zip lceda-pro-linux-x64-4.2.2.zip')

    def test_update_only_source_hash_and_refuse_downgrade(self):
        original = 'version = "1.2.3";\nsrc = fetchurl {\n  hash = "sha256-old";\n};\nnarHash = "sha256-other";\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'default.nix'
            path.write_text(original)
            with patch.object(updater, 'latest_version', return_value='1.2.4'), patch.object(updater, 'source_hash', return_value='sha256-new'):
                updater.update_package('baidunetdisk', path)
            self.assertIn('version = "1.2.4";', path.read_text())
            self.assertIn('hash = "sha256-new";', path.read_text())
            self.assertIn('narHash = "sha256-other";', path.read_text())
            with patch.object(updater, 'latest_version', return_value='1.2.3'):
                with self.assertRaises(ValueError):
                    updater.update_package('baidunetdisk', path)

    def test_source_hash_is_sri_sha256(self):
        def download(url, path):
            path.write_bytes(b'abc')
        with patch.object(updater, 'curl', side_effect=download):
            self.assertEqual(updater.source_hash('https://example.test/source'),
                             'sha256-ungWv48Bz+pBQUDeXa4iI7ADYaOWF3qctBD/YfIAFa0=')

    def test_unchanged_skips_download(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'default.nix'
            path.write_text('version = "1.2.3";\nsrc = fetchurl { hash = "sha256-old"; };')
            with patch.object(updater, 'latest_version', return_value='1.2.3'), patch.object(updater, 'source_hash', side_effect=AssertionError('unexpected download')):
                updater.update_package('baidunetdisk', path)


if __name__ == '__main__':
    unittest.main()
