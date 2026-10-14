"""Publication identity checks use mocked transport, never public requests."""
import contextlib, io, json, pathlib, runpy, shutil, sys, tempfile, types, unittest
from unittest.mock import patch

SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'scripts/audit_live_release.py'
class ReleaseIdentity(unittest.TestCase):
 def audit(self, start=None, end=None, expected='a'*40, transport=0, article=False, article_languages=None):
  initial={'revision':'23.17','commit':'a'*40} if start is None else start
  final=initial if end is None else end
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);(root/'scripts').mkdir();(root/'docs/implementation/evidence').mkdir(parents=True)
   script=root/'scripts/audit_live_release.py';shutil.copy2(SCRIPT,script)
   article_route='/pl/artykuly/opinie-jakosc/'
   routes=['/pl/','/en/']+([article_route] if article else [])
   (root/'routes.json').write_text(json.dumps(routes))
   if article:
    (root/'content').mkdir()
    (root/'content/editorial-articles.json').write_text(json.dumps({'singleLocaleRoutes':[article_route],'articles':[{'route':article_route,'language':'pl'}]}))
   (root/'release.json').write_text(json.dumps({'revision':'23.17'}))
   calls=[]
   def fetch(args,**kwargs):
    url=args[-1];code=0
    if url.endswith('/release.json'):
     calls.append(url);body=json.dumps(initial if len(calls)==1 else final);code=transport if len(calls)==1 else 0
    elif url.endswith('/robots.txt'):body='User-agent: *\nDisallow: /'
    elif url.endswith('/assets/analytics-config.js'):body='enabled:false'
    else:
     route=article_route if url.endswith(article_route) else ('/en/' if url.endswith('/en/') else '/pl/')
     languages=['pl','en','de','zh-Hans','uk','es','it','x-default']
     if route==article_route:languages=['pl','x-default'] if article_languages is None else article_languages
     body='<html><head><meta name="robots" content="noindex,nofollow,noarchive"><link rel="canonical" href="https://hornigold.pl'+route+'">'+''.join('<link hreflang="'+language+'">' for language in languages)+'</head><body><h1>Stay</h1></body></html>'
    return types.SimpleNamespace(stdout=body+'\n200',stderr='',returncode=code)
   argv=[str(script),'--origin','https://kamilkita-ux.github.io','--label','test','--expected-commit',expected]
   with patch('sys.path',[str(SCRIPT.parent),*sys.path]),patch('sys.argv',argv),patch('subprocess.run',side_effect=fetch),contextlib.redirect_stdout(io.StringIO()):
    with self.assertRaises(SystemExit) as result:runpy.run_path(str(script),run_name='__main__')
   report=json.loads((root/'docs/implementation/evidence/public-test.json').read_text())
   return bool(result.exception.code),report['checks']
 def test_same_revision_correct_commit_passes(self):self.assertFalse(self.audit()[0])
 def test_registered_polish_article_passes(self):self.assertFalse(self.audit(article=True)[0])
 def test_fictional_article_language_cluster_fails(self):self.assertTrue(self.audit(article=True,article_languages=['en','x-default'])[0])
 def test_same_revision_wrong_commit_fails(self):
  failed,checks=self.audit(expected='b'*40);self.assertTrue(failed);self.assertFalse(checks['expectedCommit'])
 def test_changed_deployment_fails(self):
  failed,checks=self.audit(end={'revision':'23.17','commit':'b'*40});self.assertTrue(failed);self.assertFalse(checks['deploymentStable'])
 def test_changed_revision_fails(self):self.assertTrue(self.audit(end={'revision':'23.18','commit':'a'*40})[0])
 def test_missing_commit_fails(self):self.assertTrue(self.audit(start={'revision':'23.17'})[0])
 def test_transport_failure_fails_even_with_http_200(self):
  failed,checks=self.audit(transport=60);self.assertTrue(failed);self.assertFalse(checks['releaseFetched'])
if __name__=='__main__':unittest.main()
