"""Validate factual accessibility disclosures and preserve unverified journey gates."""
from pathlib import Path
import argparse,datetime,json
from bs4 import BeautifulSoup
r=Path(__file__).resolve().parent.parent
rel=json.loads((r/'release.json').read_text());plan=json.loads((r/'docs/PAD_BOOKING_ACCEPTANCE.json').read_text());contract=json.loads((r/'legal/checkout-contract.json').read_text())
languages=rel['languages']
assert languages and len(languages)==len(set(languages))
assert plan['languages']==languages
assert rel['accessibilityJourneyVerified'] is False and rel['PADScopeConfirmed'] is False
if rel.get('taggedPDFs'):
 from audit_tagged_legal_candidates import audit
 expected={f'hornigold-{edition}-{lang.lower()}.pdf' for edition in ('policies','safeguarding','safeguarding-children') for lang in languages}
 documents=list((r/'site/documents').glob('*.pdf'))
 assert {p.name for p in documents}==expected
 for path in documents:
  assert not audit(path)['errors'],path
assert not rel['bookingEnabled'] and not rel['paymentsEnabled'] and not rel['indexing']
assert not plan['verified'] and len(plan['stages'])==15
assert all(set(s['resultsByLanguage'])==set(languages) for s in plan['stages'])
assert all(v=='NOT_RUN' for s in plan['stages'] for v in s['resultsByLanguage'].values())
assert {'PADScopeAssessment','endToEndAccessibilityAcceptance','accessibleDurableConfirmations'}<=set(contract['mustConfirmBeforeActivation'])
pages=0
for language in languages:
 lang=language.lower()
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
assert pages==len(languages)
report={'date':datetime.date.today().isoformat(),'revision':rel['revision'],'languages':len(languages),'documentPages':pages,'accessibilityParagraphs':8,'futureStages':len(plan['stages']),'futureStageLanguageCells':sum(len(s['resultsByLanguage']) for s in plan['stages']),'futureTestsExecuted':0,'scopeConfirmed':False,'manualReaderAcceptance':False,'pdfUAValidated':False,'errors':[]}
parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,default=r/'docs/implementation/evidence/pad-source-current.json');args=parser.parse_args();args.report.parent.mkdir(parents=True,exist_ok=True)
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report))
