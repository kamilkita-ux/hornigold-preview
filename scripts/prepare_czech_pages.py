"""Create isolated Czech candidates; never activate or publish a partial locale."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup, Comment, Doctype

ROOT = Path(__file__).resolve().parent.parent

def prepare(destination):
    destination = destination.resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError('Candidates must be written outside repository sources')
    config = json.loads((ROOT / 'content/localization/cs-rollout.json').read_text())
    rows = json.loads((ROOT / 'content/localization/cs-translations.json').read_text())
    if any(not r.get('reviewed') or not r.get('translation') for r in rows):
        raise ValueError('Unreviewed translations remain')
    for name, digest in config['sourcePages'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Source changed: ' + name)
    translations = {r['source']: r['translation'] for r in rows}
    missing, written = set(), []
    routes = [r for r in json.loads((ROOT / 'routes.json').read_text()) if r.startswith('/en/')]
    def translate(value):
        core = value.strip()
        if not core or not any(ch.isalpha() for ch in core):
            return value
        if core not in translations:
            missing.add(core)
            return value
        return value[:len(value)-len(value.lstrip())] + translations[core] + value[len(value.rstrip()):]
    def url(value):
        if value.startswith('/en/'):
            return '/cs/' + value[4:]
        return value.replace('https://hornigold.pl/en/', 'https://hornigold.pl/cs/')
    def schema(value):
        if isinstance(value, dict):
            return {k: ('cs' if k == 'inLanguage' and v == 'en' else schema(v)) for k,v in value.items()}
        if isinstance(value, list):
            return [schema(v) for v in value]
        if isinstance(value, str):
            return url(translations.get(value, value))
        return value
    for route in routes:
        source = ROOT / 'site' / route.lstrip('/') / 'index.html'
        soup = BeautifulSoup(source.read_text(), 'html.parser')
        soup.html['lang'] = 'cs'
        for node in list(soup.find_all(string=True)):
            if isinstance(node, (Comment, Doctype)) or node.parent.name in ('script', 'style'):
                continue
            # Native language names remain native in the language selector.
            if node.find_parent(attrs={'data-language': True}):
                continue
            node.replace_with(translate(str(node)))
        for tag in soup.find_all(True):
            for attr in ('alt', 'title', 'aria-label', 'placeholder'):
                if attr in tag.attrs:
                    tag[attr] = translate(tag[attr])
            if tag.name == 'meta' and tag.get('name') in ('description','twitter:title','twitter:description'):
                tag['content'] = translate(tag['content'])
            if tag.name == 'meta' and tag.get('property') in ('og:title','og:description'):
                tag['content'] = translate(tag['content'])
            if tag.name == 'meta' and tag.get('property') == 'og:locale':
                tag['content'] = 'cs_CZ'
            if tag.has_attr('data-language') or tag.has_attr('hreflang'):
                continue
            for attr in ('href','content','action'):
                if attr in tag.attrs:
                    tag[attr] = url(tag[attr])
            if tag.name == 'script' and '/assets/messages/en.js' in tag.get('src',''):
                tag['src'] = '/assets/messages/cs.js'
        for script in soup.select('script[type="application/ld+json"]'):
            script.string = json.dumps(schema(json.loads(script.string)), ensure_ascii=False)
        nav = soup.select_one('[data-language-switcher]')
        en = nav.select_one('[data-language="en"]') if nav else None
        if en:
            en.attrs.pop('aria-current',None)
            cs = copy.copy(en)
            cs['data-language'] = cs['lang'] = cs['hreflang'] = 'cs'
            cs['href'] = url(en['href'])
            cs['aria-current'] = 'page'
            spans = cs.find_all('span')
            spans[0].string = '🇨🇿'
            spans[1].string = 'Čeština'
            en.insert_after(cs)
        canonical = soup.select_one('link[rel="canonical"]')
        alternate = soup.select_one('link[hreflang="en"]')
        if alternate:
            cs = copy.copy(alternate)
            cs['hreflang'] = 'cs'
            cs['href'] = canonical['href']
            alternate.insert_after(cs)
        target = destination / route.replace('/en/','cs/',1) / 'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(str(soup)+'\n')
        written.append(str(target))
    report = {'state':'isolated-candidates-not-published','routes':len(written),'missing':sorted(missing),'written':written,
              'limitations':['Existing languages not updated with reciprocal Czech links yet','Dynamic locale route maps and external English fallback disclosure not yet verified','Legal PDF integration and responsive tests still required']}
    (destination / 'candidate-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-directory',type=Path,required=True)
    args=parser.parse_args()
    result=prepare(args.output_directory)
    print(json.dumps({'routes':result['routes'],'missing':result['missing']},ensure_ascii=False))
    raise SystemExit(bool(result['missing']))
