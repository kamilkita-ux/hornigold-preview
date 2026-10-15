import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const H = 'c98ead00-c7fd-4013-bb45-f19539b932d4';
const LANG = {pl: 'pl', en: 'en', de: 'de', uk: 'uk', es: 'es', it: 'it', 'zh-hans': 'en'};
const read = p => readFileSync(new URL('../site/' + p, import.meta.url), 'utf8');
const OLD_NOTICE = ['Rezerwacje online są obecnie niedostępne', 'Online booking is currently unavailable', 'Online-Buchungen sind derzeit nicht verfügbar',
  'Онлайн-бронювання наразі недоступне', 'Las reservas en línea no están disponibles', 'Le prenotazioni online non sono al momento disponibili', '本网站版暂不支持预订'];

const ALL_ROOMS = {pl: 'Zobacz wszystkie dostępne pokoje', en: 'See all available rooms', de: 'Alle verfügbaren Zimmer ansehen', uk: 'Переглянути всі доступні номери',
  es: 'Ver todas las habitaciones disponibles', it: 'Vedi tutte le camere disponibili', 'zh-hans': '查看所有可订房型'};

for (const [lang, engine] of Object.entries(LANG)) {
  test(`${lang} booking block has a hidden all-rooms link right after the button`, () => {
    const html = read(`${lang}/rezerwacja/index.html`);
    assert.equal(html.split('data-booking-all=""').length - 1, 1);
    assert.ok(html.includes(`</a></p><p hidden=""><a class="text-link" data-booking-all="" href="https://be.guestsage.com/${engine}/${H}">${ALL_ROOMS[lang]}</a></p><p>`),
      'the link must follow the booking button and stay hidden until booking.js narrows the button to one room');
  });
  test(`${lang} reservation page links to GuestSage without JavaScript`, () => {
    const html = read(`${lang}/rezerwacja/index.html`);
    const links = [...html.matchAll(/<a [^>]*data-booking=""[^>]*>/g)].map(m => m[0]);
    assert.equal(links.length, 1);
    assert.match(links[0], new RegExp(`href="https://be\\.guestsage\\.com/${engine}/${H}"`));
    assert.match(links[0], /class="button"/);
    for (const old of OLD_NOTICE) assert.ok(!html.includes(old), `old notice text left: ${old}`);
  });
  test(`${lang} booking block is a plain panel, not the status notice app.js writes into`, () => {
    const html = read(`${lang}/rezerwacja/index.html`);
    assert.match(html, /<div class="booking-panel"><h2>[^<]+<\/h2><p>[^<]+<\/p><p><a class="button" data-booking=""/);
    assert.ok(!html.includes('class="notice"'), 'a .notice would receive the "no valid dates" message from app.js');
  });
  test(`${lang} reservation page loads booking.js after app.js`, () => {
    const html = read(`${lang}/rezerwacja/index.html`);
    const app = html.indexOf('/assets/app.js'), booking = html.indexOf('<script defer="" src="/assets/booking.js"></script>');
    assert.ok(app > 0 && booking > app);
    assert.equal(html.split('/assets/booking.js').length - 1, 1);
  });
}

test('style.css styles the booking panel like the former notice', () => {
  const css = read('assets/style.css');
  assert.ok(css.includes('.booking-panel{padding:28px;background:var(--warm);border-left:3px solid var(--gold);margin-bottom:30px}'));
  assert.ok(css.includes('.booking-panel h2{font-size:1.9rem}'));
});

const HELP = {
  "pl": "Po wyborze pokoju przejdziesz do zewnętrznego systemu rezerwacji. Sprawdź tam dostępność, cenę końcową i warunki przed dokonaniem rezerwacji.",
  "en": "After choosing a room, you will continue to an external booking system. Check availability, the total price and terms there before making a reservation.",
  "de": "Nach der Zimmerwahl gelangen Sie zu einem externen Buchungssystem. Prüfen Sie dort Verfügbarkeit, Gesamtpreis und Bedingungen, bevor Sie buchen.",
  "uk": "Після вибору номера ви перейдете до зовнішньої системи бронювання. Перед бронюванням перевірте там доступність, загальну ціну та умови.",
  "es": "Tras elegir la habitación, pasarás a un sistema de reservas externo. Comprueba allí la disponibilidad, el precio total y las condiciones antes de reservar.",
  "it": "Dopo aver scelto la camera, passerai a un sistema di prenotazione esterno. Verifica disponibilità, prezzo totale e condizioni prima di prenotare.",
  "zh-hans": "选择房型后，您将进入外部预订系统。请在预订前核实可订情况、总价及相关条款。"
};
const unescape = s => s.replace(/&#x27;|&#39;/g, "'").replace(/&amp;/g, '&');
for (const lang of Object.keys(HELP)) for (const page of [`${lang}/index.html`, `${lang}/pobyt/index.html`]) {
  test(`${page} search form help describes external handoff and checks before reservation`, () => {
    const m = read(page).match(/<p class="form-help" id="date-help">(.*?)<\/p>/s);
    assert.ok(m, 'form-help missing');
    assert.equal(unescape(m[1]), HELP[lang]);
  });
}
