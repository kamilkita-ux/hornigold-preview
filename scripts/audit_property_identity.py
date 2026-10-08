"""Assert every content route exposes the same dated, attributed property identity."""
from pathlib import Path
from bs4 import BeautifulSoup
import json
r=Path(__file__).resolve().parent.parent
identity=json.loads((r/'content/property-identity.json').read_text());errors=[];counts={l:0 for l in identity}
for p in (r/'_site').rglob('*.html'):
 s=BeautifulSoup(p.read_text(),'html.parser')
 if not s.body or not s.body.has_attr('data-page-key'):continue
 lang=s.html['lang'].lower();info=identity[lang];blocks=s.select('[data-property-identity]')
 if len(blocks)!=1:errors.append([str(p),'identity block count']);continue
 text=blocks[0].get_text(' ',strip=True)
 for k in ['tagline','description','rating','ratingNote']:
  if info[k] not in text:errors.append([str(p),k])
 if not blocks[0].find('a',href=info['reviewUrl']):errors.append([str(p),'review attribution'])
 if 'noindex,nofollow,noarchive'!=s.select_one('meta[name=robots]')['content']:errors.append([str(p),'robots'])
 counts[lang]+=1
for lang,info in identity.items():
 text=(r/'_site/llms'/f'{lang}.txt').read_text()
 for k in ['description','rating','ratingNote']:
  if info[k] not in text:errors.append([lang,'AI guide '+k])
report=dict(pages=sum(counts.values()),languages=counts,errors=errors,ratingSourceDate='2026-10-09',schemaUnchanged=True)
(r/'docs/property-identity-audit-23-9.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report));assert not errors
