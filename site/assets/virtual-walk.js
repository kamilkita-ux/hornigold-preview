(() => {
  for (const tour of document.querySelectorAll('[data-virtual-walk]')) {
    const panels = [...tour.querySelectorAll('[data-walk-panel]')];
    const steps = [...tour.querySelectorAll('[data-walk-step]')];
    const viewer = tour.querySelector('[data-walk-viewer]');
    const gate = tour.querySelector('[data-walk-gate]');
    const load = tour.querySelector('[data-walk-load]');
    const close = tour.querySelector('[data-walk-close]');
    const previous = tour.querySelector('[data-walk-prev]');
    const next = tour.querySelector('[data-walk-next]');
    let index = 0;
    let enabled = window.HornigoldPrivacy?.allowsMaps()===true;
    let frame;
    function render() {
      panels.forEach((panel, i) => { panel.hidden = i !== index; });
      steps.forEach((button, i) => {
        if (i === index) button.setAttribute('aria-current', 'step');
        else button.removeAttribute('aria-current');
      });
      previous.disabled = index === 0;
      next.disabled = index === panels.length - 1;
      tour.querySelector('[data-walk-progress]').textContent = `${index + 1} / ${panels.length}`;
      if (frame) { frame.remove(); frame = undefined; }
      gate.hidden = enabled;
      close.hidden = !enabled;
      if (!enabled) return;
      const source = new URL(panels[index].dataset.embed);
      if (source.origin !== 'https://www.google.com' || source.pathname !== '/maps/embed') return;
      frame = document.createElement('iframe');
      frame.title = 'Google Street View — ' + panels[index].querySelector('h3').textContent;
      frame.referrerPolicy = 'no-referrer';
      frame.allowFullscreen = true;
      frame.src = source.href;
      viewer.append(frame);
    }
    steps.forEach((button, i) => button.addEventListener('click', () => { index = i; render(); }));
    previous.addEventListener('click', () => { index = Math.max(0, index - 1); render(); });
    next.addEventListener('click', () => { index = Math.min(panels.length - 1, index + 1); render(); });
    load.addEventListener('click', () => { window.HornigoldPrivacy?.open(); });
    window.addEventListener('hornigold:privacy', event => { enabled = event.detail.maps===true; render(); });
    close.addEventListener('click', () => { window.HornigoldPrivacy?.deny(); enabled = false; render(); load.focus(); });
    tour.querySelector('[data-walk-controls]').hidden = false;
    tour.querySelector('[data-walk-selectors]').hidden = false;
    load.hidden = false;
    render();
  }
})();
