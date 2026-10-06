(() => {
  'use strict';
  const {t,locale,validate,setError} = window.HornigoldI18n, path = location.pathname;
  const params = new URLSearchParams(location.search);
  // No campaign tracking identifiers are propagated while measurement is disabled.
  const campaignKeys=[];
  function carryCampaign(url){for(const key of campaignKeys){const value=params.get(key);if(value&&value.length<=512)url.searchParams.set(key,value);}}
  const roomNames = {classic:'Classic',deluxe:'Deluxe','deluxe-premium':'Deluxe Premium',premium:'Premium',suite:'Suite','apartament-deluxe':'Deluxe Apartment',prestige:'Prestige Apartment','prestige-deluxe':'Prestige Deluxe Apartment',hornigold:'Hornigold Apartment'};
  const plNames={'apartament-deluxe':'Apartament Deluxe',prestige:'Apartament Prestige','prestige-deluxe':'Apartament Prestige Deluxe',hornigold:'Apartament Hornigold'};
  const today = () => new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Warsaw'}).format(new Date());
  const validDate = v => /^\d{4}-\d{2}-\d{2}$/.test(v||'') && !isNaN(Date.parse(v)) && new Date(v+'T12:00:00Z').toISOString().slice(0,10)===v;
  const plusDay = v => {const d=new Date(v+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+1);return d.toISOString().slice(0,10);};
  function clean(s) {
    const out={};
    if(validDate(s.arrival)&&s.arrival>=today())out.arrival=s.arrival;
    if(out.arrival&&validDate(s.departure)&&s.departure>out.arrival)out.departure=s.departure;
    if(/^[1-6]$/.test(String(s.guests||'')))out.guests=String(s.guests);
    if(Object.hasOwn(roomNames,s.room))out.room=s.room;
    return out;
  }
  let saved={};try{saved=JSON.parse(sessionStorage.getItem('hornigold-stay')||'{}')}catch{}
  const query=Object.fromEntries(params);
  let stay=clean(params.has('arrival')||params.has('departure')?query:{...saved,...query});
  function save(){try{sessionStorage.setItem('hornigold-stay',JSON.stringify(stay))}catch{}}
  function updateLinks(){document.querySelectorAll('a[data-stay]').forEach(a=>{
    const u=new URL(a.href,location.origin);u.search='';
    Object.entries(stay).forEach(([k,v])=>u.searchParams.set(k,v));
    carryCampaign(u);
    if(a.dataset.room)u.searchParams.set('room',a.dataset.room);
    if(a.hasAttribute('data-language'))u.hash=location.hash;
    a.href=u.pathname+u.search+u.hash;
  });}
  save();updateLinks();
  window.HornigoldStay={get:()=>({...stay}),update:value=>{stay=clean({...stay,...value});save();updateLinks();}};
  // Keep the floating mobile CTA away from visible form fields and actions.
  const planningForms=[...document.querySelectorAll('form')];
  function updateFloatingBooking(){document.body.toggleAttribute('data-form-visible',planningForms.some(form=>{const r=form.getBoundingClientRect();return r.height>0&&r.bottom>0&&r.top<innerHeight;}));}
  if(planningForms.length){
    updateFloatingBooking();
    const observer=new IntersectionObserver(updateFloatingBooking);planningForms.forEach(form=>observer.observe(form));
    window.addEventListener('resize',updateFloatingBooking);
  }
  const fmt=s=>new Intl.DateTimeFormat(locale,{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(s+'T12:00:00Z'));
  document.querySelectorAll('.stay-summary').forEach(el=>{
    if(stay.arrival&&stay.departure){const nights=Math.round((new Date(stay.departure)-new Date(stay.arrival))/86400000);el.textContent=`${fmt(stay.arrival)} – ${fmt(stay.departure)} · ${t('Liczba nocy','Nights')}: ${nights} · ${t('Goście','Guests')}: ${stay.guests||2}`;}
    else el.textContent=t('Wybierz termin, aby zaplanować pobyt.','Choose your dates to plan your stay.');
    if(stay.room&&document.body.dataset.pageKey==='rezerwacja'){const strong=document.createElement('strong');strong.className='selected-room';strong.textContent=t('Kategoria pokoju: ','Room category: ')+t(plNames[stay.room]||roomNames[stay.room],roomNames[stay.room]);el.append(strong);}
  });
  document.querySelectorAll('form[data-search]').forEach(form=>{
    const a=form.elements.arrival,d=form.elements.departure,g=form.elements.guests,error=form.querySelector('.form-error');
    a.min=today();d.min=plusDay(today());
    if(stay.arrival){a.value=stay.arrival;d.value=stay.departure||'';d.min=plusDay(stay.arrival);}if(stay.guests)g.value=stay.guests;
    function sync(){stay=clean({...stay,arrival:a.value,departure:d.value,guests:g.value});save();updateLinks();}
    a.addEventListener('change',()=>{if(validDate(a.value)){d.min=plusDay(a.value);if(d.value&&d.value<=a.value)d.value='';}error.textContent='';sync();});
    d.addEventListener('change',sync);g.addEventListener('change',sync);
    form.addEventListener('submit',e=>{
      e.preventDefault();error.textContent='';
      if(!validate(form))return;
      if(!validDate(a.value)||!validDate(d.value)||a.value<today()||d.value<=a.value){setError(form,d,t('Wybierz datę wyjazdu późniejszą niż przyjazd. Termin nie może być w przeszłości.','Choose a departure date after arrival. Past dates cannot be selected.'));return;}
      sync();const u=new URL(form.action);u.search='';Object.entries(stay).forEach(([k,v])=>u.searchParams.set(k,v));carryCampaign(u);location.assign(u.pathname+u.search+'#stay-results');
    });
  });
  const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('#mobile-menu');
  if(menu&&nav){menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.hidden=!open;});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!nav.hidden){nav.hidden=true;menu.setAttribute('aria-expanded','false');menu.focus();}});}
  if(document.body.dataset.pageKey==='rezerwacja'&&(!stay.arrival||!stay.departure)){const n=document.querySelector('.notice');if(n){const p=document.createElement('p');p.textContent=t('Nie wybrano prawidłowego terminu. Wróć do planowania pobytu.','No valid dates selected. Go back and choose your stay.');n.prepend(p);}}
})();

// Keep the full language list on desktop and a compact disclosure on phones.
(()=>{const picker=document.querySelector('.language-picker');if(!picker)return;const media=window.matchMedia('(max-width:760px)');const sync=()=>{picker.open=!media.matches};sync();media.addEventListener('change',sync);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&media.matches&&picker.open){picker.open=false;picker.querySelector('summary').focus()}});document.addEventListener('click',e=>{if(media.matches&&!picker.contains(e.target))picker.open=false})})();
