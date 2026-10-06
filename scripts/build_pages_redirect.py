"""Prepare (do not publish) the GitHub Pages handover to the single live Sites origin."""
from pathlib import Path
from urllib.parse import quote
from html import escape
import json,shutil
R=Path(__file__).resolve().parent.parent;origin=json.loads((R/'release.json').read_text())['primaryOrigin'];out=R/'_pages'
if out.exists():shutil.rmtree(out)
out.mkdir();base='/hornigold-preview/'
script="""(() => {const a=document.querySelector('[data-destination]');if(!a)return;const u=new URL(a.href);const source=new URL(location.href);for(const key of ['arrival','departure','guests','room']){const v=source.searchParams.get(key);if(v&&v.length<=512)u.searchParams.set(key,v)}u.hash=source.hash;location.replace(u.href)})();"""
(out/'handover.js').write_text(script)
for p in (R/'site').rglob('*.html'):
 rel=p.relative_to(R/'site');route='/'+str(rel).removesuffix('index.html');target=origin+quote(route,safe='/%')
 d=out/rel;d.parent.mkdir(parents=True,exist_ok=True)
 d.write_text('<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><title>Hornigold</title><script defer src="'+base+'handover.js"></script></head><body><main><h1>Hornigold</h1><p><a data-destination href="'+escape(target,quote=True)+'">Otwórz stronę / Open website</a></p></main></body></html>')
(out/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print(json.dumps({'html':len(list(out.rglob('*.html'))),'target':origin,'status':'prepared only'}))
