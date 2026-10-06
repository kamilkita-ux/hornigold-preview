"""Validate every multilingual guide link and its visible source answer."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse, json, re
from bs4 import BeautifulSoup
from discovery import inputs

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(); parser.add_argument('--mode', choices=['preview','production-ready'], required=True)
args = parser.parse_args(); out = root/('_site' if args.mode == 'preview' else '_production_ready')
release = json.loads((out/'release.json').read_text()); data, routes = inputs(root)
errors = []; links = 0
for p in [out/'llms.txt', *sorted((out/'llms').glob('*.txt'))]:
    text = p.read_text()
    if re.search(r'\b(?:PLN|EUR|GBP|USD)\b|\b\d+\s*m²', text): errors.append(str(p)+': stale numeric offer')
    for raw in re.findall(r'\]\(([^)]+)\)', text):
        links += 1; url = urlsplit(raw)
        if args.mode == 'production-ready':
            if url.scheme != 'https' or url.netloc != 'hornigold.pl': errors.append('Wrong production origin: '+raw)
        elif url.scheme or url.netloc or not url.path.startswith(release['base']): errors.append('Wrong preview link: '+raw)
        path = unquote(url.path if args.mode == 'production-ready' else url.path[len(release['base'])-1:])
        target = out/path.lstrip('/'); target = target/'index.html' if target.is_dir() else target
        if not target.is_file(): errors.append('Missing guide target: '+raw)
for lang, row in data.items():
    if len(row['labels']) != 8 or len(row['questions']) != 3: errors.append(lang+': incomplete translation')
    guide = (out/'llms'/ (lang.lower()+'.txt')).read_text()
    for key in ['pl/faq','pl/informacje']:
        p = out/unquote(routes[key][lang]).lstrip('/')/'index.html'
        soup = BeautifulSoup(p.read_text(),'html.parser'); sections = soup.select('[data-discovery-content]')
        if len(sections) != 1 or soup.html['lang'] != lang: errors.append(lang+': wrong section/language')
        if key == 'pl/faq':
            for question, answer, _ in row['questions']:
                if question not in soup.get_text() or answer not in soup.get_text() or answer not in guide: errors.append(lang+': mismatched answer')
if len(list((out/'llms').glob('*.txt'))) != 7: errors.append('Expected seven guides')
report = {'mode':args.mode,'languages':7,'updatedPages':14,'guideFiles':8,'guideLinks':links,'errors':errors,
          'limits':['Navigation files do not grant crawl access or guarantee inclusion in AI answers.',
                    'No external native-speaker review or live PMS verification performed.']}
(root/'docs/seo'/('discovery-'+args.mode+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False)); raise SystemExit(bool(errors))
