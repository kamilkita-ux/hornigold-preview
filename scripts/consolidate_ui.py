# -*- coding: utf-8 -*-
"""Idempotent shared UI for the consolidated v23; never copies old guest pages."""
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent
labels={
'pl':('Odsłony od 05.10.2026','Licznik chwilowo niedostępny','Łączna liczba odsłon, nie unikalnych osób. Odświeżenia i testy mogą zwiększać wynik.'),
'en':('Page views since 5 Oct 2026','Counter currently unavailable','Total page views, not unique people. Reloads and tests may increase the count.'),
'de':('Seitenaufrufe seit 05.10.2026','Zähler derzeit nicht verfügbar','Seitenaufrufe insgesamt, keine einzelnen Personen. Neuladen und Tests können die Zahl erhöhen.'),
'zh-hans':('自2026年10月5日起的浏览次数','计数器暂时不可用','这是页面浏览总数，不是独立访客人数。刷新和测试可能增加计数。'),
'uk':('Перегляди з 05.10.2026','Лічильник тимчасово недоступний','Загальна кількість переглядів, а не унікальних осіб. Оновлення й тести можуть збільшувати число.'),
'es':('Páginas vistas desde el 05/10/2026','Contador no disponible temporalmente','Total de páginas vistas, no de personas únicas. Las recargas y pruebas pueden aumentar la cifra.'),
'it':('Visualizzazioni dal 05/10/2026','Contatore temporaneamente non disponibile','Totale delle visualizzazioni, non delle persone uniche. Ricaricamenti e test possono aumentare il numero.')}
for p in (ROOT/'site').rglob('*.html'):
 raw=p.read_text()
 if 'data-page-key=' not in raw:continue
 s=BeautifulSoup(raw,'html.parser');lang=s.html['lang'].lower();label,offline,detail=labels[lang]
 v=s.select_one('.site-views')
 if not v:raise ValueError(str(p))
 v.clear();v['title']=detail
 a=s.new_tag('span');a.string=label+': ';v.append(a)
 n=s.new_tag('strong');n['data-view-count']='';n['hidden']='';v.append(n)
 u=s.new_tag('span');u['data-view-unavailable']='';u.string=offline;v.append(u)
 if not s.select_one('script[src*="site-stats.js"]'):
  js=s.new_tag('script',src='/assets/site-stats.js',defer=True);s.head.append(js)
 s.select_one('[data-site-version]')['title']='23.1'
 p.write_text(str(s))
print('Consolidated UI: 7 languages')
