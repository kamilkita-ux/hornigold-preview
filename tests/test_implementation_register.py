"""Keep all 34 owner requirements represented; summaries cannot certify completion."""
import collections
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ImplementationRegisterTests(unittest.TestCase):
    def setUp(self):
        self.directory = ROOT / 'docs/implementation'
        self.register = json.loads((self.directory / 'REGISTER.json').read_text())

    def test_exact_scope_and_summary_counts(self):
        expected = [f'{group}{number}' for group, total in [('A', 7), ('B', 3), ('C', 4), ('D', 3), ('E', 4), ('F', 2), ('G', 5), ('H', 1), ('I', 3), ('J', 2)] for number in range(1, total + 1)]
        items = self.register['items']
        self.assertCountEqual([item['id'] for item in items], expected)
        self.assertEqual(self.register['counts'], dict(collections.Counter(item['status'] for item in items)))

    def test_referenced_evidence_exists(self):
        for item in self.register['items']:
            for reference in item.get('evidence', []):
                with self.subTest(item=item['id'], reference=reference):
                    target = (self.directory / reference).resolve()
                    self.assertIn(ROOT, target.parents)
                    self.assertTrue(target.is_file())


if __name__ == '__main__':
    unittest.main()
