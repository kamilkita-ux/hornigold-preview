"""Compare preserved v18 manifest with current guest assets, routes and translations."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
from urllib.parse import unquote,urlsplit
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parent.parent
old=json.loads((R/'docs/V18-ASSET-MANIFEST.json').read_text());errors=[];images=[];html=[];changed=[]
for f in old['files']:
 p=R/'site'/f['path']
 if f['path'].endswith('.html'):
  html.append(f['path'])
  if not p.exists():errors.append('Missing v18 HTML '+f['path'])
 if p.suffix.lower() in ('.jpg','.jpeg','.webp','.png','.svg','.gif','.avif'):
  images.append(f['path'])
  if not p.exists():errors.append('Missing image '+f['path'])
  elif hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:changed.append(f['path'])
if sorted(changed)!=['assets/favicon.png','assets/og/hornigold.jpg']:errors.append('Unreviewed changed image set')
routes=json.loads((R/'routes.json').read_text());pages=0
for route in routes:
 s=BeautifulSoup((R/'site'/unquote(route.strip('/'))/'index.html').read_text(),'html.parser');pages+=1
 for selector in ('[data-view-count]','[data-view-unavailable]','[data-site-version]','#privacy-dialog','script[src*="site-stats.js"]'):
  if not s.select_one(selector):errors.append(route+' missing '+selector)
 if s.select_one('[data-site-version]').text!='23':errors.append(route+' wrong version')
 if s.select_one('main') and __import__('re').search(r'\bhotel\b',s.main.get_text(' ',strip=True),__import__('re').I):errors.append(route+' hotel terminology')
 locs=ET.parse(R/'site/sitemap.xml').getroot().findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc') if pages==1 else locs
if {urlsplit(e.text).path for e in locs}!=set(routes):errors.append('Sitemap differs from route catalog')
for lang in ['pl','en','de','zh-hans','uk','es','it']:
 d=json.loads((R/'legal'/f'{lang}.json').read_text());sections={s['id']:s for s in d['sections']}
 if len(sections)!=6 or len(sections['cookies']['paragraphs'])!=5:errors.append(lang+' legal sections')
 if 'cloudflare.com/privacypolicy/' not in ' '.join(sections['privacy']['paragraphs']):errors.append(lang+' hosting disclosure')
report={'version':23,'revision':'23.1','sourceCommit':old['sourceCommit'],'oldHTMLPreserved':len(html),'oldImagePathsPreserved':len(images),'intentionallyReplacedImages':changed,'currentRoutes':pages,'languages':7,'errors':errors,'decisions':{'club':'Full four-part section restored at owner request, reception confirms benefits; original internal wording archived','root':'Saved explicit language wins; no forced Polish server redirect','terminology':'Current Hornigold wording retained','comparison':'Current table keeps previous room values','legal':'v23 policies retained and updated for Sites/counting','bookingAndPayments':'Remain disabled','counter':'Existing Sites D1 table retained, aggregate page views only','githubPush':'Deferred by user'}}
(R/'docs/CONSOLIDATION-23.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(errors))
