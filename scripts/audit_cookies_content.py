"""Keep cookie descriptions synchronized across language HTML and PDF source."""
from pathlib import Path
from bs4 import BeautifulSoup
import json
r=Path(__file__).resolve().parent.parent;pages=0
for lang in ['pl','en','de','zh-hans','uk','es','it']:
 d=json.loads((r/'legal'/f'{lang}.json').read_text());sec=next(s for s in d['sections'] if s['id']=='cookies');assert len(sec['paragraphs'])==6
 assert 'hornigold-language-suggestion-dismissed' in sec['paragraphs'][2]
 assert 'sessionStorage' in sec['paragraphs'][2] and 'localStorage' in sec['paragraphs'][2]
 assert 'GitHub Pages' in sec['paragraphs'][-1]
 for p in (r/'site'/lang).rglob('*.html'):
  raw=p.read_text()
  if 'data-page-key="dokumenty"' not in raw and 'data-page-key="prywatnosc"' not in raw:continue
  s=BeautifulSoup(raw,'html.parser');section=s.find('h2',id='cookies').parent
  assert [x.get_text() for x in section.find_all('p',recursive=False)]==sec['paragraphs'],p
  pages+=1
assert pages==14
report={'date':'2026-10-09','revision':'23.6','languages':7,'documentPages':pages,'cookieParagraphsPerLanguage':6,'errors':[]}
(r/'docs/cookies-content-audit-23-6.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
