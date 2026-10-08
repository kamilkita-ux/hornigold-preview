"""Check disclosure publication while guarding the inactive payment boundary."""
from pathlib import Path
import json
from bs4 import BeautifulSoup
r=Path(__file__).resolve().parent.parent
release=json.loads((r/'release.json').read_text());contract=json.loads((r/'legal/checkout-contract.json').read_text())
assert not any(release[k] for k in ['bookingEnabled','paymentsEnabled','indexing','onlineSalesOperationalConfirmation'])
assert contract['enabled'] is False and len(contract['labels'])==7
assert contract['labels']['pl']=='Rezerwuję z obowiązkiem zapłaty'
assert 'contractFormationRule' in contract['mustConfirmBeforeActivation']
assert 'amountPayableNow' in contract['visibleImmediatelyBeforeOrder']
pages=0;document_pages=0
for p in (r/'site').rglob('*.html'):
 s=BeautifulSoup(p.read_text(),'html.parser')
 if not s.body or not s.body.get('data-page-key'):continue
 assert s.select_one('.legal-footer a[href$="#online-sales"]'),p
 assert 'noindex' in s.select_one('meta[name=robots]')['content'],p
 pages+=1
 if s.body['data-page-key']=='dokumenty':
  lang=p.relative_to(r/'site').parts[0];d=json.loads((r/'legal'/f'{lang}.json').read_text());sec=next(x for x in d['sections'] if x['id']=='online-sales');el=s.find(id='online-sales').parent
  assert len(sec['paragraphs'])==10
  assert [x.get_text() for x in el.find_all('p',recursive=False)]==sec['paragraphs'],p
  assert contract['labels']['zh-Hans' if lang=='zh-hans' else lang] in el.get_text(),p
  assert len(el.select('li a[href^="https://"]'))==5,p
  assert len(s.select('.legal-content section'))==9,p
  document_pages+=1
assert pages==686 and document_pages==7
report={'date':'2026-10-09','revision':release['revision'],'languages':7,'contentPages':pages,'documentPages':document_pages,'legalSections':9,'paragraphsAddedPerLanguage':10,'inactiveCheckoutLabelsPrepared':7,'bookingEnabled':False,'paymentsEnabled':False,'operationalAndLegalApproval':False,'errors':[]}
(r/'docs/online-sales-source-audit-23-7.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
