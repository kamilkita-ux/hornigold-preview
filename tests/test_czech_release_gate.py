import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('czech_gate', Path(__file__).parents[1] / 'scripts/check_czech_locale.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CzechReleaseGateTests(unittest.TestCase):
    def fixture(self, root):
        folder = root / 'content/localization'
        folder.mkdir(parents=True)
        page = root / 'site/en/index.html'
        page.parent.mkdir(parents=True)
        page.write_text('<h1>Rooms</h1>')
        config = {'order': ['pl', 'en', 'cs', 'de'],
                  'sourcePages': {'site/en/index.html': hashlib.sha256(page.read_bytes()).hexdigest()},
                  'legalHtmlAndPdfVerified': True, 'routeAndLanguageTestsPassed': True,
                  'externalBookingLanguageDisclosed': True}
        row = {'id': hashlib.sha256(b'Rooms').hexdigest()[:16], 'source': 'Rooms',
               'translation': 'Pokoje', 'reviewed': True}
        (folder / 'cs-rollout.json').write_text(json.dumps(config))
        (folder / 'cs-translations.json').write_text(json.dumps([row]))
        return folder, page, row

    def test_unreviewed_translation_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder, _, row = self.fixture(root)
            self.assertTrue(module.audit(root)['publicationReady'])
            row['reviewed'] = False
            (folder / 'cs-translations.json').write_text(json.dumps([row]))
            self.assertFalse(module.audit(root)['publicationReady'])

    def test_source_change_invalidates_previous_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, page, _ = self.fixture(root)
            page.write_text('<h1>Rooms and apartments</h1>')
            self.assertFalse(module.audit(root)['publicationReady'])


if __name__ == '__main__':
    unittest.main()
