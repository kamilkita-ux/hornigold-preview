"""Evidence-based multilingual discovery guides; no network or indexing changes."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
from bs4 import BeautifulSoup

KEYS = ['pl/pokoje', 'pl/rezerwacja', 'pl/lokalizacja', 'pl/informacje',
        'pl/faq', 'pl/dokumenty', 'pl/miasto-i-okolice', 'pl/kontakt']

def inputs(root):
    data = json.loads((root/'seo/discovery-content.json').read_text())
    routes = {}
    for key in KEYS:
        soup = BeautifulSoup((root/'site'/key/'index.html').read_text(), 'html.parser')
        routes[key] = {x['hreflang']: urlsplit(x['href']).path
                       for x in soup.select('link[hreflang]') if x['hreflang'] != 'x-default'}
    return data, routes

def write_guides(root, out, base='/', mode='preview'):
    data, routes = inputs(root)
    def target(route):
        return ('https://hornigold.pl' + route) if mode == 'production-ready' else base + route.lstrip('/')
    folder = out/'llms'; folder.mkdir(exist_ok=True)
    index = ['# Hornigold w Zielonej Kamienicy', '',
             '> Multilingual navigation to source pages / Wielojęzyczny przewodnik po stronach źródłowych.', '',
             'This file is a navigation aid, not a price, availability or booking feed.',
             'Preview copies are intentionally excluded from crawling and indexing.', '',
             '## Languages / Języki']
    for lang, row in data.items():
        filename = lang.lower()+'.txt'
        index.append(f'- [{row["name"]}]({target("/llms/"+filename)})')
        lines = ['# '+row['guide'], '', '> '+row['notice'], '', '## '+row['heading']]
        for key, label in zip(KEYS, row['labels']):
            route = routes[key][lang]
            path = root/'site'/unquote(route).lstrip('/')/'index.html'
            if not path.is_file(): raise ValueError('Missing source page: '+route)
            lines.append(f'- [{label}]({target(route)})')
        lines += ['', '## '+row['labels'][4]]
        for question, answer, key in row['questions']:
            lines += ['', '### '+question, answer, f'[{row["labels"][KEYS.index(key)]}]({target(routes[key][lang])})']
        (folder/filename).write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (out/'llms.txt').write_text('\n'.join(index)+'\n', encoding='utf-8')

def apply_visible_content(root):
    data, routes = inputs(root)
    for lang, row in data.items():
        for key in ['pl/informacje', 'pl/faq']:
            p = root/'site'/unquote(routes[key][lang]).lstrip('/')/'index.html'
            soup = BeautifulSoup(p.read_text(), 'html.parser')
            for old in soup.select('[data-discovery-content]'): old.decompose()
            if key == 'pl/informacje':
                section = soup.new_tag('section', attrs={'class':'wrap narrow section', 'data-discovery-content':''})
                h = soup.new_tag('h2'); h.string = row['heading']; section.append(h)
                para = soup.new_tag('p'); para.string = row['intro']; section.append(para)
                nav = soup.new_tag('nav', attrs={'class':'completion-links', 'aria-label':row['heading']})
                for target_key in ['pl/faq','pl/rezerwacja','pl/dokumenty','pl/kontakt']:
                    a = soup.new_tag('a', href=routes[target_key][lang], attrs={'class':'text-link'})
                    a.string = row['labels'][KEYS.index(target_key)]; nav.append(a)
                section.append(nav)
                soup.main.select_one('section').insert_after(section)
            else:
                section = soup.new_tag('section', attrs={'class':'wrap narrow section', 'data-discovery-content':''})
                h = soup.new_tag('h2'); h.string = row['heading']; section.append(h)
                for question, answer, target_key in row['questions']:
                    detail = soup.new_tag('details'); summary = soup.new_tag('summary'); summary.string = question
                    para = soup.new_tag('p'); para.string = answer
                    a = soup.new_tag('a', href=routes[target_key][lang], attrs={'class':'text-link'})
                    a.string = row['labels'][KEYS.index(target_key)]
                    detail.extend([summary, para, a]); section.append(detail)
                soup.main.append(section)
            p.write_text(str(soup), encoding='utf-8')

if __name__ == '__main__':
    root = Path(__file__).resolve().parent.parent
    apply_visible_content(root)
    write_guides(root, root/'site')
    print('Updated 14 existing pages and 8 navigation files in 7 languages.')
