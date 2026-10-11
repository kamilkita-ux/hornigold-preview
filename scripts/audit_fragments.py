from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from bs4 import BeautifulSoup
import json
R=Path(__file__).resolve().parent.parent;O=R/'_production_ready';docs={p:BeautifulSoup(p.read_text(),'html.parser') for p in O.rglob('*.html')};bad=[];count=0
for p,s in docs.items():
 for a in s.select('a[href]'):
  raw=a['href'];u=urlsplit(urljoin('https://hornigold.pl/'+str(p.relative_to(O)),raw))
  if u.netloc!='hornigold.pl' or not u.fragment:continue
  target=O/unquote(u.path.lstrip('/'));target=target/'index.html' if target.is_dir() else target
  if target not in docs:continue
  count+=1;t=docs[target];fragment=unquote(u.fragment)
  if not t.find(id=fragment) and not t.find(attrs={'name':fragment}):bad.append({'file':str(p.relative_to(O)),'href':raw,'target':str(target.relative_to(O))})
p=R/'docs/implementation/evidence/fragments.json';p.write_text(json.dumps({'checked':count,'errors':bad},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checked':count,'errors':len(bad),'sample':bad[:12]},ensure_ascii=False));raise SystemExit(bool(bad))
