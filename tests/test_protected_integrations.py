"""Integrity gate: detect accidental deployment changes, never touch production."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

spec = importlib.util.spec_from_file_location('protected_gate', Path(__file__).resolve().parents[1] / 'scripts/check_protected_integrations.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class ProtectedIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / 'booking').mkdir()
        (self.root / 'booking/module.js').write_text('synthetic fixture only')
        self.before = gate.capture(self.root, ['booking'])

    def test_unchanged_and_unrelated_content(self):
        (self.root / 'page.html').write_text('new website content')
        result = gate.compare(self.root, self.before)
        self.assertEqual(result, {'changed': [], 'removed': [], 'added': [], 'filesChecked': 1})

    def test_changed_deleted_added_files(self):
        (self.root / 'booking/module.js').write_text('changed')
        (self.root / 'booking/new.js').write_text('new')
        result = gate.compare(self.root, self.before)
        self.assertEqual(result['changed'], ['booking/module.js'])
        self.assertEqual(result['added'], ['booking/new.js'])
        (self.root / 'booking/module.js').unlink()
        self.assertEqual(gate.compare(self.root, self.before)['removed'], ['booking/module.js'])

    def test_missing_selection_fails_closed(self):
        (self.root / 'booking/module.js').unlink()
        (self.root / 'booking').rmdir()
        with self.assertRaises(ValueError):
            gate.compare(self.root, self.before)

    def test_traversal_and_symlink_rejected(self):
        with self.assertRaises(ValueError):
            gate.capture(self.root, ['../outside'])
        (self.root / 'booking/link').symlink_to(self.root / 'booking/module.js')
        with self.assertRaises(ValueError):
            gate.compare(self.root, self.before)

    def test_empty_baseline_rejected(self):
        with self.assertRaises(ValueError):
            gate.capture(self.root, [])
        with self.assertRaises(ValueError):
            gate.compare(self.root, {'format': 1, 'selections': [], 'files': {}})

    def test_cli_requires_external_baseline_and_never_overwrites_it(self):
        script = str(Path(gate.__file__))
        inside = subprocess.run([sys.executable, script, 'capture', '--root', str(self.root), '--manifest', str(self.root / 'baseline.json'), '--protect', 'booking'], capture_output=True)
        self.assertEqual(inside.returncode, 1)
        self.assertFalse((self.root / 'baseline.json').exists())
        with tempfile.TemporaryDirectory() as outside:
            baseline = Path(outside) / 'baseline.json'
            args = [sys.executable, script, '--root', str(self.root), '--manifest', str(baseline)]
            captured = subprocess.run([*args, 'capture', '--protect', 'booking'], capture_output=True)
            self.assertEqual(captured.returncode, 0, captured.stdout)
            original = baseline.read_bytes()
            checked = subprocess.run([*args, 'check'], capture_output=True)
            self.assertEqual(checked.returncode, 0, checked.stdout)
            (self.root / 'booking/module.js').write_text('changed')
            self.assertEqual(subprocess.run([*args, 'check'], capture_output=True).returncode, 1)
            self.assertEqual(subprocess.run([*args, 'capture', '--protect', 'booking'], capture_output=True).returncode, 1)
            self.assertEqual(baseline.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
