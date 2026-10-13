"""Read-only full canonical-route check after release; never submits forms."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from bs4 import BeautifulSoup
import argparse,json,subprocess,datetime
root=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser();ap.add_argument('--origin',required=True);ap.add_argument('--base',default='');ap.add_argument('--label',required=True);ap.add_argument('--expected-commit');opts=ap.parse_args()
assert opts.origin in ['https://hornigold-przeglad-beata.ai-bd6d706867.chatgpt.site','https://kamilkita-ux.github.io']
routes=json.loads((root/'routes.json').read_text())
fetch_diagnostics=[];fetch_diagnostics_lock=Lock()
def fetch(url):
 r=subprocess.run(['curl','-sS','-L','--fail','--max-time','25','--retry','2','--retry-delay','1','--retry-max-time','55','--write-out','\n%{http_code}',url],capture_output=True,text=True)
 body,_,status=r.stdout.rpartition('\n')
 if r.stderr.strip():
  with fetch_diagnostics_lock:fetch_diagnostics.append({'url':url,'finalStatus':status,'returnCode':r.returncode,'stderr':r.stderr.strip()[:2000]})
 return body,status,r.returncode
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
start_body,start_status,start_code=fetch(opts.origin+opts.base+'/release.json')
try:start_release=json.loads(start_body)
except Exception:start_release={}
with ThreadPoolExecutor(max_workers=8) as pool:rows=list(pool.map(check,routes))
robots,rs,rc=fetch(opts.origin+opts.base+'/robots.txt');release,ls,lc=fetch(opts.origin+opts.base+'/release.json');config,cs,cc=fetch(opts.origin+opts.base+'/assets/analytics-config.js')
try:release=json.loads(release)
except Exception:release={}
checks={'releaseFetched':start_status=='200' and start_code==0 and ls=='200' and lc==0,'deploymentStable':bool(start_release.get('commit')) and start_release.get('commit')==release.get('commit') and start_release.get('revision')==release.get('revision'),'commit':release.get('commit'),'expectedCommit':not opts.expected_commit or release.get('commit')==opts.expected_commit,'robotsBlocked':rc==0 and rs=='200' and 'Disallow: /' in robots,'revision':release.get('revision'),'expectedRevision':release.get('revision')==json.loads((root/'release.json').read_text()).get('revision'),'analyticsDisabled':cc==0 and cs=='200' and 'enabled:false' in config}
report={'date':datetime.datetime.now().astimezone().isoformat(),'origin':opts.origin,'base':opts.base,'routes':len(rows),'checks':checks,'failures':[r for r in rows if r['errors']],'fetchDiagnostics':fetch_diagnostics,'results':rows,'limits':['Read-only HTML verification, not a completed booking, receipt of analytics or legal certification.']}
p=root/'docs/implementation/evidence'/('public-'+opts.label+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['results','limits']},ensure_ascii=False));raise SystemExit(bool(report['failures']) or not all(checks[k] for k in ['releaseFetched','deploymentStable','expectedCommit','robotsBlocked','expectedRevision','analyticsDisabled']))
