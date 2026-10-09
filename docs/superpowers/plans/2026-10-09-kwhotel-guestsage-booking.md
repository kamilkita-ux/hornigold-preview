# Rezerwacje przez KWHotel / GuestSage — plan wdrożenia

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Na 7 podstronach `rezerwacja/` przycisk „Sprawdź dostępność i zarezerwuj” prowadzi do hostowanego silnika GuestSage z datami i liczbą osób gościa.

**Architecture:** Statyczne strony w `site/<lang>/` (ręcznie pisany HTML) dostają blok rezerwacji z linkiem do strony głównej silnika; nowy skrypt `site/assets/booking.js` (własny, `script-src 'self'`) czyta `window.HornigoldStay` i podmienia `href` na adres `…/offers?arrivalDate&departureDate&personsCount`. Bez zmian CSP, `release.json` i audytów Kamila.

**Tech Stack:** HTML statyczny, JavaScript przeglądarkowy (IIFE, bez bundlera), `node:test` + `node:vm`, Python 3 (build/audyty Kamila w `.venv`), Cloudflare Workers (`wrangler`).

**Spec:** `docs/superpowers/specs/2026-10-09-kwhotel-guestsage-booking-design.md`

## Global Constraints

- Identyfikator hotelu: `c98ead00-c7fd-4013-bb45-f19539b932d4`; origin silnika: `https://be.guestsage.com`.
- Mapa języków strona → silnik: `pl→pl, en→en, de→de, uk→uk, es→es, it→it, zh-hans→en`; nieznany → `en`.
- Parametry `offers` tylko razem: `arrivalDate`, `departureDate` (YYYY-MM-DD), `personsCount` (1–6; brak → `2`, jak w `.stay-summary` w `app.js:45`).
- Bez zmian w: `server/worker.mjs` (CSP), `release.json`, `scripts/audit_*.py`, `legal/*`, `site/assets/messages/*.js`, `site/assets/app.js`, `site/assets/experience.js`.
- Folder `kwhotel/` NIE trafia do repozytorium (repo publiczne, dane kontaktowe dostawcy).
- Pliki LF (`core.autocrlf=false`); w Git Bash na Windows `export MSYS_NO_PATHCONV=1 PYTHONUTF8=1`.
- Pracujemy w `C:\dev\hornigold-cloudflare` na gałęzi `deploy/cloudflare`.

## Review Focus

- Grupa powyżej 6 osób wpisana w formularzu zapytania (`people` 8): `HornigoldStay` odrzuca wartość, link idzie z `personsCount=2`; strona kieruje grupy do formularza zapytania — test `guests '8' → personsCount 2` w Task 1.
- Nieaktualny wybór z `sessionStorage` (przyjazd wczoraj): link do strony głównej silnika, bez parametrów — test w Task 1.
- Nieprawidłowa data (`2026-02-30`, tekst): bez wyjątku, link do strony głównej silnika — test w Task 1.
- Strona poza katalogiem języka lub nieznany język: silnik po angielsku — test w Task 1.
- Wyłączony JavaScript: przycisk i tak prowadzi do silnika we właściwym języku (statyczny `href`) — test w Task 2.

## File Structure

- Create `site/assets/booking.js` — budowa adresu GuestSage i podmiana `href` linków `a[data-booking]`; eksport `bookingUrl` dla testów.
- Create `tests/booking.test.mjs` — testy jednostkowe `bookingUrl`.
- Create `tests/booking-pages.test.mjs` — testy statycznego HTML (7 podstron rezerwacji, 14 stron z formularzem pobytu).
- Create `scripts/kwhotel_booking_pages.py` — jednorazowa, idempotentna podmiana bloków HTML (dokumentuje zmianę dla Kamila).
- Modify `site/{pl,en,de,uk,es,it,zh-hans}/rezerwacja/index.html` — blok `.notice`, `.integration-limit`, `<script src="/assets/booking.js">`.
- Modify `site/{pl,en,de,uk,es,it,zh-hans}/index.html` i `site/*/pobyt/index.html` — `p#date-help.form-help`.
- Modify `docs/CLOUDFLARE.md`, spec (doprecyzowanie `personsCount` domyślnie 2).

