"""Read-only checks. No forms, tracking consent, mail or transactions are submitted."""
import argparse,json,subprocess,datetime,xml.etree.ElementTree as ET
from pathlib import Path
P=argparse.ArgumentParser();P.add_argument('--output',default='docs/implementation/evidence/monitor-latest.json');P.add_argument('--self-test',action='store_true');args=P.parse_args()
def request(url):
 p=subprocess.run(['curl','-sS','--max-time','25','-D','-','-w','\n%{http_code}',url],capture_output=True,text=True)
 head,_,rest=p.stdout.partition('\r\n\r\n')
 if not rest:head,_,rest=p.stdout.partition('\n\n')
 body,_,status=rest.rpartition('\n');return status,head.lower(),body
checks=[]
def check(name,ok,detail):checks.append({'name':name,'ok':bool(ok),'detail':detail})
if args.self_test:
 check('controlled_failure',False,'TEST ONLY: simulated unavailable endpoint; no production configuration changed')
else:
 for route in ['/pl/','/en/','/pl/pokoje/','/pl/lokalizacja/','/pl/rezerwacja/']:
  status,h,b=request('https://hornigold.pl'+route);check(route,status=='200' and 'x-robots-tag: noindex' not in h,{'http':status,'tls':True,'hsts':'strict-transport-security:' in h})
 status,h,b=request('https://hornigold.pl/robots.txt');check('robots',status=='200' and 'Allow: /' in b and '\nDisallow: /\n' not in b,status)
 status,h,b=request('https://hornigold.pl/sitemap.xml')
 try:urls=[e.text for e in ET.fromstring(b).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];valid=len(urls)==693 and len(set(urls))==693 and all(u.startswith('https://hornigold.pl/') for u in urls)
 except Exception:urls=[];valid=False
 check('sitemap',status=='200' and valid,{'http':status,'count':len(urls)})
 status,h,b=request('https://www.hornigold.pl/pl/');check('www301',status=='301' and 'location: https://hornigold.pl/pl/' in h,status)
 status,h,b=request('https://hornigold.pl/__monitor_missing_20261011__/');check('404',status=='404' and 'noindex' in h,status)
 status,h,b=request('https://hornigold.pl/release.json')
 try:release=json.loads(b)
 except Exception:release={}
 check('release',status=='200' and bool(release.get('revision')),release)
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'controlled-test' if args.self_test else 'production-read-only','ok':all(x['ok'] for x in checks),'checks':checks,'limits':['No mail delivery, booking, payment, GA4 receipt or Google indexing is inferred from HTTP health.','No Google account API credentials are configured.']}
out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'ok':report['ok'],'checks':len(checks),'report':str(out)}));raise SystemExit(0 if report['ok'] else 1)
