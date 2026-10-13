"""Synthetic responses only: no network or production changes."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('monitor_public', Path(__file__).resolve().parents[1] / 'scripts/monitor_public.py')
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class MonitorPublicTests(unittest.TestCase):
    def fetch(self, stdout, code=0, url='https://example.invalid/'):
        with patch.object(monitor.subprocess, 'run', return_value=SimpleNamespace(stdout=stdout, returncode=code)) as run:
            result = monitor.request(url)
            self.assertNotIn('--insecure', run.call_args.args[0])
            return result

    def check_response(self, name, url, response):
        default = {'status': '200', 'headers': '', 'body': '{}', 'tlsVerified': True, 'curlExit': 0}
        with patch.object(monitor, 'request', side_effect=lambda requested: response if requested == url else default) as request:
            rows = monitor.run_checks()
        return next(row for row in rows if row['name'] == name), request

    def test_certificate_failure_is_not_verified_tls(self):
        result = self.fetch('\n000', 60)
        self.assertFalse(result['tlsVerified'])
        self.assertEqual(result['curlExit'], 60)

    def test_transport_failure_cannot_pass_with_partial_http_200(self):
        self.assertFalse(self.fetch('HTTP/2 200\n\npartial\n200', 28)['tlsVerified'])

    def test_valid_https_and_http_error_distinguished(self):
        self.assertTrue(self.fetch('HTTP/2 200\n\nok\n200')['tlsVerified'])
        self.assertTrue(self.fetch('HTTP/2 403\n\nforbidden\n403')['tlsVerified'])
        self.assertFalse(self.fetch('HTTP/1.1 200\n\nok\n200', url='http://example.invalid/')['tlsVerified'])

    def test_proxy_headers_do_not_hide_server_headers(self):
        result = self.fetch('HTTP/1.1 200 Connection established\r\n\r\nHTTP/2 200\r\nX-Robots-Tag: noindex\r\n\r\nbody\n200')
        self.assertEqual(monitor.header_values(result, 'x-robots-tag'), ['noindex'])
        self.assertEqual(result['body'], 'body')

    def test_location_preserves_case_sensitive_path_and_query(self):
        location = 'https://hornigold.pl/PL/?Promo=AbC'
        result = self.fetch('HTTP/2 301\nLoCaTiOn: ' + location + '\n\n\n301')
        self.assertEqual(monitor.header_values(result, 'LOCATION'), [location])

    def test_www_requires_exact_location(self):
        for location in ['https://hornigold.pl/pl/', 'https://hornigold.pl/PL/', 'https://hornigold.pl/pl/extra', 'https://hornigold.pl/pl/?unexpected=1']:
            with self.subTest(location=location):
                response = {'status': '301', 'headers': 'LoCaTiOn: ' + location, 'body': '', 'tlsVerified': True, 'curlExit': 0}
                row, _ = self.check_response('www301', 'https://www.hornigold.pl/pl/', response)
                self.assertEqual(row['ok'], location == 'https://hornigold.pl/pl/')

    def test_root_redirect_requires_301_tls_and_unchanged_utm(self):
        query = 'utm_source=monitor&utm_medium=health&utm_campaign=RootCase'
        expected = 'https://hornigold.pl/pl/?' + query
        cases = [('301', expected, True, True), ('302', expected, True, False), ('301', expected, False, False),
                 ('301', 'https://hornigold.pl/pl/', True, False), ('301', expected.lower(), True, False)]
        for status, location, tls, ok in cases:
            with self.subTest(status=status, location=location, tls=tls):
                response = {'status': status, 'headers': 'Location: ' + location, 'body': '', 'tlsVerified': tls, 'curlExit': 0 if tls else 60}
                row, _ = self.check_response('root301_utm', 'https://hornigold.pl/?' + query, response)
                self.assertEqual(row['ok'], ok)

    def test_counter_accepts_valid_aggregate_without_posting(self):
        url = 'https://hornigold.pl/api/site-stats'
        response = {'status': '200', 'headers': '', 'body': json.dumps({'total': 0, 'startedAt': '2026-10-05', 'metric': 'pageviews'}), 'tlsVerified': True, 'curlExit': 0}
        row, request = self.check_response('counter', url, response)
        self.assertTrue(row['ok'])
        request.assert_any_call(url)
        with patch.object(monitor.subprocess, 'run', return_value=SimpleNamespace(stdout='HTTP/2 200\n\n{}\n200', returncode=0)) as curl:
            monitor.request(url)
        command = curl.call_args.args[0]
        self.assertEqual(command[-1], url)
        self.assertNotIn('POST', command)
        self.assertNotIn('--data', command)

    def test_counter_rejects_invalid_json_and_unusable_data(self):
        bodies = ['not JSON', '[]', 'null', '{}', '{"error":"counter_unavailable"}',
                  json.dumps({'total': True, 'startedAt': '2026-10-05', 'metric': 'pageviews'}),
                  json.dumps({'total': -1, 'startedAt': '2026-10-05', 'metric': 'pageviews'}),
                  json.dumps({'total': 1, 'startedAt': '2026-02-30', 'metric': 'pageviews'})]
        for body in bodies:
            with self.subTest(body=body):
                response = {'status': '200', 'headers': '', 'body': body, 'tlsVerified': True, 'curlExit': 0}
                row, _ = self.check_response('counter', 'https://hornigold.pl/api/site-stats', response)
                self.assertFalse(row['ok'])

    def test_counter_rejects_transport_or_http_failure_with_valid_body(self):
        body = json.dumps({'total': 10, 'startedAt': '2026-10-05', 'metric': 'pageviews'})
        for status, tls, curl_exit in [('200', False, 60), ('503', True, 0)]:
            with self.subTest(status=status, tls=tls):
                response = {'status': status, 'headers': '', 'body': body, 'tlsVerified': tls, 'curlExit': curl_exit}
                row, _ = self.check_response('counter', 'https://hornigold.pl/api/site-stats', response)
                self.assertFalse(row['ok'])

    def test_failed_tls_fails_all_checks(self):
        response = {'status': '200', 'headers': '', 'body': '{}', 'tlsVerified': False, 'curlExit': 60}
        with patch.object(monitor, 'request', return_value=response):
            rows = monitor.run_checks()
        self.assertEqual(len(rows), 12)
        self.assertFalse(any(x['ok'] for x in rows))

    def test_self_test_is_offline(self):
        with patch.object(monitor, 'request', side_effect=AssertionError('network not allowed')):
            rows = monitor.run_checks(True)
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]['ok'])

    def test_html_noindex_fails_production_route_checks(self):
        response = {'status': '200', 'headers': '', 'body': '<META CONTENT="NOINDEX,follow" NAME="robots">', 'tlsVerified': True, 'curlExit': 0}
        with patch.object(monitor, 'request', return_value=response):
            rows = monitor.run_checks()
        self.assertTrue(all(not row['ok'] and row['detail']['indexingBlocked'] for row in rows[:5]))

    def test_approved_transactional_noindex_is_required_for_new_release(self):
        for reservation_blocked in (True, False):
            def respond(url):
                body = '{}'
                if url.endswith('/release.json'):
                    body = '{"revision":"23.20","audit3ImprovementsDate":"2026-10-13"}'
                elif url.endswith('/pl/rezerwacja/') and reservation_blocked:
                    body = '<meta name="robots" content="noindex,follow">'
                return {'status':'200','headers':'','body':body,'tlsVerified':True,'curlExit':0}
            with self.subTest(reservation_blocked=reservation_blocked), patch.object(monitor, 'request', side_effect=respond):
                rows = monitor.run_checks()
                self.assertTrue(all(row['ok'] for row in rows[:4]))
                self.assertEqual(rows[4]['ok'], reservation_blocked)
                self.assertTrue(rows[4]['detail']['expectedNoindex'])

    def test_crawler_directives_and_none_are_detected(self):
        for headers, body in [
            ('X-Robots-Tag: googlebot: noindex, follow', ''),
            ('x-robots-tag: noarchive\nx-robots-tag: none', ''),
            ('', '<meta name="googlebot" content="none">'),
            ('', '<meta name="robots" content="no&#105;ndex">'),
        ]:
            with self.subTest(headers=headers, body=body):
                self.assertTrue(monitor.indexing_blocked({'headers': headers, 'body': body}))

    def test_visible_words_and_nonblocking_directives_do_not_fail(self):
        self.assertFalse(monitor.indexing_blocked({'headers': 'x-robots-tag: noarchive', 'body': '<meta name="robots" content="index,follow"><p>noindex none</p>'}))


if __name__ == '__main__':
    unittest.main()
