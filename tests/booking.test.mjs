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
