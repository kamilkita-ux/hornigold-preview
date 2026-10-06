"""Read-only byte verification of every published file against a built local manifest."""
import argparse,json,urllib.request,urllib.parse,hashlib,concurrent.futures,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--url',required=True);p.add_argument('--output',required=True);a=p.parse_args();m=json.load(open(a.manifest))
def get(item):
 url=a.url.rstrip('/')+'/'+urllib.parse.quote(item['path'],safe='/')
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HornigoldReadOnlyQA/1.0'}),timeout=30) as r:
    body=r.read();code=r.status
   if item['path']=='release.json':ok=json.loads(body)['version']==m['version']
   else:ok=hashlib.sha256(body).hexdigest()==item['sha256']
   return {'path':item['path'],'status':code,'match':ok}
  except Exception as e:
   if attempt==2:return {'path':item['path'],'error':str(e),'match':False}
   time.sleep(1)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(get,[f for f in m['files'] if f['path']!='.nojekyll']))
release=json.load(urllib.request.urlopen(a.url.rstrip('/')+'/release.json'))
report={'version':m['version'],'release':release,'checkedFiles':len(results),'failures':[x for x in results if not x['match']],'results':results,'completedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False));raise SystemExit(bool(report['failures']))
