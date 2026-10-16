import {mkdir, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {redirects} from '../server/routes.mjs';
import {pageTargets, portfolioTargets} from '../server/legacy-wordpress-redirects.mjs';

const root = resolve(import.meta.dirname, '..');
const output = resolve(root, 'docs/seo/URL_MIGRATION_TABLE.csv');
const rows = [['source_url', 'source', 'classification', 'action', 'destination_or_response', 'implementation_state', 'notes']];
const add = row => rows.push(row.map(value => `"${String(value).replaceAll('"', '""')}"`));

for (const [oldPath, destination] of Object.entries(redirects)) {
  add([`https://hornigold.pl${oldPath}`, 'server/routes.mjs', 'known historical path', '301', `https://hornigold.pl${destination}`, 'existing application rule', 'Canonical language/path equivalent']);
}
for (const [slug, destination] of Object.entries(portfolioTargets)) {
  add([`https://hornigold.pl/?portfolio-item=${encodeURIComponent(slug)}`, 'migration-map.json', 'known WordPress portfolio URL', '301', `https://hornigold.pl${destination}`, 'prepared locally', 'Closest confirmed room category']);
}
for (const [key, destination] of Object.entries(pageTargets)) {
  const [pageId, language] = key.split(':');
  const query = new URLSearchParams({page_id: pageId});
  if (language) query.set('lang', language);
  add([`https://hornigold.pl/?${query}`, 'migration-map.json / legacy-migration.json', 'known WordPress page URL', '301', `https://hornigold.pl${destination}`, 'prepared locally', 'Closest confirmed content equivalent']);
}
for (const pageId of ['6647', '6642', '6637', '6574', '5977', '5906']) {
  add([`https://hornigold.pl/?page_id=${pageId}`, 'migration-map.json', 'retired WordPress URL without equivalent', '410', 'Gone + X-Robots-Tag noindex', 'prepared locally', 'Do not redirect unrelated content to home page']);
}
for (const host of ['apartamenty.hornigold.pl', 'hornigold.com.pl', 'hotel-hornigold.com.pl', 'hotel-hornigold.pl', 'zielona-kamienica.hornigold.pl']) {
  add([`https://${host}/`, 'DNS/public audit 2026-10-16', 'alias or historic host', 'hold', 'No redirect configured', 'requires owner decision', 'Do not restore DNS or mass-redirect without historic URL evidence']);
}
add(['Google Search Console: 1,200 historical 404 URLs', 'Search Console report updated 2026-10-12', 'unknown historic URLs', 'review individually or retain 404/410', 'No universal destination', 'pending URL export/log evidence', 'Do not use a blanket redirect to the home page']);

await mkdir(dirname(output), {recursive: true});
await writeFile(output, `${rows.map(row => row.join(',')).join('\n')}\n`);
console.log(JSON.stringify({output, rows: rows.length - 1}));
