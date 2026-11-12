"""Stage the production verification file and notify IndexNow after public readback."""
import argparse
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ORIGIN = 'https://hornigold.pl'
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['stage', 'notify'])
    parser.add_argument('--assets', type=Path, default=Path('_cloudflare_production/assets'))
    args = parser.parse_args()
    key_file = Path(os.environ['HORNIGOLD_INDEXNOW_KEY_FILE'])
    key = key_file.read_text().strip()
    if not re.fullmatch(r'[0-9a-f]{32,128}', key):
        raise SystemExit('Invalid IndexNow verification key')
    local = json.loads((args.assets / 'release.json').read_text())
    if local.get('buildMode') != 'production-ready' or not re.fullmatch(r'[0-9a-f]{40}', local.get('commit', '')):
        raise SystemExit('A production package tied to a full Git commit is required')
    name = key + '.txt'
    if args.mode == 'stage':
        (args.assets / name).write_text(key + '\n')
        return
    with urlopen(ORIGIN + '/release.json', timeout=15) as response:
        public = json.load(response)
    if public.get('commit') != local['commit'] or not public.get('published'):
        raise SystemExit('Production commit does not match the package')
    with urlopen(ORIGIN + '/' + name, timeout=15) as response:
        if response.read().decode().strip() != key:
            raise SystemExit('Public IndexNow verification file does not match')
    index = ET.parse(args.assets / 'sitemap.xml')
    paths = [e.text for e in index.findall(NS + 'sitemap/' + NS + 'loc')]
    urls = [
        e.text for path in paths
        for e in ET.parse(args.assets / path.rsplit('/', 1)[-1]).findall(NS + 'url/' + NS + 'loc')
        if e.text and e.text.startswith(ORIGIN + '/')
    ]
    # The first migration changes the hreflang links on each translated page.
    urls.extend(ORIGIN + path for path in json.loads(Path('seo/czech-redirects.json').read_text()))
    data = json.dumps({'host': 'hornigold.pl', 'key': key, 'urlList': sorted(set(urls))}).encode()
    request = Request('https://api.indexnow.org/indexnow', data=data,
                      headers={'Content-Type': 'application/json; charset=utf-8'})
    with urlopen(request, timeout=25) as response:
        print(json.dumps({'status': response.status, 'urls': len(set(urls)), 'commit': local['commit']}))


if __name__ == '__main__':
    main()
