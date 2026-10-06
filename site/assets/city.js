(() => {
  const root = document.querySelector('[data-directory]');
  if (!root) return;
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ł/g,'l').replace(/Ł/g,'L').toLocaleLowerCase();
  const places = [...root.querySelectorAll('[data-place]')];
  const index = places.map(place => normalize(place.textContent));
  root.querySelector('[data-place-search]').addEventListener('input', event => {
    const terms = normalize(event.target.value).trim().split(/\s+/).filter(Boolean);
    let count = 0;
    places.forEach((place, i) => {
      place.hidden = !terms.every(term => index[i].includes(term));
      if (!place.hidden) count++;
    });
    root.querySelector('[data-place-count]').textContent = count;
    root.querySelector('[data-place-empty]').hidden = count > 0;
  });
})();
