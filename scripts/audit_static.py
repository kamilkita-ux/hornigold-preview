"""Offline structural audit; no claim of editorial or WCAG certification."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
import json, re, argparse, hashlib, datetime
p=argparse.ArgumentParser();p.add_argument('--base',default='/');p.add_argument('--output',default='/tmp/hornigold-static-audit.json');args=p.parse_args()
root=Path(__file__).resolve().parent.parent;out=root/'_site';base=args.base
routes=json.loads((root/'routes.json').read_text());release=json.loads((root/'release.json').read_text())
docs={f:BeautifulSoup(f.read_text(),'html.parser') for f in out.rglob('*.html')};errors=[];warnings=[];links=0
langs={'pl','en','de','zh-Hans','uk','es','it'}
for route in routes:
 f=out/unquote(route.strip('/'))/'index.html';s=docs[f]
 def check(ok,kind):
  if not ok:errors.append({'route':route,'error':kind})
 check(s.html.get('lang') in langs,'lang')
 check(s.title and s.title.get_text(strip=True),'title')
 check(s.select_one('meta[name=description][content]'),'description')
 check('noindex' in s.select_one('meta[name=robots]')['content'],'noindex')
 check(not s.select('.preview-bar'),'removed banner')
 check(s.select_one('[data-site-version]').get_text()==str(release['version']),'version')
 alts={a['hreflang']:a['href'] for a in s.select('link[rel=alternate][hreflang]')}
 check(set(alts)==langs|{'x-default'},'hreflang matrix')
 check(len(s.select('a[data-language]'))==7,'language switcher')
 canonical=s.select_one('link[rel=canonical]')
 check(canonical and canonical['href']=='https://hornigold.pl'+route,'canonical')
 for lang,url in alts.items():
  u=urlsplit(url);peer=out/unquote(u.path.strip('/'))/'index.html'
  check(peer in docs,'alternate route')
  if peer in docs:
   back={a['href'] for a in docs[peer].select('link[rel=alternate][hreflang]')};check('https://hornigold.pl'+route in back,'reciprocal hreflang')
 check(len(s.select('h1'))==1,'one h1')
 for img in s.select('img'):check(img.has_attr('alt'),'image alt')
 for form in s.select('form'):
  check(form.get('method','get').lower()=='get','unexpected POST form')
 if s.select('form[data-search]'):check(s.select_one('.form-help'),'booking disclosure')
for f,s in docs.items():
 for e in s.select('[src],[href],[action],[poster],[srcset]'):
  values=[e[a] for a in ('src','href','action','poster') if e.has_attr(a)]
  if e.has_attr('srcset'):values += [part.strip().split()[0] for part in e['srcset'].split(',') if part.strip()]
  for value in values:
   u=urlsplit(value);links+=1
   if e.name in ('script','img','iframe','link') and u.scheme=='http':errors.append({'file':str(f.relative_to(out)),'error':'mixed content'})
   if u.scheme or u.netloc:continue
   if not u.path:target=f
   elif u.path.startswith(base):target=out/unquote(u.path[len(base):]);target=target/'index.html' if target.is_dir() else target
   else:errors.append({'file':str(f.relative_to(out)),'error':'outside base','url':value});continue
   if not target.exists():errors.append({'file':str(f.relative_to(out)),'error':'missing target','url':value})
   if u.fragment and target in docs and not docs[target].find(id=unquote(u.fragment)):
    # Language switching retains the current anchor; missing anchors are separately reviewed.
    warnings.append({'file':str(f.relative_to(out)),'error':'missing anchor','url':value})
assert 'Disallow: /' in (out/'robots.txt').read_text()
report={'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':release['version'],'base':base,'pages':len(routes),'html':len(docs),'links':links,'errors':errors,'warnings':warnings,'files':[{'path':str(f.relative_to(out)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in out.rglob('*') if f.is_file()]}
Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False)[:4000]);raise SystemExit(bool(errors))