---

### Task 1: `booking.js` — adres GuestSage

**Files:**
- Create: `site/assets/booking.js`
- Test: `tests/booking.test.mjs`

**Interfaces:**
- Consumes: `window.HornigoldStay.get()` z `site/assets/app.js:34` → `{arrival?, departure?, guests?, room?}` (już oczyszczone przez `clean()`).
- Produces: `bookingUrl(stay, pageLang, today?) → string`; w przeglądarce `window.HornigoldBooking = {bookingUrl, HOTEL, ORIGIN, LANG, ROOMS}`; w kontekście z `module` → `module.exports` (to samo API, bez dotykania DOM).

- [ ] **Step 1: Napisz test (failing)**

`tests/booking.test.mjs`:

```js
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

function load() {
  const code = readFileSync(new URL('../site/assets/booking.js', import.meta.url), 'utf8');
  const sandbox = {module: {exports: {}}, URLSearchParams, Intl, Date};
  vm.runInNewContext(code, sandbox);
  return sandbox.module.exports;
}
const B = load();
const BASE = 'https://be.guestsage.com';
const H = 'c98ead00-c7fd-4013-bb45-f19539b932d4';
const TODAY = '2026-10-09';

test('valid stay produces offers URL with three parameters', () => {
  assert.equal(B.bookingUrl({arrival: '2026-10-20', departure: '2026-10-22', guests: '3'}, 'pl', TODAY),
    `${BASE}/pl/${H}/offers?arrivalDate=2026-10-20&departureDate=2026-10-22&personsCount=3`);
});
test('missing guests defaults to 2 like the stay summary', () => {
  assert.equal(B.bookingUrl({arrival: '2026-10-20', departure: '2026-10-21'}, 'de', TODAY),
    `${BASE}/de/${H}/offers?arrivalDate=2026-10-20&departureDate=2026-10-21&personsCount=2`);
});
test('more than 6 guests falls back to 2', () => {
  assert.match(B.bookingUrl({arrival: '2026-10-20', departure: '2026-10-21', guests: '8'}, 'pl', TODAY), /personsCount=2$/);
});
test('no dates gives engine home in page language', () => {
  assert.equal(B.bookingUrl({}, 'uk', TODAY), `${BASE}/uk/${H}`);
  assert.equal(B.bookingUrl(undefined, 'es', TODAY), `${BASE}/es/${H}`);
});
test('arrival in the past gives engine home', () => {
  assert.equal(B.bookingUrl({arrival: '2026-10-08', departure: '2026-10-10', guests: '2'}, 'pl', TODAY), `${BASE}/pl/${H}`);
});
test('departure not after arrival gives engine home', () => {
  assert.equal(B.bookingUrl({arrival: '2026-10-20', departure: '2026-10-20'}, 'it', TODAY), `${BASE}/it/${H}`);
});
test('invalid dates never throw and give engine home', () => {
  assert.equal(B.bookingUrl({arrival: '2026-02-30', departure: '2026-03-02'}, 'pl', '2026-01-01'), `${BASE}/pl/${H}`);
  assert.equal(B.bookingUrl({arrival: 'jutro', departure: 'pojutrze'}, 'pl', TODAY), `${BASE}/pl/${H}`);
});
test('chinese and unknown languages open the engine in English', () => {
  assert.equal(B.bookingUrl({}, 'zh-hans', TODAY), `${BASE}/en/${H}`);
  assert.equal(B.bookingUrl({}, '', TODAY), `${BASE}/en/${H}`);
  assert.equal(B.bookingUrl({}, 'api', TODAY), `${BASE}/en/${H}`);
});
test('room mapping adds featuredRoomTypeId only when configured', () => {
  const stay = {arrival: '2026-10-20', departure: '2026-10-21', guests: '2', room: 'classic'};
  assert.doesNotMatch(B.bookingUrl(stay, 'pl', TODAY), /featuredRoomTypeId/);
  B.ROOMS.classic = 8739;
  try { assert.match(B.bookingUrl(stay, 'pl', TODAY), /&featuredRoomTypeId=8739$/); }
  finally { delete B.ROOMS.classic; }
});
```

