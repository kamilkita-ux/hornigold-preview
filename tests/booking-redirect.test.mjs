// Wybór pokoju z terminem ma trafić do silnika bez malowania strony Rezerwacja: Worker odpowiada 302.
// Adres musi być ten sam, który buduje site/assets/booking.js — test porównuje oba źródła.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import worker from '../_cloudflare_production/server/production-entry.mjs';

const sandbox = {module: {exports: {}}, URLSearchParams, Intl, Date};
vm.runInNewContext(readFileSync(new URL('../site/assets/booking.js', import.meta.url), 'utf8'), sandbox);
const B = sandbox.module.exports;
const ROOMS = Object.keys(B.ROOMS), LANGUAGES = Object.keys(B.LANG);
const day = offset => new Date(Date.now() + offset * 86400000).toISOString().slice(0, 10);
const STAY = {arrival: day(30), departure: day(32), guests: '2'};

function env() {
  const calls = [];
  return {calls, ASSETS: {async fetch(request) { calls.push(new URL(request.url).pathname); return new Response('<html><body>Rezerwacja</body></html>', {headers: {'Content-Type': 'text/html'}}); }}};
}
const address = (language, stay, path = 'rezerwacja/') => `https://hornigold.pl/${language}/${path}?${new URLSearchParams(Object.entries(stay).filter(([, value]) => value !== undefined))}`;

test('booking.js and the Worker know the same rooms and languages', () => {
  assert.equal(ROOMS.length, 6);
  assert.equal(LANGUAGES.length, 7);
});

for (const language of LANGUAGES) test(`${language}: a room with dates is redirected to the engine address booking.js builds`, async () => {
  for (const room of ROOMS) for (const guests of ['1', '2', '6', '9', undefined]) {
    const stay = {...STAY, guests, room}, e = env();
    const response = await worker.fetch(new Request(address(language, stay)), e);
    assert.equal(response.status, 302, `${room}, guests ${guests}`);
    assert.equal(response.headers.get('Location'), B.bookingUrl(stay, language));
    assert.match(response.headers.get('Location'), /&featuredRoomTypeId=\d+$/);
    assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.match(response.headers.get('X-Robots-Tag'), /noindex/);
    assert.deepEqual(e.calls, [], 'the reservation page must not be fetched');
  }
});

test('HEAD and a path without the trailing slash are redirected too', async () => {
  const stay = {...STAY, room: 'suite'};
  assert.equal((await worker.fetch(new Request(address('pl', stay), {method: 'HEAD'}), env())).status, 302);
  assert.equal((await worker.fetch(new Request(address('pl', stay, 'rezerwacja')), env())).headers.get('Location'), B.bookingUrl(stay, 'pl'));
});

const STAYS = [
  ['room without an online offer', {...STAY, room: 'hornigold'}],
  ['apartment without an online offer', {...STAY, room: 'apartament-deluxe'}],
  ['unknown room', {...STAY, room: 'constructor'}],
  ['no room', STAY],
  ['no dates', {room: 'classic'}],
  ['arrival in the past', {arrival: day(-2), departure: day(2), guests: '2', room: 'classic'}],
  ['departure not after arrival', {arrival: day(30), departure: day(30), guests: '2', room: 'classic'}],
  ['impossible date', {arrival: '2027-02-30', departure: '2027-03-02', guests: '2', room: 'classic'}],
  ['not a date', {arrival: 'jutro', departure: 'pojutrze', room: 'classic'}],
];
for (const [why, stay] of STAYS) test(`the reservation page is served: ${why}`, async () => {
  const e = env();
  const response = await worker.fetch(new Request(address('pl', stay)), e);
  assert.equal(response.status, 200);
  assert.deepEqual(e.calls, ['/pl/rezerwacja/']);
  assert.doesNotMatch(B.bookingUrl(stay, 'pl'), /featuredRoomTypeId/, 'booking.js must agree that there is nothing to hand over');
});

test('only the reservation page of a known language redirects', async () => {
  const stay = {...STAY, room: 'classic'};
  for (const path of ['pobyt/', 'pokoje/classic/', 'rezerwacja/regulamin/']) assert.equal((await worker.fetch(new Request(address('pl', stay, path)), env())).status, 200, path);
  assert.equal((await worker.fetch(new Request(address('fr', stay)), env())).status, 200);
  assert.notEqual((await worker.fetch(new Request(address('pl', stay), {method: 'POST'}), env())).status, 302);
});
