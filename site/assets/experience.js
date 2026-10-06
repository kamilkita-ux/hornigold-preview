(() => {
  'use strict';
  const {t,validate,setError} = window.HornigoldI18n;
  const date = value => /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
  const today = new Intl.DateTimeFormat('sv-SE', {timeZone: 'Europe/Warsaw'}).format(new Date());
  const options = [...document.querySelectorAll('[data-compare]')];
  const comparisonStatus = document.querySelector('[data-compare-status]');
  try {
    const saved=JSON.parse(sessionStorage.getItem('hornigold-comparison')||'null');
    if(Array.isArray(saved)&&saved.length<=3&&new Set(saved).size===saved.length&&saved.every(v=>options.some(o=>o.value===v)))options.forEach(o=>o.checked=saved.includes(o.value));
  } catch {}
  function compare() {
    const selected = options.filter(o => o.checked).map(o => o.value);
    if(options.length)try{sessionStorage.setItem('hornigold-comparison',JSON.stringify(selected));}catch{}
    document.querySelectorAll('[data-comparison]').forEach(c => { c.hidden = !selected.includes(c.dataset.comparison); });
    if (comparisonStatus) comparisonStatus.textContent = selected.length ? t('Wybrano kategorii: ', 'Selected categories: ') + selected.length : t('Wybierz kategorię, aby rozpocząć porównanie.', 'Select a category to start comparing.');
  }
  options.forEach(o => o.addEventListener('change', () => {
    if (options.filter(x => x.checked).length > 3) {
      o.checked = false;
      comparisonStatus.textContent = t('Możesz porównać maksymalnie trzy kategorie.', 'You can compare up to three categories.');
      return;
    }
    compare();
  }));
  compare();
  document.querySelectorAll('[data-event-end]').forEach(el => {
    if (el.dataset.eventEnd < today || el.dataset.eventReview < today) el.remove();
  });
  const empty = document.querySelector('[data-events-empty]');
  if (empty) empty.hidden = !!document.querySelector('[data-event-end]');
  const form = document.querySelector('[data-enquiry]');
  if (!form) return;
  const f = form.elements, result = form.querySelector('[data-enquiry-result]');
  const nextDay=value=>{const d=new Date(value+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+1);return d.toISOString().slice(0,10);};
  f.arrival.min = today;
  f.departure.min = nextDay(today);
  // No persistence of free text or invoice requirements.
  try {
    const stay = window.HornigoldStay.get();
    if (date(stay.arrival) && stay.arrival >= today) {
      f.arrival.value = stay.arrival; f.departure.min=nextDay(stay.arrival);
      if(date(stay.departure)&&stay.departure>stay.arrival)f.departure.value=stay.departure;
    }
    if (/^[1-6]$/.test(String(stay.guests))) f.people.value = stay.guests;
    const saved=JSON.parse(sessionStorage.getItem('hornigold-enquiry-plan')||'null');
    if(saved&&saved.arrival===f.arrival.value&&saved.departure===f.departure.value){
      for(const key of ['people','rooms'])if(/^\d+$/.test(saved[key])&&+saved[key]>=1&&+saved[key]<=100)f[key].value=saved[key];
    }
  } catch {}
  form.addEventListener('input', () => {
    result.hidden = true;f.departure.setCustomValidity('');
    f.departure.min=date(f.arrival.value)&&f.arrival.value>=today?nextDay(f.arrival.value):nextDay(today);
    const validArrival=date(f.arrival.value)&&f.arrival.value>=today?f.arrival.value:'';
    const validDeparture=validArrival&&date(f.departure.value)&&f.departure.value>validArrival?f.departure.value:'';
    window.HornigoldStay.update({arrival:validArrival,departure:validDeparture,guests:f.people.value});
    // Numeric planning values only; never persist purpose, invoice choice or free text.
    const plan={arrival:validArrival,departure:validDeparture};
    for(const key of ['people','rooms'])if(/^\d+$/.test(f[key].value)&&+f[key].value>=1&&+f[key].value<=100)plan[key]=f[key].value;
    try{sessionStorage.setItem('hornigold-enquiry-plan',JSON.stringify(plan));}catch{}
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const error = form.querySelector('[data-enquiry-error]');
    error.textContent = ''; f.departure.setCustomValidity('');
    if (!validate(form)) return;
    if (!date(f.arrival.value) || !date(f.departure.value) || f.arrival.value < today || f.departure.value <= f.arrival.value) {
      setError(form,f.departure,t('Wyjazd musi być późniejszy od przyjazdu; termin nie może być w przeszłości.', 'Departure must follow arrival; dates cannot be in the past.'));return;
    }
    if (+f.rooms.value > +f.people.value) {
      setError(form,f.rooms,t('Liczba pokojów nie może być większa od liczby osób.', 'The number of rooms cannot exceed the number of guests.'));return;
    }
    const invoice = f.invoice.selectedOptions[0].textContent;
    const text = [t('Dzień dobry, proszę o ofertę pobytu w Hornigold.', 'Hello, please send a quote for a stay at Hornigold.'),
      t('Przyjazd: ', 'Arrival: ') + f.arrival.value,
      t('Wyjazd: ', 'Departure: ') + f.departure.value,
      t('Osoby: ', 'Guests: ') + f.people.value,
      t('Pokoje: ', 'Rooms: ') + f.rooms.value,
      t('Cel: ', 'Purpose: ') + f.purpose.value,
      t('Faktura: ', 'Invoice: ') + invoice,
      t('Wymagania: ', 'Requirements: ') + (f.needs.value.trim() || t('Do ustalenia', 'To be agreed')),
      t('Proszę o pełną cenę, warunki płatności i anulacji oraz potwierdzenie dostępności. To zapytanie, nie rezerwacja.', 'Please confirm availability, the total price, payment and cancellation terms. This is an enquiry, not a reservation.')].join('\n');
    form.querySelector('[data-enquiry-text]').value = text;
    form.querySelector('[data-enquiry-mail]').href = 'mailto:office@hornigold.pl?subject=' + encodeURIComponent(t('Zapytanie o pobyt — Hornigold', 'Stay enquiry — Hornigold')) + '&body=' + encodeURIComponent(text);
    result.hidden = false;
    form.querySelector('[data-copy-status]').textContent = '';
    result.querySelector('textarea').focus();
  });
  form.querySelector('[data-enquiry-copy]').addEventListener('click', async () => {
    const field = form.querySelector('[data-enquiry-text]'), status = form.querySelector('[data-copy-status]');
    try { await navigator.clipboard.writeText(field.value); status.textContent = t('Skopiowano. Niczego nie wysłano.', 'Copied. Nothing has been sent.'); }
    catch { field.focus(); field.select(); status.textContent = t('Zaznaczono tekst — skopiuj go ręcznie.', 'Text selected — copy it manually.'); }
  });
})();
