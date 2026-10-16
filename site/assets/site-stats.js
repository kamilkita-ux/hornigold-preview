(() => {
  const counter=document.querySelector('[data-view-count]');
  const unavailable=document.querySelector('[data-view-unavailable]');
  const label=document.querySelector('[data-view-label]');
  const endpoint=document.querySelector('meta[name=hornigold-counter-endpoint]')?.content;
  if(!counter||!unavailable||!endpoint)return;
  const url=new URL(endpoint,location.href);
  if(url.origin!==location.origin)return;
  let started=false;
  function updateLabel(startedAt) {
    if(!label)return;
    label.textContent=label.dataset.neutralLabel;
    if(typeof startedAt!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(startedAt))return;
    const date=new Date(startedAt+'T00:00:00Z');
    if(!Number.isFinite(date.getTime())||date.toISOString().slice(0,10)!==startedAt||date.getTime()>Date.now())return;
    const formatted=new Intl.DateTimeFormat(document.documentElement.lang,{year:'numeric',month:'short',day:'numeric',timeZone:'UTC'}).format(date);
    label.textContent=label.dataset.sinceLabel.replace('{date}',formatted);
  }
  async function update() {
    const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),8000);
    try {
      const response=await fetch(url,{method:'POST',headers:{'X-Hornigold-View':'1'},cache:'no-store',credentials:'omit',referrerPolicy:'no-referrer',signal:controller.signal});
      if(!response.ok)throw new Error('unavailable');
      const data=await response.json();
      if(!Number.isSafeInteger(data.total)||data.total<0||data.metric!=='pageviews')throw new Error('invalid count');
      counter.textContent=new Intl.NumberFormat(document.documentElement.lang).format(data.total);
      updateLabel(data.startedAt);
      counter.hidden=false;unavailable.hidden=true;
    } catch {counter.hidden=true;unavailable.hidden=false;}
    finally {clearTimeout(timeout);}
  }
  function start(){if(started||document.visibilityState!=='visible')return;started=true;update();}
  document.addEventListener('visibilitychange',start);start();
})();
