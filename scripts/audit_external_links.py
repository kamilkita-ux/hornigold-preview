"""Read-only public link check. No forms, bookings, payments or authenticated APIs."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,urlunsplit
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,datetime
root=Path(__file__).resolve().parent.parent
urls=set()
for f in (root/'site').rglob('*.html'):
 for a in BeautifulSoup(f.read_text(),'html.parser').select('main a[href^="https://"]'):
  u=urlsplit(a['href'])
  if u.hostname not in ['hornigold.pl','www.hornigold.pl'] and not any(k in u.query.lower() for k in ['email=','token=','key=']):urls.add(urlunsplit((u.scheme,u.netloc,u.path,u.query,'')))
def check(u):
 r=subprocess.run(['curl','--head','--location','--max-time','15','--silent','--output','/dev/null','--write-out','%{http_code}',u],capture_output=True,text=True)
 code=r.stdout.strip();return {'url':u,'status':code,'exit':r.returncode,'result':'ok' if code.startswith(('2','3')) else 'manual_review' if code in ['403','429','405'] or r.returncode else 'possible_broken'}
with ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(check,sorted(urls)))
report={'date':datetime.datetime.now().astimezone().isoformat(),'method':'Public HEAD; refusal/rate limits are not proof of a broken page','results':results}
(root/'docs/implementation/evidence/external-links.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checked':len(results),'ok':sum(r['result']=='ok' for r in results),'manualReview':sum(r['result']=='manual_review' for r in results),'possibleBroken':[r for r in results if r['result']=='possible_broken']}))
