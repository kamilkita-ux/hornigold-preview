// Strona "/" tylko przekierowuje do zapamiętanego języka. Nic na niej nie może być widać, zanim skrypt zadziała:
// odnośnik zapasowy jest dla przeglądarek bez JavaScriptu, a skrypt ma ruszyć przed pierwszym malowaniem.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const html = readFileSync(new URL('../site/index.html', import.meta.url), 'utf8');

test('root page shows nothing to a browser with JavaScript', () => {
  const body = html.match(/<body[^>]*>(.*)<\/body>/s)?.[1];
  assert.ok(body !== undefined, 'body missing');
  assert.equal(body.replace(/<noscript>.*?<\/noscript>/gs, '').trim(), '');
});
test('root page keeps a plain link for browsers without JavaScript', () => {
  assert.match(html, /<body><noscript><a href="\/pl\/">Polski<\/a><\/noscript><\/body>/);
});
test('root language script runs before the first paint', () => {
  const script = html.match(/<head>.*?(<script[^>]*root-language\.js[^>]*>)<\/script>.*?<\/head>/s)?.[1];
  assert.ok(script, 'root-language.js must be loaded in <head>');
  assert.doesNotMatch(script, /\b(defer|async)\b/, 'a deferred script lets the browser paint the page first');
});
test('root page stays out of search results', () => {
  assert.match(html, /<meta content="noindex,nofollow,noarchive" name="robots"\/>/);
});
