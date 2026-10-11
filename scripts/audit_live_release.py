"""Read-only full canonical-route check after release; never submits forms."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import argparse,json,subprocess,datetime
root=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--origin',required=True);ap.add_argument('--base',default='');ap.add_argument('--label',required=True);opts=ap.parse_args()
assert opts.origin in ['https://hornigold-przeglad-beata.ai-bd6d706867.chatgpt.site','https://kamilkita-ux.github.io']
routes=json.loads((root/'routes.json').read_text())
def fetch(url):
 r=subprocess.run(['curl','-sS','-L','--max-time','25','--write-out','\n%{http_code}',url],capture_output=True,text=True)
 body,_,status=r.stdout.rpartition('\n');return body,status,r.returncode
def check(route):
 body,status,code=fetch(opts.origin+opts.base+route);errors=[]
 if status!='200' or code:errors.append('HTTP '+status)
 soup=BeautifulSoup(body,'html.parser');meta=soup.select_one('meta[name=robots]');canonical=soup.select_one('link[rel=canonical]')
 if not meta or meta.get('content')!='noindex,nofollow,noarchive':errors.append('preview indexing gate')
 if not canonical or canonical.get('href')!='https://hornigold.pl'+route:errors.append('canonical')
 if len(soup.select('link[hreflang]'))!=8:errors.append('hreflang count')
 if len(soup.select('h1'))!=1:errors.append('H1')
 for s in soup.select('script[type="application/ld+json"]'):
  try:json.loads(s.string)
  except Exception:errors.append('JSON-LD')
 return {'route':route,'status':status,'errors':errors}
with ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(check,routes))
robots,rs,_=fetch(opts.origin+opts.base+'/robots.txt');release,ls,_=fetch(opts.origin+opts.base+'/release.json');config,cs,_=fetch(opts.origin+opts.base+'/assets/analytics-config.js')
try:release=json.loads(release)
except Exception:release={}
checks={'robotsBlocked':rs=='200' and 'Disallow: /' in robots,'revision':release.get('revision'),'expectedRevision':release.get('revision')==json.loads((root/'release.json').read_text()).get('revision'),'analyticsDisabled':cs=='200' and 'enabled:false' in config}
report={'date':datetime.datetime.now().astimezone().isoformat(),'origin':opts.origin,'base':opts.base,'routes':len(rows),'checks':checks,'failures':[r for r in rows if r['errors']],'results':rows,'limits':['Read-only HTML verification, not a completed booking, receipt of analytics or legal certification.']}
p=root/'docs/implementation/evidence'/('public-'+opts.label+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['results','limits']},ensure_ascii=False));raise SystemExit(bool(report['failures']) or not all(checks[k] for k in ['robotsBlocked','expectedRevision','analyticsDisabled']))
