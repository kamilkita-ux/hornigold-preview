"""Apply local-only Polish metadata and contextual navigation; no new business facts."""
from pathlib import Path
from bs4 import BeautifulSoup
import json

R=Path(__file__).resolve().parent.parent
data=json.loads((R/'seo/local-intents-pl.json').read_text())
overrides=json.loads((R/'seo/metadata-overrides.json').read_text())
links={
 '/pl/': [('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Dojazd do Hornigold','/pl/lokalizacja/')],
 '/pl/pokoje/': [('Zaplanuj pobyt','/pl/pobyt/'),('Nocleg służbowy','/pl/pobyt/sluzbowo/'),('Weekend w Katowicach','/pl/pobyt/weekend/'),('Pobyt na wydarzenie','/pl/pobyt/wydarzenie/'),('Lokalizacja i dojazd','/pl/lokalizacja/')],
 '/pl/pobyt/': [('Wszystkie pokoje i apartamenty','/pl/pokoje/'),('Podróż służbowa','/pl/pobyt/sluzbowo/'),('Weekend w Katowicach','/pl/pobyt/weekend/'),('Nocleg na wydarzenie','/pl/pobyt/wydarzenie/'),('Spodek, MCK i NOSPR – plan przyjazdu','/pl/katowice/wydarzenie/'),('Lokalizacja i dojazd','/pl/lokalizacja/')],
 '/pl/pobyt/sluzbowo/': [('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Lokalizacja i dojazd','/pl/lokalizacja/'),('Przewodnik przed podróżą służbową','/pl/katowice/sluzbowo/')],
 '/pl/pobyt/weekend/': [('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Lokalizacja i dojazd','/pl/lokalizacja/'),('Katowice na 24 i 48 godzin','/pl/katowice/weekend/')],
 '/pl/pobyt/wydarzenie/': [('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Lokalizacja i dojazd','/pl/lokalizacja/'),('Spodek, MCK i NOSPR – plan przyjazdu','/pl/katowice/wydarzenie/')],
 '/pl/katowice/wydarzenie/': [('Nocleg na wydarzenie','/pl/pobyt/wydarzenie/'),('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Lokalizacja i dojazd','/pl/lokalizacja/')],
 '/pl/lokalizacja/': [('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Przyjazd samochodem','/pl/parking/'),('Plan przyjazdu na wydarzenie','/pl/katowice/wydarzenie/')],
 '/pl/parking/': [('Lokalizacja i dojazd','/pl/lokalizacja/'),('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Kontakt z recepcją','/pl/kontakt/')]
}
for route in ['/pl/faq/','/pl/catering/','/pl/konferencje/','/pl/o-nas/','/pl/opinie/','/pl/pobyt/dluzszy-pobyt/','/pl/pobyt/rodzina/','/pl/sniadania/','/pl/wellness-spa/']:
 links[route]=[('Pokoje i apartamenty','/pl/pokoje/'),('Plan pobytu','/pl/pobyt/'),('Lokalizacja i dojazd','/pl/lokalizacja/')]
for route in sorted(set(data)|set(links)):
 p=R/'site'/route.lstrip('/')/'index.html';s=BeautifulSoup(p.read_text(),'html.parser')
 assert len(s.select('h1'))==1
 if route in data:
  title,description,h1=data[route]
  s.title.string=title;s.select_one('meta[name=description]')['content']=description;s.h1.string=h1
  for name,value in [('og:title',title),('og:description',description),('twitter:title',title),('twitter:description',description)]:
   node=s.find('meta',attrs={'property' if name.startswith('og:') else 'name':name})
   if node:node['content']=value
  overrides[route]={'title':title,'description':description}
 for node in s.select('[data-local-intent-links]'):node.decompose()
 if route in links:
  section=s.new_tag('section',attrs={'class':'wrap section','data-local-intent-links':''})
  heading=s.new_tag('h2');heading.string='Zaplanuj kolejne kroki';section.append(heading)
  nav=s.new_tag('nav',attrs={'class':'completion-links','aria-label':'Zaplanuj kolejne kroki'})
  for label,target in links[route]:
   assert (R/'site'/target.lstrip('/')/'index.html').is_file()
   a=s.new_tag('a',href=target,attrs={'class':'text-link','data-stay':''});a.string=label;nav.append(a)
  section.append(nav)
  intro=s.main.select_one('section');intro.insert_after(section)
 p.write_text(str(s))
(R/'seo/metadata-overrides.json').write_text(json.dumps(overrides,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'metadataPages':len(data),'navigationPages':len(links),'contextualLinks':sum(map(len,links.values()))}))
