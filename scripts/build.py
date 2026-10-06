"""Build isolated preview or local-only production-ready static artifacts."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
import argparse,shutil,json,re,hashlib
from bs4 import BeautifulSoup
from seo import load_routes, route_for_file, apply_seo, write_indexing_files
ROOT=Path(__file__).resolve().parent.parent
RELEASE=json.loads((ROOT/'release.json').read_text())
VERSION=str(RELEASE['version'])
args=argparse.ArgumentParser();args.add_argument('--base',default='/hornigold-preview/');args.add_argument('--counter',action='store_true');args.add_argument('--mode',choices=['preview','production-ready'],default='preview');opts=args.parse_args()
BASE='/'+opts.base.strip('/')+'/' if opts.base.strip('/') else '/'
if not re.fullmatch(r'/[A-Za-z0-9_/-]*',BASE):raise SystemExit('Invalid base path')
if opts.mode=='production-ready' and (BASE!='/' or opts.counter):raise SystemExit('production-ready requires --base / and does not enable server integrations')
OUT=ROOT/('_site' if opts.mode=='preview' else '_production_ready')
ROUTES=load_routes(ROOT)
OVERRIDES=json.loads((ROOT/'seo/metadata-overrides.json').read_text())
if OUT.exists():shutil.rmtree(OUT)
shutil.copytree(ROOT/'site',OUT)
def prefixed(url):return BASE+url.lstrip('/') if url.startswith('/') and not url.startswith('//') else url
# These two scripts use root-relative generated destinations. All other UI follows DOM URLs.
p=OUT/'assets/root-language.js';s=p.read_text().replace("location.replace('/'+language+",'location.replace('+json.dumps(BASE)+'+language+');p.write_text(s)
p=OUT/'assets/error-language.js';s=p.read_text().replace('location.pathname.replace(', 'location.pathname.slice('+str(len(BASE)-1)+').replace(').replace("a.href='/'+a.dataset.language",'a.href='+json.dumps(BASE)+'+a.dataset.language');p.write_text(s)
for p in OUT.rglob('*.html'):
 s=BeautifulSoup(p.read_text(),'html.parser')
 apply_seo(s,route_for_file(p,OUT),ROOT,opts.mode,ROUTES,OVERRIDES)
 if opts.counter and s.select_one('[data-site-version]'):
  meta=s.new_tag('meta');meta['name']='hornigold-counter-endpoint';meta['content']=BASE+'api/site-stats';s.head.append(meta)
 for el in s.select('[href],[src],[action],[poster]'):
  for attr in ['href','src','action','poster']:
   if attr in el.attrs:el[attr]=prefixed(el[attr])
 for el in s.select('[srcset]'):
  el['srcset']=', '.join(' '.join([prefixed(part.strip().split()[0])]+part.strip().split()[1:]) for part in el['srcset'].split(','))
 for meta in s.select('meta[http-equiv=refresh]'):
  meta['content']=re.sub(r'(url=)(/[^;]+)',lambda m:m[1]+prefixed(m[2]),meta['content'])
 for asset in s.select('script[src],link[rel=stylesheet]'):
  attr='src' if asset.name=='script' else 'href';u=urlsplit(asset[attr])
  if u.path.startswith(BASE+'assets/'):
   local=OUT/unquote(u.path[len(BASE):])
   if local.is_file():asset[attr]=u.path+'?v='+VERSION+'-'+hashlib.sha256(local.read_bytes()).hexdigest()[:10]
 # Preview indexing exclusion must survive any static host configuration.
 if not s.select_one('meta[name=robots]'):
  meta=s.new_tag('meta');meta['name']='robots';meta['content']='noindex,nofollow,noarchive';s.head.append(meta)
 p.write_text(str(s))
write_indexing_files(OUT,opts.mode,ROUTES)
p=OUT/'site.webmanifest';d=json.loads(p.read_text());d['start_url']=prefixed(d['start_url']);d['scope']=BASE;p.write_text(json.dumps(d,ensure_ascii=False))
# Validate every local document/asset link, and require the preview markers on real pages.
errors=[];pages=0
for p in OUT.rglob('*.html'):
 s=BeautifulSoup(p.read_text(),'html.parser')
 if s.select_one('[data-site-version]'):
  pages+=1
  if s.select_one('[data-site-version]').get_text()!=VERSION:errors.append(str(p)+' wrong version')
  expected='noindex' if opts.mode=='preview' else 'index'
  if expected not in s.select_one('meta[name=robots]')['content'].split(','):errors.append(str(p)+' indexing')
  if s.select_one('.preview-bar'):errors.append(str(p)+' unexpected preview banner')
 for el in s.select('a[href],img[src],script[src],link[rel=stylesheet],form[action]'):
  raw=el.get('href') or el.get('src') or el.get('action');u=urlsplit(raw)
  if u.scheme or u.netloc or not u.path:continue
  if not u.path.startswith(BASE):errors.append(str(p)+' outside base '+raw);continue
  target=OUT/unquote(u.path[len(BASE):]);target=target/'index.html' if target.is_dir() else target
  if not target.exists():errors.append(str(p)+' missing '+raw)
if pages!=693:errors.append('Expected 693 pages, found '+str(pages))
if errors:raise SystemExit('\n'.join(errors[:30]))
import os
(OUT/'release.json').write_text(json.dumps({**RELEASE,'base':BASE,'buildMode':opts.mode,'indexing':opts.mode=='production-ready','published':False,'counterEnabled':opts.counter,'commit':os.environ.get('GITHUB_SHA','local')},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pages':pages,'base':BASE,'errors':0,'mode':opts.mode,'output':str(OUT)}))