- [ ] **Step 2: Uruchom test — ma paść**

Run: `node --test tests/booking.test.mjs`
Expected: FAIL — `ENOENT … site/assets/booking.js`.

- [ ] **Step 3: Implementacja**

`site/assets/booking.js`:

```js
// Rezerwacje przez GuestSage AI Booking Engine (KWHotel) — przekazanie linkiem.
// Spec: docs/superpowers/specs/2026-10-09-kwhotel-guestsage-booking-design.md
(function (root) {
  'use strict';
  const HOTEL = 'c98ead00-c7fd-4013-bb45-f19539b932d4';
  const ORIGIN = 'https://be.guestsage.com';
  // Silnik nie ma chińskiego; obsługiwane m.in. pl, en, de, uk, es, it.
  const LANG = {pl: 'pl', en: 'en', de: 'de', uk: 'uk', es: 'es', it: 'it', 'zh-hans': 'en'};
  // Slug pokoju (app.js roomNames) -> featuredRoomTypeId z panelu KWHotel. Uzupełnić po otrzymaniu ID.
  const ROOMS = {};
  const validDate = v => /^\d{4}-\d{2}-\d{2}$/.test(v || '') && !isNaN(Date.parse(v)) && new Date(v + 'T12:00:00Z').toISOString().slice(0, 10) === v;
  const todayWarsaw = () => new Intl.DateTimeFormat('sv-SE', {timeZone: 'Europe/Warsaw'}).format(new Date());

  function bookingUrl(stay, pageLang, today) {
    const base = ORIGIN + '/' + (Object.hasOwn(LANG, pageLang) ? LANG[pageLang] : 'en') + '/' + HOTEL;
    const s = stay || {};
    const day = today || todayWarsaw();
    if (!validDate(s.arrival) || s.arrival < day || !validDate(s.departure) || s.departure <= s.arrival) return base;
    const q = new URLSearchParams({
      arrivalDate: s.arrival,
      departureDate: s.departure,
      personsCount: /^[1-6]$/.test(String(s.guests || '')) ? String(s.guests) : '2',
    });
    if (Object.hasOwn(ROOMS, s.room)) q.set('featuredRoomTypeId', String(ROOMS[s.room]));
    return base + '/offers?' + q.toString();
  }

  const api = {bookingUrl, HOTEL, ORIGIN, LANG, ROOMS};
  if (typeof module === 'object' && module && module.exports) { module.exports = api; return; }
  root.HornigoldBooking = api;
  if (!document.querySelector('a[data-booking]')) return;
  const pageLang = location.pathname.split('/')[1] || '';
  function refresh() {
    const stay = root.HornigoldStay ? root.HornigoldStay.get() : {};
    const url = bookingUrl(stay, pageLang);
    document.querySelectorAll('a[data-booking]').forEach(a => { a.href = url; });
  }
  refresh();
  // Formularze strony aktualizują HornigoldStay w swoich listenerach; dokument dostaje zdarzenie później.
  document.addEventListener('input', refresh);
  document.addEventListener('change', refresh);
})(typeof window !== 'undefined' ? window : globalThis);
```

- [ ] **Step 4: Uruchom test — ma przejść**

Run: `node --test tests/booking.test.mjs`
Expected: PASS, `ℹ tests 9`, `ℹ fail 0`.

- [ ] **Step 5: Commit**

```bash
git add site/assets/booking.js tests/booking.test.mjs
git commit -m "feat(booking): adres GuestSage z wyboru pobytu (booking.js)"
```

