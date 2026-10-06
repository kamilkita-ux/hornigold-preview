"""Derive a review-only 301 map from local evidence. Does not deploy redirects."""
from pathlib import Path
from urllib.parse import unquote, urlsplit, quote
from bs4 import BeautifulSoup
import json,csv
from seo import load_routes,ORIGIN
R=Path(__file__).resolve().parent.parent
routes=load_routes(R)
s=(R/'server/routes.mjs').read_text();server=json.loads(s.split('export const redirects=',1)[1].strip().removesuffix(';'))
mapping={unquote(k):unquote(v) for k,v in server.items()};evidence={unquote(k):'server/routes.mjs' for k in server}
for p in (R/'site').rglob('index.html'):
    text=p.read_text()
    if 'data-redirect' not in text:continue
    a=BeautifulSoup(text,'html.parser').select_one('a[data-redirect]')
    if not a:continue
    src='/'+str(p.relative_to(R/'site'))[:-10];dst=unquote(urlsplit(a['href']).path)
    if src in mapping and mapping[src]!=dst:raise SystemExit('Conflicting redirect: '+src)
    mapping[src]=dst;evidence[src]=str(p.relative_to(R))
rows=[]
for src in sorted(mapping):
    seen=set();dst=src
    while dst in mapping:
        if dst in seen:raise SystemExit('Redirect loop: '+src)
        seen.add(dst);dst=mapping[dst]
    if dst not in routes:raise SystemExit('Missing destination: '+dst)
    if src in routes:raise SystemExit('Canonical URL would redirect: '+src)
    for old in sorted({src,src.rstrip('/') or '/'}):
        rows.append([ORIGIN+quote(old,safe='/%'),ORIGIN+routes[dst],'301','Alias obecny w '+evidence[src]+'; cel spłaszczony do adresu kanonicznego','SZKIC — potwierdzić użycie na starej stronie i zatwierdzić przed wdrożeniem'])
with (R/'REDIRECT_MAP_DRAFT.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f,lineterminator="\n");w.writerow(['stary URL','nowy URL','typ przekierowania','uzasadnienie','status']);w.writerows(rows)
report={'aliases':len(mapping),'rows':len(rows),'loops':0,'missingTargets':0,'selfRedirects':0,'externalOldSiteVerified':False,'sourceFiles':['server/routes.mjs','site/**/index.html'],'deployed':False}
(R/'docs/seo/redirect-map.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
