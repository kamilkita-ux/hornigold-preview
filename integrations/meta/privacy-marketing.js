// STAGED CMP upgrade: deploy only with translated marketing UI and synchronized policies/PDFs.
(() => {
  'use strict';
  const key='hornigold-privacy', version='2026-10-09.meta.1', lifetime=180*86400000;
  const dialog=document.querySelector('#privacy-dialog'), notice=document.querySelector('#privacy-notice');
  if(!dialog||typeof dialog.showModal!=='function')return;
  const maps=dialog.querySelector('[name=maps]'), marketing=dialog.querySelector('[name=marketing]');let opener;
  function read(){try{const value=JSON.parse(localStorage.getItem(key));if(value?.version===version&&typeof value.maps==='boolean'&&typeof value.marketing==='boolean'&&Number.isFinite(value.time)&&value.time<=Date.now()&&Date.now()-value.time<lifetime)return value;localStorage.removeItem(key);}catch{try{localStorage.removeItem(key)}catch{}}return null;}
  let state=read();
  function publish(){window.dispatchEvent(new CustomEvent('hornigold:privacy',{detail:{maps:state?.maps===true,marketing:state?.marketing===true}}));}
  function close(){dialog.close();if(opener?.isConnected)opener.focus();}
  function save(allow,ads=false){state={version,time:Date.now(),maps:allow===true,marketing:ads===true};try{localStorage.setItem(key,JSON.stringify(state));}catch{}notice.hidden=true;publish();if(dialog.open)close();}
  function open(event){event?.preventDefault();opener=document.activeElement;maps.checked=state?.maps===true;if(marketing)marketing.checked=state?.marketing===true;dialog.querySelector('[role=status]').textContent='';dialog.showModal();dialog.querySelector('[data-privacy-close]').focus();}
  window.HornigoldPrivacy={open,allowsMaps:()=>state?.maps===true,allowsMarketing:()=>state?.marketing===true,deny:()=>save(false)};
  document.querySelectorAll('[data-privacy-open]').forEach(b=>b.addEventListener('click',open));
  document.querySelectorAll('[data-privacy-necessary]').forEach(b=>b.addEventListener('click',()=>save(false)));
  dialog.querySelector('[data-privacy-save]').addEventListener('click',()=>save(maps.checked,marketing?.checked===true));
  dialog.querySelector('[data-privacy-close]').addEventListener('click',close);
  dialog.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const items=[...dialog.querySelectorAll('a[href],button:not([disabled]),input:not([disabled])')].filter(el=>el.getClientRects().length);if(!items.length)return;const current=items.indexOf(document.activeElement);e.preventDefault();items[(current+(e.shiftKey?-1:1)+items.length)%items.length].focus();});
  dialog.addEventListener('cancel',()=>{if(opener?.isConnected)setTimeout(()=>opener.focus(),0)});
  dialog.querySelector('[data-privacy-clear]').addEventListener('click',()=>{
    window.HornigoldStay?.update({arrival:'',departure:'',guests:'',room:''});
    const url=new URL(location.href);for(const k of ['arrival','departure','guests','room'])url.searchParams.delete(k);history.replaceState(null,'',url);
    for(const k of [key,'hornigold-language'])try{localStorage.removeItem(k)}catch{}
    for(const k of ['hornigold-stay','hornigold-comparison','hornigold-enquiry-plan','hornigold-language-suggestion-dismissed'])try{sessionStorage.removeItem(k)}catch{}
    state=null;maps.checked=false;if(marketing)marketing.checked=false;publish();notice.hidden=false;
    dialog.querySelector('[role=status]').textContent=dialog.dataset.cleared;
  });
  window.addEventListener('storage',e=>{if(e.key===key||e.key===null){state=read();maps.checked=state?.maps===true;if(marketing)marketing.checked=state?.marketing===true;publish();}});
  window.addEventListener('pageshow',()=>{state=read();publish()});
  // Re-check expiry when returning to a long-lived tab, not only on navigation.
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){state=read();publish();}});
  notice.hidden=state!==null;publish();
})();
