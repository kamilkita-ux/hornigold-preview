"""Safety regressions for isolated indexable artifacts and conservative structured data."""
import sys,unittest,tempfile,json,subprocess,hashlib
from pathlib import Path
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'scripts'))
from seo import apply_seo,write_indexing_files,PREVIEW_ROBOTS,visible_image_objects

class SeoSafety(unittest.TestCase):
    def test_image_schema_uses_only_visible_existing_local_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); assets=root/'site/assets';assets.mkdir(parents=True)
            (assets/'known.webp').write_bytes(b'fixture')
            (root/'private.webp').write_bytes(b'private')
            s=BeautifulSoup('''<main>
              <img src="/assets/known.webp?v=1" alt="Ilustracja: wejście">
              <img src="/assets/known.webp" alt="Duplicate">
              <img src="https://other.example/image.jpg" alt="External">
              <img src="/assets/missing.webp" alt="Missing">
              <img src="/assets/%2e%2e/%2e%2e/private.webp" alt="Traversal">
              <img src="/assets/known.webp" alt="">
            </main>''','html.parser')
            images=visible_image_objects(s,root)
            self.assertEqual(len(images),1)
            self.assertEqual(images[0]['contentUrl'],'https://hornigold.pl/assets/known.webp')
            self.assertEqual(images[0]['description'],'Ilustracja: wejście')
            self.assertEqual(set(images[0]),{'@type','@id','contentUrl','description'})
    def test_hidden_and_decorative_images_are_not_described(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);assets=root/'site/assets';assets.mkdir(parents=True)
            (assets/'known.webp').write_bytes(b'fixture')
            s=BeautifulSoup('''<main><div hidden><img src="/assets/known.webp" alt="Hidden"></div>
              <img aria-hidden="true" src="/assets/known.webp" alt="Hidden">
              <img src="/assets/known.webp" alt=""></main>''','html.parser')
            self.assertEqual(visible_image_objects(s,root),[])
    def soup(self):
        return BeautifulSoup('<html lang="pl"><head><title>Page</title><meta name="description" content="Known page"><meta name="robots" content="index,follow"><script type="application/ld+json">{"@type":"Hotel","priceRange":"unknown","numberOfRooms":999}</script></head><body><h1>Page</h1></body></html>','html.parser')
    def test_preview_overrides_existing_index_permission(self):
        s=self.soup();apply_seo(s,'/pl/',R,'preview',{'/pl/':'/pl/'},{})
        self.assertEqual(s.select_one('meta[name=robots]')['content'],PREVIEW_ROBOTS)
    def test_production_only_canonical_is_indexable(self):
        for route,expected in [('/pl/','index,follow'),('/old/',PREVIEW_ROBOTS),('/404.html',PREVIEW_ROBOTS)]:
            s=self.soup();apply_seo(s,route,R,'production-ready',{'/pl/':'/pl/'},{})
            self.assertEqual(s.select_one('meta[name=robots]')['content'],expected)
    def test_no_unverified_commercial_schema_leaks(self):
        s=self.soup();apply_seo(s,'/pl/',R,'production-ready',{'/pl/':'/pl/'},{})
        ld=json.loads(s.select_one('script[type="application/ld+json"]').string)
        self.assertEqual([x['@type'] for x in ld['@graph']],['WebPage','LodgingBusiness','Organization'])
        self.assertNotIn('numberOfRooms',str(ld));self.assertNotIn('priceRange',str(ld))
    def test_alias_cannot_leak_business_schema(self):
        s=self.soup();apply_seo(s,'/old/',R,'production-ready',{'/pl/':'/pl/'},{})
        self.assertFalse(s.select('script[type="application/ld+json"]'))
    def test_schema_escapes_markup_without_changing_text(self):
        s=self.soup();text='Page </script> & <known>'
        s.title.string=text
        apply_seo(s,'/pl/',R,'production-ready',{'/pl/':'/pl/'},{})
        raw=s.select_one('script[type="application/ld+json"]').string
        self.assertNotIn('<',raw)
        self.assertEqual(json.loads(raw)['@graph'][0]['name'],text)
    def test_preview_removes_old_sitemaps(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t);(out/'sitemap.xml').write_text('stale');(out/'sitemap-old.xml').write_text('stale')
            write_indexing_files(out,'preview',{'/pl/':'/pl/'})
            self.assertFalse(list(out.glob('*sitemap*.xml')));self.assertEqual((out/'robots.txt').read_text(),'User-agent: *\nDisallow: /\n')
    def test_production_sitemap_does_not_touch_preview(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);preview=root/'preview';prod=root/'prod';preview.mkdir();prod.mkdir()
            write_indexing_files(preview,'preview',{'/pl/':'/pl/'});before=(preview/'robots.txt').read_bytes()
            write_indexing_files(prod,'production-ready',{'/pl/':'/pl/'})
            self.assertEqual(before,(preview/'robots.txt').read_bytes());self.assertIn('https://hornigold.pl/pl/',(prod/'sitemap.xml').read_text())
    def test_production_rejects_preview_prefix_before_writing(self):
        before=(R/'_site/release.json').read_bytes();p=subprocess.run([sys.executable,str(R/'scripts/build.py'),'--mode','production-ready','--base','/hornigold-preview/'],capture_output=True)
        self.assertNotEqual(p.returncode,0);self.assertEqual(before,(R/'_site/release.json').read_bytes())
    def test_production_cannot_enable_counter(self):
        p=subprocess.run([sys.executable,str(R/'scripts/build.py'),'--mode','production-ready','--base','/','--counter'],capture_output=True)
        self.assertNotEqual(p.returncode,0)
    def test_deployment_stays_preview_only(self):
        workflow=(R/'.github/workflows/pages.yml').read_text();self.assertIn('path: _site',workflow);self.assertIn('--mode preview',workflow);self.assertNotIn('--mode production-ready',workflow);self.assertNotIn('_production_ready',workflow)
        self.assertFalse(json.loads((R/'release.json').read_text())['indexing'])
        self.assertIn('Disallow: /',(R/'site/robots.txt').read_text())
        self.assertIn('noindex',(R/'site/_headers').read_text())
        self.assertIn('local-only; Sites packaging refused',(R/'scripts/build_sites.mjs').read_text())

if __name__=='__main__':unittest.main(verbosity=2)
