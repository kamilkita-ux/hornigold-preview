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
test('page language is the first known language segment, also under a non-root base', () => {
  assert.equal(B.pageLanguage('/pl/rezerwacja/'), 'pl');
  assert.equal(B.pageLanguage('/hornigold-preview/de/rezerwacja/'), 'de');
  assert.equal(B.pageLanguage('/hornigold-preview/zh-hans/rezerwacja/'), 'zh-hans');
  assert.equal(B.pageLanguage('/hornigold-preview/'), '');
  assert.equal(B.pageLanguage('/'), '');
});
const STAY = {arrival: '2026-10-20', departure: '2026-10-21', guests: '2'};
test('rooms sold in the booking engine are passed as featuredRoomTypeId', () => {
  const ids = {classic: 4830, deluxe: 4828, premium: 4834, 'deluxe-premium': 4836, suite: 4833, 'prestige-deluxe': 4835};
  assert.deepEqual(Object.fromEntries(Object.entries(B.ROOMS)), ids);
  for (const [room, id] of Object.entries(ids)) assert.match(B.bookingUrl({...STAY, room}, 'pl', TODAY), new RegExp(`&featuredRoomTypeId=${id}$`));
});
test('rooms without an online offer open the engine with all rooms', () => {
  for (const room of ['apartament-deluxe', 'prestige', 'hornigold', 'nieznany', 'constructor']) assert.doesNotMatch(B.bookingUrl({...STAY, room}, 'pl', TODAY), /featuredRoomTypeId/);
});
test('a room without valid dates gives engine home', () => {
  assert.equal(B.bookingUrl({room: 'classic'}, 'pl', TODAY), `${BASE}/pl/${H}`);
});

// Część przeglądarkowa: atrapa dokumentu z przyciskiem rezerwacji i odnośnikiem „wszystkie pokoje”.
function page(stay, pathname = '/pl/rezerwacja/') {
  const code = readFileSync(new URL('../site/assets/booking.js', import.meta.url), 'utf8');
  const main = {href: ''}, all = {href: '', parentElement: {hidden: true}};
  const listeners = {};
  const sandbox = {URLSearchParams, Intl, Date, location: {pathname}, HornigoldStay: {get: () => ({...stay})},
    document: {querySelector: sel => sel === 'a[data-booking]' ? main : null,
      querySelectorAll: sel => sel === 'a[data-booking]' ? [main] : sel === 'a[data-booking-all]' ? [all] : [],
      addEventListener: (type, fn) => { listeners[type] = fn; }}};
  sandbox.window = sandbox;
  vm.runInNewContext(code, sandbox);
  return {main, all, change: next => { stay = next; listeners.change(); }};
}
const future = offset => new Date(Date.now() + offset * 86400000).toISOString().slice(0, 10);
test('chosen room narrows the main button; the second link shows all rooms for the same dates', () => {
  const stay = {arrival: future(30), departure: future(32), guests: '3', room: 'suite'};
  const {main, all} = page(stay);
  const dates = `arrivalDate=${stay.arrival}&departureDate=${stay.departure}&personsCount=3`;
  assert.equal(main.href, `${BASE}/pl/${H}/offers?${dates}&featuredRoomTypeId=4833`);
  assert.equal(all.href, `${BASE}/pl/${H}/offers?${dates}`);
  assert.equal(all.parentElement.hidden, false);
});
test('the all-rooms link stays hidden when it would repeat the main button', () => {
  const dates = {arrival: future(30), departure: future(32), guests: '2'};
  for (const stay of [{}, dates, {...dates, room: 'hornigold'}, {room: 'classic'}]) {
    const {main, all} = page(stay);
    assert.equal(all.href, main.href);
    assert.equal(all.parentElement.hidden, true);
  }
});
test('the all-rooms link follows changes made in the page forms', () => {
  const dates = {arrival: future(30), departure: future(32), guests: '2'};
  const view = page({...dates, room: 'classic'});
  assert.equal(view.all.parentElement.hidden, false);
  view.change(dates);
  assert.equal(view.all.parentElement.hidden, true);
  assert.equal(view.main.href, view.all.href);
});
