"""A Polish-only article must not invent translations or weaken other clusters."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from seo import LANGS, ORIGIN, PREVIEW_ROBOTS, apply_seo, hreflang_languages, single_locale_routes

ARTICLE = '/pl/artykuly/od-opinii-goscia-do-poprawy-jakosci/'
OG_ALTERNATES = ['en_GB', 'de_DE', 'zh_CN', 'uk_UA', 'es_ES', 'it_IT']


class EditorialSeo(unittest.TestCase):
    def soup(self, route):
        alternates = ''.join(
            f'<link rel="alternate" hreflang="{language}" href="{ORIGIN}/{language}/">'
            for language in sorted(LANGS | {'x-default'})
        )
        og_alternates = ''.join(
            f'<meta property="og:locale:alternate" content="{locale}">'
            for locale in OG_ALTERNATES
        )
        return BeautifulSoup(
            '<html lang="pl"><head><title>Editorial test</title>'
            '<meta name="description" content="A method for working with guest feedback">'
            + alternates + og_alternates + '</head><body><main><h1>Editorial test</h1></main></body></html>',
            'html.parser',
        )

    def test_only_exact_registered_article_gets_single_locale_exception(self):
        self.assertEqual(hreflang_languages(ROOT, ARTICLE), {'pl', 'x-default'})
        for route in ['/pl/', '/en/', '/pl/artykuly/not-approved/']:
            self.assertEqual(hreflang_languages(ROOT, route), LANGS | {'x-default'})

    def test_polish_article_has_self_cluster_in_both_build_modes(self):
        for mode in ['preview', 'production-ready']:
            with self.subTest(mode=mode):
                soup = self.soup(ARTICLE)
                apply_seo(soup, ARTICLE, ROOT, mode, {ARTICLE: ARTICLE}, {})
                alternates = soup.select('link[rel=alternate][hreflang]')
                self.assertEqual(len(alternates), 2)
                self.assertEqual({tag['hreflang']: tag['href'] for tag in alternates},
                                 {'pl': ORIGIN + ARTICLE, 'x-default': ORIGIN + ARTICLE})
                self.assertEqual(soup.select_one('link[rel=canonical]')['href'], ORIGIN + ARTICLE)
                expected = PREVIEW_ROBOTS if mode == 'preview' else 'index,follow'
                self.assertEqual(soup.select_one('meta[name=robots]')['content'], expected)

    def test_polish_article_does_not_advertise_unavailable_og_locales(self):
        for mode in ['preview', 'production-ready']:
            with self.subTest(mode=mode):
                soup = self.soup(ARTICLE)
                self.assertEqual(len(soup.select('meta[property="og:locale:alternate"]')), 6)
                apply_seo(soup, ARTICLE, ROOT, mode, {ARTICLE: ARTICLE}, {})
                self.assertEqual(soup.select('meta[property="og:locale:alternate"]'), [])

    def test_existing_multilingual_cluster_is_preserved(self):
        soup = self.soup('/pl/')
        before = [str(tag) for tag in soup.select('link[rel=alternate][hreflang]')]
        apply_seo(soup, '/pl/', ROOT, 'production-ready', {'/pl/': '/pl/'}, {})
        self.assertEqual([str(tag) for tag in soup.select('link[rel=alternate][hreflang]')], before)

    def test_existing_og_locale_clusters_are_preserved_in_both_build_modes(self):
        for route in ['/pl/', '/en/', '/pl/artykuly/not-approved/']:
            for mode in ['preview', 'production-ready']:
                with self.subTest(route=route, mode=mode):
                    soup = self.soup(route)
                    before = [str(tag) for tag in soup.select('meta[property="og:locale:alternate"]')]
                    apply_seo(soup, route, ROOT, mode, {route: route}, {})
                    self.assertEqual([str(tag) for tag in soup.select('meta[property="og:locale:alternate"]')], before)

    def test_single_locale_allowlist_requires_matching_article_language(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'content').mkdir()
            (root / 'content/editorial-articles.json').write_text(json.dumps({
                'singleLocaleRoutes': [ARTICLE],
                'articles': [{'id': 'PR-002', 'route': ARTICLE, 'language': 'en'}],
            }))
            with self.assertRaises(ValueError):
                single_locale_routes(root)


if __name__ == '__main__':
    unittest.main()