---

### Task 2: Podstrony `rezerwacja/` w 7 językach

**Files:**
- Create: `scripts/kwhotel_booking_pages.py`
- Modify: `site/{pl,en,de,uk,es,it,zh-hans}/rezerwacja/index.html`
- Test: `tests/booking-pages.test.mjs`

**Interfaces:**
- Consumes: `site/assets/booking.js` (Task 1) — szuka `a[data-booking]`.
- Produces: na każdej podstronie `div.notice[role=status]` z `a.button[data-booking]`, `href` = `https://be.guestsage.com/{LANG[lang]}/c98ead00-c7fd-4013-bb45-f19539b932d4`; `<script defer="" src="/assets/booking.js"></script>` bezpośrednio po skrypcie `experience.js`.

- [ ] **Step 1: Napisz test (failing)**

`tests/booking-pages.test.mjs`:

```js
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
```

- [ ] **Step 2: Uruchom test — ma paść**

Run: `node --test tests/booking-pages.test.mjs`
Expected: FAIL (`links.length` 0).

- [ ] **Step 3: Skrypt podmiany**

`scripts/kwhotel_booking_pages.py`:

```python
"""Jednorazowa podmiana bloków rezerwacji na podstronach (KWHotel/GuestSage, 2026-10-09). Idempotentny."""
from pathlib import Path
import re, sys
ROOT = Path(__file__).resolve().parent.parent
HOTEL = 'c98ead00-c7fd-4013-bb45-f19539b932d4'
LANG = {'pl': 'pl', 'en': 'en', 'de': 'de', 'uk': 'uk', 'es': 'es', 'it': 'it', 'zh-hans': 'en'}
TEXT = {
 'pl': ('Zarezerwuj online', 'Dostępność, cenę i warunki zobaczysz w systemie rezerwacyjnym hotelu (KWHotel / GuestSage). Tam zakończysz rezerwację i płatność oraz zawrzesz umowę na warunkach hotelu.', 'Sprawdź dostępność i zarezerwuj', 'Dla grup powyżej 6 osób i zapytań firmowych skorzystaj z formularza zapytania poniżej.', 'Przycisk otwiera system rezerwacyjny hotelu w języku polskim.'),
 'en': ('Book online', "You will see availability, rates and terms in the hotel's booking system (KWHotel / GuestSage). That is where you complete the booking and payment and conclude the contract on the hotel's terms.", 'Check availability and book', 'For groups of more than 6 people and business enquiries, use the enquiry form below.', "The button opens the hotel's booking system in English."),
 'de': ('Online buchen', 'Verfügbarkeit, Preise und Bedingungen sehen Sie im Buchungssystem des Hotels (KWHotel / GuestSage). Dort schließen Sie Buchung und Zahlung ab; der Vertrag kommt zu den Bedingungen des Hotels zustande.', 'Verfügbarkeit prüfen und buchen', 'Für Gruppen über 6 Personen und Firmenanfragen nutzen Sie bitte das Anfrageformular unten.', 'Die Schaltfläche öffnet das Buchungssystem des Hotels auf Deutsch.'),
 'uk': ('Забронювати онлайн', 'Наявність, ціни та умови ви побачите в системі бронювання готелю (KWHotel / GuestSage). Там ви завершите бронювання й оплату та укладете договір на умовах готелю.', 'Перевірити наявність і забронювати', 'Для груп понад 6 осіб і корпоративних запитів скористайтеся формою запиту нижче.', 'Кнопка відкриває систему бронювання готелю українською мовою.'),
 'es': ('Reserva en línea', 'Verás la disponibilidad, las tarifas y las condiciones en el sistema de reservas del hotel (KWHotel / GuestSage). Allí completarás la reserva y el pago y celebrarás el contrato según las condiciones del hotel.', 'Consultar disponibilidad y reservar', 'Para grupos de más de 6 personas y consultas de empresa, utiliza el formulario de consulta de abajo.', 'El botón abre el sistema de reservas del hotel en español.'),
 'it': ('Prenota online', "Disponibilità, prezzi e condizioni sono indicati nel sistema di prenotazione dell'hotel (KWHotel / GuestSage). Lì completerai prenotazione e pagamento e concluderai il contratto alle condizioni dell'hotel.", 'Verifica disponibilità e prenota', 'Per gruppi di oltre 6 persone e richieste aziendali, usa il modulo di richiesta qui sotto.', "Il pulsante apre il sistema di prenotazione dell'hotel in italiano."),
 'zh-hans': ('在线预订', '空房、价格和条款将在酒店预订系统（KWHotel / GuestSage）中显示。您将在该系统中完成预订和付款，并按酒店条款订立合同。', '查询空房并预订', '6人以上团体及企业咨询，请使用下方的咨询表单。', '预订系统暂无中文版本，按钮将以英文打开预订系统。'),
}
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
SCRIPT = '<script defer="" src="/assets/booking.js"></script>'
def one(pattern, repl, html, name):
    new, n = re.subn(pattern, lambda m: repl, html, count=1, flags=re.S)
    if n != 1: sys.exit(f'{name}: oczekiwano 1 dopasowania, jest {n}')
    return new
for lang, engine in LANG.items():
    p = ROOT / 'site' / lang / 'rezerwacja' / 'index.html'
    html = p.read_text(encoding='utf-8')
    if 'data-booking' in html: print(lang, 'już zmienione'); continue
    h2, lead, button, groups, limit = (esc(x) for x in TEXT[lang])
    notice = (f'<div class="notice" role="status"><h2>{h2}</h2><p>{lead}</p>'
              f'<p><a class="button" data-booking="" href="https://be.guestsage.com/{engine}/{HOTEL}">{button}</a></p>'
              f'<p>{groups}</p></div>')
    html = one(r'<div class="notice" role="status">.*?</div>', notice, html, f'{lang} notice')
    html = one(r'<div class="integration-limit">.*?</div>', f'<div class="integration-limit"><p>{limit}</p></div>', html, f'{lang} limit')
    m = re.search(r'<script defer="" src="/assets/experience\.js[^"]*"></script>', html)
    if not m: sys.exit(f'{lang}: brak skryptu experience.js')
    html = html[:m.end()] + SCRIPT + html[m.end():]
    p.write_text(html, encoding='utf-8', newline='\n')
    print(lang, 'ok')
```

