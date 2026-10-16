import json
import sys
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from counter_labels import apply_counter_labels

class CounterLabelsTests(unittest.TestCase):
    def test_every_locale_removes_fixed_date_and_preserves_count_and_failure_nodes(self):
        labels=json.loads((ROOT/'content/counter-labels.json').read_text())
        for language in labels:
            soup=BeautifulSoup((ROOT/'site'/language/'index.html').read_text(),'html.parser')
            count=str(soup.select_one('[data-view-count]'))
            failure=str(soup.select_one('[data-view-unavailable]'))
            apply_counter_labels(soup,labels)
            marker=soup.select_one('[data-view-label]')
            self.assertEqual(marker.text,labels[language]['neutral'])
            self.assertEqual(marker['data-since-label'],labels[language]['since'])
            self.assertEqual(str(soup.select_one('[data-view-count]')),count)
            self.assertEqual(str(soup.select_one('[data-view-unavailable]')),failure)
