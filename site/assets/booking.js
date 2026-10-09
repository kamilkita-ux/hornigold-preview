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
