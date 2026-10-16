import json,unittest,datetime,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
LANGUAGES=[language.lower() for language in json.loads((R/'release.json').read_text())['languages']]
@unittest.skipUnless((R/'_production_ready/sitemap.xml').exists(),'Build production-ready before artifact acceptance')
class Audit3Artifacts(unittest.TestCase):
 def test_excluded_pages_are_available_but_never_advertised_to_indexers(self):
  routes=json.loads((R/'routes.json').read_text());excluded=json.loads((R/'seo/indexing-policy.json').read_text())['excludedRoutes'];self.assertEqual(len(excluded),33*len(LANGUAGES))
  locs={e.text for e in ET.parse(R/'_production_ready/sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')};self.assertEqual(locs,{'https://hornigold.pl'+r for r in routes if r not in excluded})
  for route in excluded:
   soup=BeautifulSoup((R/'_production_ready'/unquote(route).strip('/')/'index.html').read_text(),'html.parser');self.assertEqual(soup.select_one('meta[name=robots]')['content'],'noindex,follow');self.assertFalse(soup.select('link[hreflang]'));self.assertEqual([a['data-language'] for a in soup.select('[data-language-switcher] a[data-language]')],LANGUAGES)
 def test_sitemap_dates_are_not_future_dates_and_manifest_icons_exist(self):
  routes=json.loads((R/'routes.json').read_text());excluded=json.loads((R/'seo/indexing-policy.json').read_text())['excludedRoutes']
  dates=ET.parse(R/'_production_ready/sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod');self.assertEqual(len(dates),sum(route not in excluded for route in routes))
  for d in dates:self.assertLessEqual(datetime.date.fromisoformat(d.text),datetime.datetime.now(datetime.timezone.utc).date())
  manifest=json.loads((R/'_production_ready/site.webmanifest').read_text());self.assertEqual({i['sizes'] for i in manifest['icons']},{'192x192','512x512'})
  for i in manifest['icons']:self.assertTrue((R/'_production_ready'/i['src'].lstrip('/')).is_file())
  self.assertEqual((R/'site/favicon.ico').read_bytes()[:6],b'\x00\x00\x01\x00\x01\x00')
 def test_approved_social_identities_are_visible(self):
  soup=BeautifulSoup((R/'_production_ready/pl/index.html').read_text(),'html.parser');nodes=json.loads(soup.select_one('script[type="application/ld+json"]').string)['@graph'];links={a['href'] for a in soup.select('a[href]')}
  for node in nodes:
   if node['@type'] in ['Organization','LodgingBusiness']:self.assertEqual(len(node['sameAs']),3);self.assertTrue(set(node['sameAs'])<=links)
