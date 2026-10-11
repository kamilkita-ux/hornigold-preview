"""Synthetic responses only: no network or production changes."""
import importlib.util
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
        self.assertIn('x-robots-tag: noindex', result['headers'])
        self.assertEqual(result['body'], 'body')

    def test_failed_tls_fails_all_checks(self):
        response = {'status': '200', 'headers': '', 'body': '{}', 'tlsVerified': False, 'curlExit': 60}
        with patch.object(monitor, 'request', return_value=response):
            rows = monitor.run_checks()
        self.assertEqual(len(rows), 10)
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
