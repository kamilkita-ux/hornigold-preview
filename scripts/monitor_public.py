"""Read-only checks. No forms, tracking consent, mail or transactions are submitted."""
import argparse
import datetime
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


def header_values(response, name):
    """Header names are case-insensitive; their values (notably Location) are not."""
    values = []
    for line in response['headers'].splitlines():
        key, separator, value = line.partition(':')
        if separator and key.strip().lower() == name.lower():
            values.append(value.strip())
    return values


def indexing_blocked(response):
    """Detect explicit indexing exclusions in HTTP and crawler HTML directives."""
    directives = []

    class RobotsParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if tag == 'meta' and (values.get('name') or '').lower() in ('robots', 'googlebot', 'googlebot-news'):
                directives.append(values.get('content') or '')

    for line in response['headers'].splitlines():
        key, _, value = line.partition(':')
        if key.strip().lower() == 'x-robots-tag':
            directives.append(value)
    RobotsParser().feed(response['body'])
    return any(set(re.findall(r'[a-z]+', value.lower())) & {'noindex', 'none'} for value in directives)


def request(url):
    # curl verifies the server certificate by default; never use --insecure.
    p = subprocess.run(['curl', '-sS', '--max-time', '25', '-D', '-', '-w', '\n%{http_code}', url], capture_output=True, text=True)
    payload, _, status = p.stdout.rpartition('\n')
    head, _, body = payload.replace('\r\n', '\n').partition('\n\n')
    # HTTPS proxies may emit a CONNECT response before actual server headers.
    while body.startswith('HTTP/'):
        candidate, separator, remainder = body.partition('\n\n')
        if not separator:
            break
        head, body = candidate, remainder
    tls = url.startswith('https://') and p.returncode == 0 and status.isdigit() and 100 <= int(status) <= 599
    return {'status': status, 'headers': head, 'body': body, 'tlsVerified': tls, 'curlExit': p.returncode}


def run_checks(self_test=False):
    checks = []

    def check(name, ok, detail):
        checks.append({'name': name, 'ok': bool(ok), 'detail': detail})

    if self_test:
        check('controlled_failure', False, 'TEST ONLY: simulated unavailable endpoint; no production configuration changed')
        return checks
    release_response=request('https://hornigold.pl/release.json')
    try: served_release=json.loads(release_response['body'])
    except (ValueError,TypeError): served_release={}
    expected_routes=set(json.loads((Path(__file__).resolve().parent.parent/'routes.json').read_text()))
    if served_release.get('audit3ImprovementsDate'):
        excluded=json.loads((Path(__file__).resolve().parent.parent/'seo/indexing-policy.json').read_text())['excludedRoutes']
        expected_routes-=set(excluded)
    excluded_routes = set(excluded) if served_release.get('audit3ImprovementsDate') else set()
    for route in ['/pl/', '/en/', '/pl/pokoje/', '/pl/lokalizacja/', '/pl/rezerwacja/']:
        r = request('https://hornigold.pl' + route)
        blocked = indexing_blocked(r)
        check(route, r['status'] == '200' and r['tlsVerified'] and blocked == (route in excluded_routes), {
            'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit'], 'indexingBlocked': blocked, 'expectedNoindex': route in excluded_routes, 'hsts': bool(header_values(r, 'strict-transport-security'))})
    r = request('https://hornigold.pl/robots.txt')
    check('robots', r['status'] == '200' and r['tlsVerified'] and 'Allow: /' in r['body'] and '\nDisallow: /\n' not in r['body'], {'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit']})
    r = request('https://hornigold.pl/sitemap.xml')
    try:
        urls = [e.text for e in ET.fromstring(r['body']).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        valid = len(urls)==len(set(urls)) and set(urls)=={'https://hornigold.pl'+path for path in expected_routes}
    except (ET.ParseError, ValueError):
        urls, valid = [], False
    check('sitemap', r['status'] == '200' and r['tlsVerified'] and valid, {'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit'], 'count': len(urls)})
    r = request('https://www.hornigold.pl/pl/')
    locations = header_values(r, 'location')
    check('www301', r['status'] == '301' and r['tlsVerified'] and locations == ['https://hornigold.pl/pl/'], {'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit'], 'locations': locations})
    root_query = 'utm_source=monitor&utm_medium=health&utm_campaign=RootCase'
    r = request('https://hornigold.pl/?' + root_query)
    locations = header_values(r, 'location')
    check('root301_utm', r['status'] == '301' and r['tlsVerified'] and locations == ['https://hornigold.pl/pl/?' + root_query], {'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit'], 'locations': locations})
    # GET reads the aggregate counter; only POST would increment it.
    r = request('https://hornigold.pl/api/site-stats')
    try:
        counter = json.loads(r['body'])
    except (ValueError, TypeError):
        counter = None
    counter_valid = isinstance(counter, dict) and type(counter.get('total')) is int and 0 <= counter['total'] <= 2 ** 53 - 1 and counter.get('metric') == 'pageviews'
    try:
        counter_valid = counter_valid and datetime.date.fromisoformat(counter.get('startedAt', '')).isoformat() == counter['startedAt']
    except (ValueError, TypeError):
        counter_valid = False
    check('counter', r['status'] == '200' and r['tlsVerified'] and counter_valid, {'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit'], 'validJSON': counter_valid})
    r = request('https://hornigold.pl/__monitor_missing_20261011__/')
    check('404', r['status'] == '404' and r['tlsVerified'] and indexing_blocked(r), {'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit']})
    r = release_response
    try:
        release = json.loads(r['body'])
    except (ValueError, TypeError):
        release = {}
    check('release', r['status'] == '200' and r['tlsVerified'] and isinstance(release, dict) and bool(release.get('revision')), {'http': r['status'], 'tls': r['tlsVerified'], 'curlExit': r['curlExit'], 'release': release})
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='docs/implementation/evidence/monitor-latest.json')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    checks = run_checks(args.self_test)
    report = {'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'mode': 'controlled-test' if args.self_test else 'production-read-only', 'ok': all(x['ok'] for x in checks), 'checks': checks, 'limits': [
        'TLS means a successful HTTPS request with default certificate verification; not a certificate-expiry forecast or a full security certification.',
        'No mail delivery, booking, payment, GA4 receipt or Google indexing is inferred from HTTP health.',
        'No Google account API credentials are configured.']}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'ok': report['ok'], 'checks': len(checks), 'report': str(out)}))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
