import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../_cloudflare_production/server/production-entry.mjs';

// Atrapa assetów Cloudflare z domyślnym html_handling "auto-trailing-slash": /plik.html → 307 na /plik, /plik → treść pliku.
const FILE = 'google6078b276ecb15bd4';
const BODY = `google-site-verification: ${FILE}.html`;
const env = {ASSETS: {async fetch(request) {
  const path = new URL(request.url).pathname;
  if (path === `/${FILE}.html`) return new Response(null, {status: 307, headers: {Location: `/${FILE}`}});
  if (path === `/${FILE}`) return new Response(request.method === 'HEAD' ? null : BODY, {headers: {'Content-Type': 'text/html'}});
  return new Response('Missing', {status: 404});
}}};

test('plik weryfikacyjny Google odpowiada 200 pod dokładnym adresem .html', async () => {
  const r = await worker.fetch(new Request(`https://hornigold.pl/${FILE}.html`), env);
  assert.equal(r.status, 200);
  assert.equal(r.headers.get('Location'), null);
  assert.equal((await r.text()).trim(), BODY);
});

test('HEAD pliku weryfikacyjnego też 200', async () => {
  const r = await worker.fetch(new Request(`https://hornigold.pl/${FILE}.html`, {method: 'HEAD'}), env);
  assert.equal(r.status, 200);
});

test('nieistniejący plik google*.html nie dostaje 200', async () => {
  const r = await worker.fetch(new Request('https://hornigold.pl/google0000000000000000.html'), env);
  assert.notEqual(r.status, 200);
});

test('inne pliki .html nadal przechodzą zwykłą ścieżką', async () => {
  const r = await worker.fetch(new Request('https://hornigold.pl/pl/404.html'), env);
  assert.equal(r.status, 404);
});
