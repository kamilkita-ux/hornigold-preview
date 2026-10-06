"""Exhaustive offline artifact checks, not evidence of external indexing or ranking."""
from pathlib import Path
from urllib.parse import urlsplit, unquote, urljoin
from urllib.robotparser import RobotFileParser
from collections import defaultdict, deque
import argparse, json, hashlib, re, datetime, unicodedata
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from seo import ORIGIN, LANGS, PREVIEW_ROBOTS, load_routes, route_for_file

ROOT=Path(__file__).resolve().parent.parent

def audit(mode, directory):
    routes=load_routes(ROOT);out=directory.resolve();release=json.loads((out/'release.json').read_text());base=release['base']
    errors=[];warnings=[];inventory=[];links=0;images=0;external=set();titles=defaultdict(list);descriptions=defaultdict(list);bodies=defaultdict(list);graph=defaultdict(set)
    def check(ok,rule,route=''):
        if not ok:errors.append({'route':route,'rule':rule})
    docs={p:BeautifulSoup(p.read_text(),'html.parser') for p in out.rglob('*.html')}
    by_route={route_for_file(p,out):s for p,s in docs.items()}
    robots=(out/'robots.txt').read_text();rp=RobotFileParser();rp.parse(robots.splitlines())
    check(release.get('buildMode')==mode,'build mode')
    check(not release.get('published',True),'local artifact marked unpublished')
    check(not release['bookingEnabled'] and not release['paymentsEnabled'],'sales remain disabled')
    if mode=='preview':
        check(robots=='User-agent: *\nDisallow: /\n','preview robots')
        check(not list(out.glob('*sitemap*.xml')),'no preview sitemap')
        check('X-Robots-Tag: noindex' in (out/'_headers').read_text(),'preview HTTP header template')
    else:
        check(base=='/','production root')
        check('Sitemap: '+ORIGIN+'/sitemap.xml' in robots,'production sitemap declaration')
        locs=[e.text for e in ET.parse(out/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        check(len(locs)==len(set(locs))==len(routes),'sitemap uniqueness and count')
        check(set(locs)=={ORIGIN+r for r in routes.values()},'sitemap canonical coverage')
        header=(out/'_headers').read_text().split('/404.html')[0]
        check('noindex' not in header,'no blanket production noindex header')
    def local_target(value,current,css=False):
        u=urlsplit(value)
        if u.scheme in ('mailto','tel','data','javascript'):return None
        if u.netloc and u.netloc!=urlsplit(ORIGIN).netloc:
            external.add(value);return None
        if not u.path:return current
        if u.netloc:rel=unquote(u.path.lstrip('/'))
        elif u.path.startswith(base):rel=unquote(u.path[len(base):])
        elif not u.path.startswith('/'):
            return (current.parent/unquote(u.path)).resolve()
        else:
            check(False,'link outside base: '+value,str(current.relative_to(out)));return None
        target=out/rel
        if target.is_dir():target=target/'index.html'
        return target
    for p,s in docs.items():
        path=route_for_file(p,out);route=routes.get(unquote(path));real=bool(route)
        rob=s.select('meta[name=robots]');check(len(rob)==1,'one robots meta',path)
        value=rob[0].get('content','') if rob else ''
        check(value==('index,follow' if mode=='production-ready' and real else PREVIEW_ROBOTS),'robots meta state',path)
        if not real:check(not s.select('script[type="application/ld+json"]'),'no legacy schema on aliases/errors',path)
        if real:
            h1=s.select('h1');title=s.title.get_text(strip=True) if s.title else '';desc=s.select('meta[name=description]');description=desc[0].get('content','') if desc else ''
            check(len(h1)==1 and bool(h1[0].get_text(strip=True)),'one nonempty H1',route)
            check(bool(title) and len(s.select('title'))==1,'one nonempty title',route)
            check(len(desc)==1 and bool(description),'one nonempty description',route)
            titles[unicodedata.normalize('NFKC',title).casefold()].append(route);descriptions[unicodedata.normalize('NFKC',description).casefold()].append(route)
            bodies[hashlib.sha256(s.main.get_text(' ',strip=True).encode()).hexdigest()].append(route)
            can=s.select('link[rel=canonical]');check(len(can)==1 and can[0].get('href')==ORIGIN+route,'canonical exact',route)
            lang=s.html.get('lang');check(lang in LANGS,'language',route)
            alts=s.select('link[rel=alternate][hreflang]');matrix={a['hreflang']:a.get('href') for a in alts}
            check(len(alts)==8 and set(matrix)==LANGS|{'x-default'},'complete hreflang',route)
            check(matrix.get('x-default')==matrix.get('pl'),'x-default Polish equivalent',route)
            check(matrix.get(lang)==ORIGIN+route,'hreflang self',route)
            for language,url in matrix.items():
                u=urlsplit(url);peer=by_route.get(unquote(u.path))
                check(u.scheme+'://'+u.netloc==ORIGIN and not u.query and not u.fragment,'alternate origin',route)
                check(unquote(u.path) in routes and peer is not None,'alternate canonical route exists',route)
                if peer:
                    back={a['hreflang']:a.get('href') for a in peer.select('link[rel=alternate][hreflang]')}
                    check(back==matrix,'reciprocal hreflang cluster',route)
                    if language!='x-default':check(peer.html.get('lang')==language,'alternate language',route)
                if mode=='production-ready':check(rp.can_fetch('*',url),'alternate not robots blocked',route)
            if mode=='production-ready':check(rp.can_fetch('*',ORIGIN+route),'canonical not robots blocked',route)
            expected={'og:title':title,'og:description':description,'og:url':ORIGIN+route,'og:type':'website','twitter:card':'summary_large_image','twitter:title':title,'twitter:description':description,'og:image:alt':title,'twitter:image:alt':title}
            for key,val in expected.items():
                tag=s.find_all('meta',attrs={'property' if key.startswith('og:') else 'name':key});check(len(tag)==1 and tag[0].get('content')==val,'social metadata '+key,route)
            for key in ['og:image','twitter:image']:
                tag=s.find('meta',attrs={'property' if key.startswith('og:') else 'name':key});target=local_target(tag['content'],p) if tag else None
                check(target is not None and target.exists(),'social image '+key,route)
            ld=s.select('script[type="application/ld+json"]');check(len(ld)==1,'one JSON-LD graph',route)
            try:
                data=json.loads(ld[0].string);nodes=data['@graph'];check(data['@context']=='https://schema.org' and len(nodes)==1,'minimal evidence-scoped schema',route)
                n=nodes[0];check(set(n)=={'@type','@id','url','name','description','inLanguage'},'schema allowed fields only',route)
                check(n=={'@type':'WebPage','@id':ORIGIN+route+'#page','url':ORIGIN+route,'name':title,'description':description,'inLanguage':lang},'schema equals visible metadata',route)
            except (ValueError,KeyError,IndexError,TypeError):check(False,'valid JSON-LD',route)
            inventory.append({'route':route,'lang':lang,'title':title,'description':description,'canonical':ORIGIN+route,'robots':value,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        for img in s.select('img'):
            images+=1;check(img.has_attr('alt'),'image alt attribute',path)
            if not img.get('alt','').strip():check(img.get('role')=='presentation' or img.get('aria-hidden')=='true','empty alt requires decorative marking',path)
        for e in s.select('[src],[href],[action],[poster],[srcset]'):
            values=[e[a] for a in ('href','src','action','poster') if e.has_attr(a)]
            if e.has_attr('srcset'):values += [x.strip().split()[0] for x in e['srcset'].split(',') if x.strip()]
            for v in values:
                links+=1;u=urlsplit(v)
                if e.name in ('script','img','iframe','link'):check(u.scheme!='http' and not v.startswith('//'),'mixed or protocol-relative resource',path)
                target=local_target(v,p)
                if target is None:continue
                check(target.exists(),'local target exists: '+v,path)
                if u.fragment and target in docs:check(docs[target].find(id=unquote(u.fragment)) is not None,'local fragment exists: '+v,path)
                if real and e.name=='a' and target in docs:
                    other=routes.get(route_for_file(target,out))
                    if other:graph[route].add(other)
    for label,values in [('title',titles),('description',descriptions),('main content',bodies)]:
        for same in values.values():
            if len(same)>1:errors.append({'rule':'duplicate '+label,'routes':same})
    reached=set();queue=deque(r for r in routes.values() if r.count('/')==2)
    while queue:
        route=queue.popleft()
        if route in reached:continue
        reached.add(route);queue.extend(graph[route]-reached)
    orphans=sorted(set(routes.values())-reached)
    for route in orphans:check(False,'unreachable from language homepages',route)
    # Alias-chain detection is a separate draft; no server configuration is changed.
    alias={}
    for p,s in docs.items():
        a=s.select_one('a[data-redirect]')
        if a:
            target=local_target(a['href'],p)
            if target:alias[route_for_file(p,out)]=route_for_file(target,out)
    for src in alias:
        seen=set();dest=src
        while dest in alias and dest not in seen:seen.add(dest);dest=alias[dest]
        check(dest not in seen,'redirect loop',src)
        check(dest in routes,'redirect reaches canonical route',src)
    for p in out.rglob('*.css'):
        for v in re.findall(r'url\([\s\"\']*([^\)\"\']+)',p.read_text()):
            target=local_target(v.strip(),p,True)
            if target is not None:check(target.exists(),'CSS resource exists: '+v,str(p.relative_to(out)))
    check(len(inventory)==len(routes),'canonical route completeness')
    return {'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':mode,'base':base,'routes':len(inventory),'html':len(docs),'links':links,'images':images,'reachableRoutes':len(reached),'redirectAliases':len(alias),'errors':errors,'warnings':warnings,'inventory':inventory,'externalUrlsNotRequested':sorted(external),'limits':['Offline audit only; no external link, indexing, DNS or ranking validation','No legal, translation or full WCAG certification']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',required=True,choices=['preview','production-ready']);p.add_argument('--output');a=p.parse_args()
    out=ROOT/('_site' if a.mode=='preview' else '_production_ready')
    report=audit(a.mode,out);destination=Path(a.output or str(ROOT/'docs/seo'/('audit-'+a.mode+'.json')));destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('inventory','externalUrlsNotRequested')},ensure_ascii=False)[:8000]);raise SystemExit(bool(report['errors']))
