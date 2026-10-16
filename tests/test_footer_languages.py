"""Regression coverage for the previously stale seven-language footer."""
import sys
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from footer_languages import apply_footer_languages

class FooterLanguagesTests(unittest.TestCase):
    def test_release_order_replaces_stale_inventory_and_preserves_other_content(self):
        soup = BeautifulSoup('<footer><div class="footer-bottom"><span>Copyright</span><span>PL / EN / DE / 中文 / УКР / ES / IT</span></div></footer>', 'html.parser')
        languages = ['pl', 'en', 'cs', 'de', 'zh-Hans', 'uk', 'es', 'it']
        apply_footer_languages(soup, languages)
        marker = soup.select_one('[data-language-inventory]')
        self.assertEqual(marker.text, 'PL / EN / CS / DE / 中文 / УКР / ES / IT')
        self.assertEqual(marker['translate'], 'no')
        self.assertEqual(soup.span.text, 'Copyright')
        first = str(soup)
        apply_footer_languages(soup, languages)
        self.assertEqual(str(soup), first)
        apply_footer_languages(soup, ['pl', 'cs', 'en'])
        self.assertEqual(marker.text, 'PL / CS / EN')

    def test_no_footer_is_safe(self):
        soup = BeautifulSoup('<main>Content</main>', 'html.parser')
        apply_footer_languages(soup, ['pl', 'cs'])
        self.assertEqual(str(soup), '<main>Content</main>')