Uwaga: `site/` zawiera pliki źródłowe bez `?v=` — `build.py` dopisze wersję do `booking.js` sam (`scripts/build.py` blok „asset cache-busting”). Jeśli w źródle `experience.js` ma już `?v=`, wzorzec `[^"]*` to obejmuje.

- [ ] **Step 4: Uruchom skrypt i test**

Run: `.venv/Scripts/python scripts/kwhotel_booking_pages.py && node --test tests/booking-pages.test.mjs`
Expected: 7× `ok`, potem PASS `ℹ tests 14`, `ℹ fail 0`. Drugie uruchomienie skryptu: 7× `już zmienione`.

- [ ] **Step 5: Commit**

```bash
git add scripts/kwhotel_booking_pages.py tests/booking-pages.test.mjs site/*/rezerwacja/index.html
git commit -m "feat(booking): blok rezerwacji GuestSage na podstronach rezerwacja/ (7 języków)"
```

---

### Task 3: Tekst pomocy przy formularzach pobytu (14 stron)

**Files:**
- Modify: `scripts/kwhotel_booking_pages.py` (druga sekcja)
- Modify: `site/{pl,en,de,uk,es,it,zh-hans}/index.html`, `site/{…}/pobyt/index.html`
- Test: `tests/booking-pages.test.mjs` (dopisane testy)

**Interfaces:**
- Consumes: nic z poprzednich tasków.
- Produces: `p#date-help.form-help` zostaje (wymaga go `scripts/audit_static.py:35`), nowa treść.

