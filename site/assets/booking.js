// Rezerwacje przez GuestSage AI Booking Engine (KWHotel) — przekazanie linkiem.
// Spec: docs/superpowers/specs/2026-10-09-kwhotel-guestsage-booking-design.md
(function (root) {
  'use strict';
  const HOTEL = 'c98ead00-c7fd-4013-bb45-f19539b932d4';
  const ORIGIN = 'https://be.guestsage.com';
  // Silnik nie ma chińskiego; obsługiwane m.in. pl, en, de, uk, es, it.
  const LANG = {pl: 'pl', en: 'en', de: 'de', uk: 'uk', es: 'es', it: 'it', 'zh-hans': 'en'};
  // Slug pokoju (app.js roomNames) -> featuredRoomTypeId. Silnik zawęża wtedy listę do tej jednej kategorii.
  // Tylko kategorie, które silnik sprzedaje (stan 2026-10-12): apartament-deluxe, prestige i hornigold nie mają
  // oferty online — z identyfikatorem gość zobaczyłby „brak dostępności”, bez niego widzi wszystkie wolne pokoje.
  const ROOMS = {classic: 4830, deluxe: 4828, premium: 4834, 'deluxe-premium': 4836, suite: 4833, 'prestige-deluxe': 4835};
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

  // Pierwszy segment ścieżki będący językiem strony — działa też pod bazą /hornigold-preview/.
  function pageLanguage(pathname) {
    return String(pathname || '').split('/').find(seg => Object.hasOwn(LANG, seg)) || '';
  }

  const api = {bookingUrl, pageLanguage, HOTEL, ORIGIN, LANG, ROOMS};
  if (typeof module === 'object' && module && module.exports) { module.exports = api; return; }
  root.HornigoldBooking = api;
  if (!document.querySelector('a[data-booking]')) return;
  const pageLang = pageLanguage(location.pathname);
  // Gość przyszedł tu z wyboru pokoju (?room=…) i ma ważny termin oraz kategorię sprzedawaną w silniku: strona
  // pośrednia nic mu nie daje. replace() nie zostawia jej w historii, więc „Wstecz” z silnika wraca na listę pokoi.
  const direct = bookingUrl(root.HornigoldStay ? root.HornigoldStay.get() : {}, pageLang);
  if (new URLSearchParams(location.search).has('room') && direct.includes('featuredRoomTypeId=')) { location.replace(direct); return; }
  function refresh() {
    const stay = root.HornigoldStay ? root.HornigoldStay.get() : {};
    const url = bookingUrl(stay, pageLang);
    document.querySelectorAll('a[data-booking]').forEach(a => { a.href = url; });
    // Gdy przycisk prowadzi do jednej kategorii, drugi odnośnik otwiera wszystkie pokoje na ten sam termin.
    const all = bookingUrl({...stay, room: ''}, pageLang);
    document.querySelectorAll('a[data-booking-all]').forEach(a => { a.href = all; a.parentElement.hidden = all === url; });
  }
  refresh();
  // Formularze strony aktualizują HornigoldStay w swoich listenerach; dokument dostaje zdarzenie później.
  document.addEventListener('input', refresh);
  document.addEventListener('change', refresh);
})(typeof window !== 'undefined' ? window : globalThis);
