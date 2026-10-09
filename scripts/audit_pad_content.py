"""Validate factual accessibility disclosures and preserve unverified journey gates."""
from pathlib import Path
import json
from bs4 import BeautifulSoup
r=Path(__file__).resolve().parent.parent
rel=json.loads((r/'release.json').read_text());plan=json.loads((r/'docs/PAD_BOOKING_ACCEPTANCE.json').read_text());contract=json.loads((r/'legal/checkout-contract.json').read_text())
assert rel['accessibilityJourneyVerified'] is False and rel['PADScopeConfirmed'] is False and rel['taggedPDFs'] is False
assert not rel['bookingEnabled'] and not rel['paymentsEnabled'] and not rel['indexing']
assert not plan['verified'] and len(plan['stages'])==15
assert all(v=='NOT_RUN' for s in plan['stages'] for v in s['resultsByLanguage'].values())
assert {'PADScopeAssessment','endToEndAccessibilityAcceptance','accessibleDurableConfirmations'}<=set(contract['mustConfirmBeforeActivation'])
pages=0
for lang in ['pl','en','de','zh-hans','uk','es','it']:
 d=json.loads((r/'legal'/f'{lang}.json').read_text());sec=next(s for s in d['sections'] if s['id']=='accessibility');assert len(sec['paragraphs'])==8
 for p in (r/'site'/lang).rglob('index.html'):
  s=BeautifulSoup(p.read_text(),'html.parser')
  if not s.body or not s.body.get('data-page-key'):continue
  assert s.select_one('.legal-footer a[href$="#accessibility"]'),p
  if s.body['data-page-key']=='dokumenty':
   el=s.find(id='accessibility').parent
   assert [x.get_text() for x in el.find_all('p',recursive=False)]==sec['paragraphs'],p
   assert 'PDF/UA' in el.get_text() and 'KWHotel' in el.get_text() and 'Fiserv' in el.get_text(),p
   assert len(el.select('li a'))==3,p
   pages+=1
assert pages==7
report={'date':'2026-10-09','revision':rel['revision'],'languages':7,'documentPages':pages,'accessibilityParagraphs':8,'futureStages':15,'futureStageLanguageCells':105,'futureTestsExecuted':0,'scopeConfirmed':False,'errors':[]}
(r/'docs/pad-source-audit-23-8.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