- [ ] **Step 1: Dopisz test (failing)** na końcu `tests/booking-pages.test.mjs`:

```js
const HELP = {
  pl: 'Po wyborze pokoju rezerwację i płatność zakończysz w systemie rezerwacyjnym hotelu.',
  en: "After choosing a room, you complete the booking and payment in the hotel's booking system.",
  de: 'Nach der Zimmerwahl schließen Sie Buchung und Zahlung im Buchungssystem des Hotels ab.',
  uk: 'Після вибору номера ви завершите бронювання й оплату в системі бронювання готелю.',
  es: 'Tras elegir la habitación, completarás la reserva y el pago en el sistema de reservas del hotel.',
  it: "Dopo aver scelto la camera, completerai prenotazione e pagamento nel sistema di prenotazione dell'hotel.",
  'zh-hans': '选定房型后，您将在酒店预订系统中完成预订和付款。',
};
const unescape = s => s.replace(/&#x27;|&#39;/g, "'").replace(/&amp;/g, '&');
for (const lang of Object.keys(HELP)) for (const page of [`${lang}/index.html`, `${lang}/pobyt/index.html`]) {
  test(`${page} search form help describes booking in the hotel system`, () => {
    const m = read(page).match(/<p class="form-help" id="date-help">(.*?)<\/p>/s);
    assert.ok(m, 'form-help missing');
    assert.equal(unescape(m[1]), HELP[lang]);
  });
}
```

- [ ] **Step 2: Uruchom — ma paść**

Run: `node --test tests/booking-pages.test.mjs`
Expected: 14 nowych testów FAIL (stara treść).

- [ ] **Step 3: Dopisz sekcję do skryptu** (na końcu `scripts/kwhotel_booking_pages.py`):

```python
HELP = {
 'pl': 'Po wyborze pokoju rezerwację i płatność zakończysz w systemie rezerwacyjnym hotelu.',
 'en': "After choosing a room, you complete the booking and payment in the hotel's booking system.",
 'de': 'Nach der Zimmerwahl schließen Sie Buchung und Zahlung im Buchungssystem des Hotels ab.',
 'uk': 'Після вибору номера ви завершите бронювання й оплату в системі бронювання готелю.',
 'es': 'Tras elegir la habitación, completarás la reserva y el pago en el sistema de reservas del hotel.',
 'it': "Dopo aver scelto la camera, completerai prenotazione e pagamento nel sistema di prenotazione dell'hotel.",
 'zh-hans': '选定房型后，您将在酒店预订系统中完成预订和付款。',
}
for lang, text in HELP.items():
    for rel in (f'{lang}/index.html', f'{lang}/pobyt/index.html'):
        p = ROOT / 'site' / rel
        html = p.read_text(encoding='utf-8')
        html = one(r'<p class="form-help" id="date-help">.*?</p>', f'<p class="form-help" id="date-help">{esc(text)}</p>', html, rel)
        p.write_text(html, encoding='utf-8', newline='\n')
        print(rel, 'ok')
```

(Ta sekcja jest idempotentna — zawsze zapisuje tę samą treść.)

- [ ] **Step 4: Uruchom skrypt i testy**

Run: `.venv/Scripts/python scripts/kwhotel_booking_pages.py && node --test tests/booking.test.mjs tests/booking-pages.test.mjs`
Expected: PASS, `ℹ tests 37`, `ℹ fail 0`.

- [ ] **Step 5: Commit**

```bash
git add scripts/kwhotel_booking_pages.py tests/booking-pages.test.mjs site/*/index.html site/*/pobyt/index.html
git commit -m "feat(booking): tekst pomocy formularza pobytu — rezerwacja w systemie hotelu (7 języków)"
```

---

### Task 4: Build, audyty, wdrożenie, odbiór

**Files:**
- Modify: `docs/CLOUDFLARE.md`, `docs/superpowers/specs/2026-10-09-kwhotel-guestsage-booking-design.md`

