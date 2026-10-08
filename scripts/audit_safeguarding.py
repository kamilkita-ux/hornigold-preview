"""Verify published-source safeguarding links and content without live personal data."""
from pathlib import Path
import json
from bs4 import BeautifulSoup
r=Path(__file__).resolve().parent.parent
pages=0;languages=set();downloads=0
for p in (r/'site').rglob('*.html'):
 s=BeautifulSoup(p.read_text(),'html.parser')
 if not s.html or not s.body.get('data-page-key'):continue
 lang=p.relative_to(r/'site').parts[0];languages.add(lang);pages+=1
 for key in ('safeguarding','safeguarding-children'):
  assert s.select_one(f'.legal-footer a[href$="#{key}"]'),(p,key,'footer')
 if s.body['data-page-key']=='dokumenty':
  d=json.loads((r/'legal'/f'{lang}.json').read_text())
  for sec in d['sections'][-2:]:
   element=s.find('h2',id=sec['id']).parent
   assert [x.get_text() for x in element.find_all('p',recursive=False) if not x.find('a')]==sec['paragraphs'],(p,'text')
   link=element.select_one('a[download]');target=r/'site'/link['href'].lstrip('/')
   assert target.read_bytes().startswith(b'%PDF'),target
   downloads+=1
assert pages==686 and len(languages)==7 and downloads==14
report={'date':'2026-10-09','contentPages':pages,'technical404RoutesExcluded':7,'languages':sorted(languages),'footerLinks':pages*2,'standaloneDownloads':downloads,'errors':[],'limits':['Operational adoption, named appointments, staff training and on-site display require management confirmation.','PDFs have an HTML alternative; no PDF/UA certification.']}
(r/'docs/safeguarding-source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
