"""Stage the production verification file and notify IndexNow after public readback."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ORIGIN = 'https://hornigold.pl'
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def fetch_public(path):
    # The production edge accepts curl for anonymous verification requests.
    return subprocess.run(['curl', '--fail', '--silent', '--max-time', '15', ORIGIN + path],
                          check=True, capture_output=True).stdout


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
    public = json.loads(fetch_public('/release.json'))
    if public.get('commit') != local['commit'] or not public.get('published'):
        raise SystemExit('Production commit does not match the package')
    if fetch_public('/' + name).decode().strip() != key:
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
    data = json.dumps({'host': 'hornigold.pl', 'key': key, 'keyLocation': ORIGIN + '/' + name, 'urlList': sorted(set(urls))}).encode()
    request = Request('https://api.indexnow.org/indexnow', data=data,
                      headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urlopen(request, timeout=25) as response:
            status = response.status
    except HTTPError as error:
        detail = error.read(1000).decode(errors='replace').replace(key, '[redacted]')
        raise SystemExit(f'IndexNow HTTP {error.code}: {detail}') from None
    print(json.dumps({'status': status, 'urls': len(set(urls)), 'commit': local['commit']}))


if __name__ == '__main__':
    main()
