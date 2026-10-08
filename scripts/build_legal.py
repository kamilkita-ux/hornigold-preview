"""Render translated policies and shared privacy controls into the existing seven-language site."""
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import json,re
ROOT=Path(__file__).resolve().parent.parent
VERSION=str(json.loads((ROOT/'release.json').read_text())['version'])
langs=['pl','en','de','zh-hans','uk','es','it']
content={l:json.loads((ROOT/'legal'/f'{l}.json').read_text()) for l in langs}
reference=[(x['id'],len(x['paragraphs'])) for x in content['pl']['sections']]
for l,d in content.items():
 assert [(x['id'],len(x['paragraphs'])) for x in d['sections']]==reference,l
 assert all(d['ui'].get(k) for k in content['pl']['ui']),l
paths={}
for p in (ROOT/'site').rglob('*.html'):
 raw=p.read_text()
 if 'data-page-key=' not in raw:continue
 s=BeautifulSoup(raw,'html.parser');lang=s.html.get('lang','').lower()
 if lang not in langs:continue
 key=s.body.get('data-page-key')
 if key in ('dokumenty','prywatnosc'):paths[(lang,key)]='/'+str(p.parent.relative_to(ROOT/'site'))+'/'
for p in (ROOT/'site').rglob('*.html'):
 raw=p.read_text()
 if 'data-page-key=' not in raw:continue
 s=BeautifulSoup(raw,'html.parser');lang=s.html.get('lang','').lower()
 if lang not in content:continue
 d=content[lang];u=d['ui'];doc=paths[(lang,'dokumenty')];privacy=paths[(lang,'prywatnosc')]
 pdf='/documents/hornigold-policies-'+lang+'.pdf'
 def fragment(html):return BeautifulSoup(html,'html.parser')
 key=s.body.get('data-page-key')
 if key in ('dokumenty','prywatnosc'):
  sections=d['sections'] if key=='dokumenty' else [x for x in d['sections'] if x['id'] in ('privacy','cookies')]
  title=d['title'] if key=='dokumenty' else sections[0]['title']
  s.title.string=title+' | Hornigold'
  s.select_one('meta[name=description]')['content']=d['intro']
  toc=''.join(f'<a href="{doc}#{x["id"]}">{escape(x["title"])}</a>' for x in d['sections'])
  html=f'<div class="wrap legal-content"><h1>{escape(title)}</h1><p>{escape(d["intro"])}</p><p><a class="button" href="{pdf}" download>{escape(d["download"])}</a></p><nav class="legal-toc" aria-label="{escape(u["toc"])}">{toc}</nav>'
  for sec in sections:
   html+=f'<section aria-labelledby="{sec["id"]}"><h2 id="{sec["id"]}">{escape(sec["title"])}</h2>'
   html+=''.join('<p>'+escape(t)+'</p>' for t in sec['paragraphs'])
   if sec.get('sources'):
    html+='<ul>'+''.join('<li><a href="'+escape(x['url'],quote=True)+'">'+escape(x['title'])+'</a> (2026-10-09)</li>' for x in sec['sources'])+'</ul>'
   if sec['id'] in ('safeguarding','safeguarding-children'):
    download='/documents/hornigold-'+sec['id']+'-'+lang+'.pdf'
    html+=f'<p><a class="button" href="{download}" download>{escape(sec["title"])} — PDF</a></p>'
   html+='</section>'
  html+='</div>'
  s.main.clear();s.main.append(fragment(html))
 for old in s.select('[data-legal-generated]'):old.decompose()
 css=s.new_tag('link',rel='stylesheet',href='/assets/legal.css');css['data-legal-generated']='';s.head.append(css)
 script=s.new_tag('script',src='/assets/privacy.js',defer=True);script['data-legal-generated']='';s.head.append(script)
 for old in s.select('meta[http-equiv=Content-Security-Policy]'):old.decompose()
 csp=s.new_tag('meta',attrs={'http-equiv':'Content-Security-Policy','content':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-src https://www.google.com; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'"});s.head.insert(1,csp)
 if not s.select_one('meta[name=referrer]'):s.head.append(s.new_tag('meta',attrs={'name':'referrer','content':'no-referrer'}))
 else:s.select_one('meta[name=referrer]')['content']='no-referrer'
 footerlinks=''.join(f'<a href="{doc}#{x["id"]}">{escape(x["title"])}</a>' for x in d['sections'])
 s.footer.append(fragment(f'<nav class="wrap legal-footer" data-legal-generated aria-label="{escape(u["legal"])}">{footerlinks}<a href="{pdf}" download>{escape(d["download"])}</a><a href="{doc}#cookies" data-privacy-open>{escape(u["settings"])}</a></nav>'))
 s.footer.append(fragment(f'<section id="privacy-notice" class="privacy-notice wrap" data-legal-generated hidden aria-label="{escape(u["settings"])}"><p>{escape(u["notice"])}</p><div class="privacy-actions"><button type="button" data-privacy-necessary>{escape(u["necessary"])}</button><a href="{doc}#cookies" data-privacy-open>{escape(u["settings"])}</a></div></section>'))
 modal=f'<dialog id="privacy-dialog" class="privacy-dialog" data-legal-generated aria-labelledby="privacy-title" data-cleared="{escape(u["cleared"],quote=True)}"><button type="button" data-privacy-close>{escape(u["close"])}</button><h2 id="privacy-title">{escape(u["settings"])}</h2><p>{escape(u["notice"])}</p><label><input type="checkbox" name="maps" aria-describedby="maps-detail">{escape(u["maps"])}</label><p id="maps-detail">{escape(u["mapDetail"])}</p><p class="privacy-panel-help">{escape(u["inactive"])}</p><p><a href="{privacy}">{escape(u["privacyLink"])}</a></p><div class="privacy-actions"><button type="button" data-privacy-necessary>{escape(u["necessary"])}</button><button type="button" data-privacy-save>{escape(u["save"])}</button></div><button type="button" data-privacy-clear>{escape(u["clear"])}</button><p role="status"></p></dialog>'
 s.body.append(fragment(modal))
 for form in s.select('form[data-enquiry],form[data-business-enquiry]'):
  note=fragment(f'<p class="privacy-inline" data-legal-generated><a href="{privacy}#privacy">{escape(u["form"])}</a></p>')
  form.insert(0,note)
 for el in s.select('.mobile-contact,.mobile-book'):
  # Keep visual positioning but put shortcuts inside a named navigation landmark.
  if el.parent.get('data-mobile-landmark') is None:
   nav=s.new_tag('nav',attrs={'aria-label':u['quick']+' '+el.get_text(' ',strip=True),'data-mobile-landmark':''});el.wrap(nav)
 for nav in s.select('[data-mobile-landmark]'):nav['aria-label']=u['quick']+' '+nav.get_text(' ',strip=True)
 if key=='opinie':s.main.append(fragment(f'<p class="wrap privacy-inline" data-legal-generated>{escape(u["reviews"])}</p>'))
 if key=='club-hornigold' and not (ROOT/'content/club.json').exists():
  s.main.clear();s.main.append(fragment(f'<div class="wrap legal-content"><h1>Club Hornigold</h1><p>{escape(u["club"])}</p><p><a href="mailto:office@hornigold.pl">office@hornigold.pl</a> · <a href="tel:+48608662707">+48 608 662 707</a></p></div>'))
 if key in ('pokoje','katowice'):
  for h in s.select('.card-body h3,.editorial-card h3'):h.name='h2';h['class']=h.get('class',[])+['a11y-card-heading']
 v=s.select_one('[data-site-version]')
 if v:v.string=VERSION
 # Complete company disclosures on every page, without translating the registered name.
 company=s.select_one('.footer-company')
 if company:
  for old in company.select('[data-company-register]'):old.decompose()
  capital={'pl':'Kapitał zakładowy','en':'Share capital','de':'Stammkapital','es':'Capital social','it':'Capitale sociale','uk':'Статутний капітал','zh-hans':'注册资本'}[lang]
  company.append(fragment(f'<p data-company-register>KRS: 0001265196 · <span>{capital}: 500 000 PLN</span><br><span lang="pl">Sąd Rejonowy Katowice-Wschód w Katowicach, VIII Wydział Gospodarczy Krajowego Rejestru Sądowego</span></p>'))
 p.write_text(str(s))
release=json.loads((ROOT/'release.json').read_text());release.update(legalDocumentsDate='2026-10-09',privacyControls=True,independentLegalReview=False);(ROOT/'release.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'languages':len(content),'sectionsPerLanguage':len(reference),'pages':693},ensure_ascii=False))
