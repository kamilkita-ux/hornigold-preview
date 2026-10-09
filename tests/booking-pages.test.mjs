import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const H = 'c98ead00-c7fd-4013-bb45-f19539b932d4';
const LANG = {pl: 'pl', en: 'en', de: 'de', uk: 'uk', es: 'es', it: 'it', 'zh-hans': 'en'};
const read = p => readFileSync(new URL('../site/' + p, import.meta.url), 'utf8');
const OLD_NOTICE = ['Rezerwacje online są obecnie niedostępne', 'Online booking is currently unavailable', 'Online-Buchungen sind derzeit nicht verfügbar',
  'Онлайн-бронювання наразі недоступне', 'Las reservas en línea no están disponibles', 'Le prenotazioni online non sono al momento disponibili', '本网站版暂不支持预订'];

for (const [lang, engine] of Object.entries(LANG)) {
  test(`${lang} reservation page links to GuestSage without JavaScript`, () => {
    const html = read(`${lang}/rezerwacja/index.html`);
    const links = [...html.matchAll(/<a [^>]*data-booking[^>]*>/g)].map(m => m[0]);
    assert.equal(links.length, 1);
    assert.match(links[0], new RegExp(`href="https://be\\.guestsage\\.com/${engine}/${H}"`));
    assert.match(links[0], /class="button"/);
    for (const old of OLD_NOTICE) assert.ok(!html.includes(old), `old notice text left: ${old}`);
  });
  test(`${lang} reservation page loads booking.js after app.js`, () => {
    const html = read(`${lang}/rezerwacja/index.html`);
    const app = html.indexOf('/assets/app.js'), booking = html.indexOf('<script defer="" src="/assets/booking.js"></script>');
    assert.ok(app > 0 && booking > app);
    assert.equal(html.split('/assets/booking.js').length - 1, 1);
  });
}