**Interfaces:**
- Consumes: Task 1–3.
- Produces: Worker `hornigold` z nową wersją, wpis w runbooku.

- [ ] **Step 1: Build i audyty** (Git Bash, `C:\dev\hornigold-cloudflare`)

```sh
export MSYS_NO_PATHCONV=1 PYTHONUTF8=1 GITHUB_SHA=$(git rev-parse HEAD); P=.venv/Scripts/python
$P scripts/build.py --base / --counter          # podgląd (_site) — tylko dla audit_static
$P scripts/audit_static.py --base /
$P scripts/build.py --mode production-ready --base / --counter --production-counter
$P scripts/audit_seo.py --mode production-ready
$P scripts/audit_discovery.py --mode production-ready
$P scripts/prepare_cloudflare_production.py
node --test tests/production-indexing.test.mjs tests/server.test.mjs tests/booking.test.mjs tests/booking-pages.test.mjs
$P -m unittest discover -s tests -p 'test_seo*.py'
grep -c 'assets/booking.js?v=' _cloudflare_production/assets/pl/rezerwacja/index.html
git checkout -- docs/seo/   # raporty audytów nie są częścią zmiany
```

Expected: oba buildy `"errors": 0`, 693 stron; `audit_static`, `audit_seo`, `audit_discovery` bez `errors`; wszystkie testy node PASS (`fail 0`) i `OK` z unittest; `grep` → `1`.

- [ ] **Step 2: Wdrożenie**

Run: `npx wrangler deploy --config C:/dev/hornigold-cloudflare/wrangler.jsonc`
Expected: `Current Version ID: …` (zapisać; poprzednia wersja do rollbacku: `576f78bb-82b4-44eb-b206-c9574a250fd0`).

- [ ] **Step 3: Odbiór na produkcji**

```sh
H=c98ead00-c7fd-4013-bb45-f19539b932d4
for l in pl:pl en:en de:de uk:uk es:es it:it zh-hans:en; do p=${l%%:*}; e=${l##*:}
  html=$(curl -s https://hornigold.pl/$p/rezerwacja/)
  echo "$p $(curl -s -o /dev/null -w '%{http_code}' https://hornigold.pl/$p/rezerwacja/) link=$(echo "$html" | grep -c "be.guestsage.com/$e/$H") js=$(echo "$html" | grep -c 'assets/booking.js')"
done
curl -s -o /dev/null -w 'booking.js %{http_code}\n' https://hornigold.pl/assets/booking.js
curl -sI https://hornigold.pl/pl/rezerwacja/ | grep -i content-security-policy
curl -s -o /dev/null -w 'engine offers %{http_code}\n' "https://be.guestsage.com/pl/$H/offers?arrivalDate=2026-11-10&departureDate=2026-11-12&personsCount=2"
```

Expected: 7× `200 link=1 js=1`; `booking.js 200`; CSP identyczny jak przed zmianą (`script-src 'self'`); silnik 200. Ręcznie w przeglądarce (Marek): wybór dat na `/pl/` → pokój → „Sprawdź dostępność i zarezerwuj” → GuestSage z tymi datami.

- [ ] **Step 4: Dokumentacja**

Dopisać w `docs/CLOUDFLARE.md` sekcję „Rezerwacje GuestSage (9 października 2026 r.)”: Worker, link do specu i planu, zakres etapu Kamila. W specu w „Zachowanie” pkt 3 zmienić „`guests` ≥ 1” na „`personsCount` = `guests` (1–6), brak → 2 jak w `.stay-summary`”.

- [ ] **Step 5: Commit**

```bash
git add docs/CLOUDFLARE.md docs/superpowers/specs/2026-10-09-kwhotel-guestsage-booking-design.md docs/superpowers/plans/2026-10-09-kwhotel-guestsage-booking.md
git commit -m "docs: rezerwacje GuestSage — wdrożenie i odbiór"
```
