"""Offline review of every canonical Polish page and nonindexable file class."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
from collections import defaultdict
from bs4 import BeautifulSoup
import json,re,argparse,datetime

R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['preview','production-ready'],required=True);a=p.parse_args()
out=R/('_site' if a.mode=='preview' else '_production_ready');release=json.loads((out/'release.json').read_text());base=release['base']
routes=json.loads((R/'routes.json').read_text());pl=[x for x in routes if x.startswith('/pl/')]
expected=json.loads((R/'seo/local-intents-pl.json').read_text());titles=defaultdict(list);descs=defaultdict(list);incoming=defaultdict(set)
inventory=[];errors=[];claims=[];technical=[];ambiguous=[]
business=re.compile(r'\bPLN\b|\bzł\b|Wi-Fi|klimatyzac|prywatn\w* parking|\d+[–-]\d+\s*m²|\d+:\d+|\bsaun\w*|\bjacuzzi\b',re.I)
poetic={'/pl/dla-firm/','/pl/oferty/','/pl/club-hornigold/','/pl/sniadania/'}
def intent(route):
 if '/ilustracje/' in route:return 'Galeria ilustracji; nie dowód wyglądu miejsca ani oferta noclegowa'
 if route.startswith('/pl/miasto-i-okolice/'):return 'Przewodnik po mieście/regionie; treść redakcyjna'
 if route.startswith('/pl/katowice/'):return 'Praktyczny przewodnik; przejście do planu pobytu'
 if '/pokoje/' in route:return 'Wybór kategorii pokoju/apartamentu; oferta do potwierdzenia'
 if '/pobyt/' in route:return 'Planowanie pobytu; nie wynik dostępności'
 if route in ['/pl/dokumenty/','/pl/prywatnosc/']:return 'Informacja prawna; niezależny odbiór prawny wymagany'
 if route in ['/pl/parking/','/pl/sniadania/','/pl/wellness-spa/','/pl/konferencje/','/pl/catering/']:return 'Informacja o usłudze; fakty operacyjne wymagają potwierdzenia'
 return 'Informacja: '+route.rstrip('/').rsplit('/',1)[-1]
for route in pl:
 s=BeautifulSoup((out/unquote(route).lstrip('/')/'index.html').read_text(),'html.parser')
 title=s.title.get_text(' ',strip=True);desc=s.select_one('meta[name=description]')['content'];h1=[h.get_text(' ',strip=True)for h in s.select('h1')]
 titles[title.casefold()].append(route);descs[desc.casefold()].append(route)
 targets=set()
 for link in s.main.select('a[href]'):
  u=urlsplit(link['href'])
  if not u.netloc and u.path.startswith(base):
   target='/'+u.path[len(base):];targets.add(target);incoming[target].add(route)
 nodes=s.select('[data-local-intent-links] a[href]')
 if route in expected:
  t,d,h=expected[route]
  if (title,desc,h1)!=(t,d,[h]):errors.append({'route':route,'rule':'configured metadata/H1'})
  if re.search(r'\bhotel\b',title+' '+desc+' '+' '.join(h1),re.I):errors.append({'route':route,'rule':'unapproved hotel classification'})
 if len(h1)!=1:errors.append({'route':route,'rule':'H1 count'})
 canonical=s.select_one('link[rel=canonical]')['href']
 if canonical!='https://hornigold.pl'+route:errors.append({'route':route,'rule':'canonical'})
 if route in expected and route not in ['/pl/faq/','/pl/informacje/','/pl/kontakt/','/pl/porownaj/']:
  if not nodes:errors.append({'route':route,'rule':'contextual links missing'})
 if route in poetic:ambiguous.append({'route':route,'title':title,'h1':h1,'decision':'Treść istnieje; główny komunikat poetycki/ogólny. Doprecyzować po potwierdzeniu zakresu oferty, bez wzmacniania usług.'})
 for node in s.main.select('p,li,dd,td'):
  text=node.get_text(' ',strip=True)
  if business.search(text):claims.append({'route':route,'excerpt':text[:500],'status':'WYMAGA POTWIERDZENIA','reason':'Istniejąca treść; brak datowanego dossier potwierdzającego to pole. Dopasowanie heurystyczne, nie stwierdzenie fałszu.'})
 inventory.append({'route':route,'intent':intent(route),'title':title,'description':desc,'h1':h1,'mainLinksTo':sorted(targets),'contextualLinksAdded':len(nodes)})
duplicates={'titles':[x for x in titles.values()if len(x)>1],'descriptions':[x for x in descs.values()if len(x)>1]}
if any(duplicates.values()):errors.append({'rule':'duplicate Polish metadata'})
weak=[]
for row in inventory:
 row['incomingFromPolishMain']=len(incoming[row['route']])
 # A guide should offer a meaningful onward path, not every hub on every page.
 relevant=not row['route'].startswith(('/pl/dokumenty/','/pl/prywatnosc/','/pl/miasto-i-okolice/ilustracje/'))
 missing=[]
 if relevant and row['route']!='/pl/pokoje/' and '/pl/pokoje/' not in row['mainLinksTo']:missing.append('/pl/pokoje/')
 if row['route'].startswith('/pl/pobyt/') and row['route']!='/pl/pobyt/' and '/pl/pobyt/' not in row['mainLinksTo']:missing.append('/pl/pobyt/')
 if missing:weak.append({'route':row['route'],'potentialMissingTargets':missing,'status':('ŚWIADOMIE POZOSTAWIONO: treść o pamięci i dziedzictwie; brak automatycznego CTA noclegowego w artykule, nawigacja globalna pozostaje.' if row['route'] in ['/pl/miasto-i-okolice/auschwitz-birkenau/','/pl/miasto-i-okolice/dziedzictwo-zydowskie/','/pl/miasto-i-okolice/miejsca-pamieci-slaska/']else 'KANDYDAT DO REDAKCYJNEGO PRZEGLĄDU; nie wymaga automatycznego dodawania wszystkich linków')})
for file in out.rglob('*.html'):
 rel='/'+str(file.relative_to(out));route=rel[:-10]if rel.endswith('index.html')else rel
 if unquote(route)in {unquote(x)for x in routes}:continue
 s=BeautifulSoup(file.read_text(),'html.parser');robots=s.select_one('meta[name=robots]')
 if not robots or robots['content']!='noindex,nofollow,noarchive':errors.append({'route':route,'rule':'technical file noindex'})
 technical.append({'path':rel,'kind':'alias'if s.select_one('[data-redirect]')else 'error/technical','futureIndexing':'noindex'})
pdfs=sorted('/'+str(f.relative_to(out))for f in out.rglob('*.pdf'))
policy={'technicalHtml':technical,'pdfs':pdfs,'pdfRule':'/documents/*: X-Robots-Tag: noindex w szablonie production-ready; wymaga obsługującego nagłówki hostingu i kontroli HTTP po wdrożeniu.','queryResults':'Nie ma osobnych kanonicznych adresów wyników dat/gości w sitemapie. Przyszłe wyniki wyszukiwania/warianty parametrów wymagają osobnej polityki; nie tworzyć indeksowalnych kombinacji.'}
report={'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':a.mode,'polishCanonicalPages':len(pl),'allCanonicalRoutes':len(routes),'metadataPagesUpdated':len(expected),'contextualLinksAdded':sum(x['contextualLinksAdded']for x in inventory),'duplicates':duplicates,'ambiguousIntentCandidates':ambiguous,'weakLinkCandidates':weak,'businessClaimCandidates':claims,'inventory':inventory,'futureNoindex':policy,'errors':errors,'limits':['Offline source review; no new validation of commercial facts, local distances, external profiles or rankings.','Business-claim scanner is heuristic, not a complete factual audit or legal assessment.']}
D=R/'docs/seo';(D/('pl-intents-'+a.mode+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['inventory','businessClaimCandidates','futureNoindex','ambiguousIntentCandidates','weakLinkCandidates']},ensure_ascii=False));print(json.dumps({'claimCandidates':len(claims),'ambiguousCandidates':len(ambiguous),'weakLinkCandidates':len(weak),'technicalNoindexHtml':len(technical),'pdfs':len(pdfs)}));raise SystemExit(bool(errors))
