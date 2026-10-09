/* Staged integration. Not shipped by the current website build. */
(() => {
 'use strict';
 const id='2174344740165965';
 const config=document.querySelector('meta[name="hornigold-meta-pixel"]');
 if(location.origin!=='https://hornigold.pl'||config?.content!==id)return;
 // Avoid SDK disclosure of reservation parameters, fragments or free-text query data.
 if(location.search||location.hash||window.fbq)return;
 const sent=new Set();let loaded=false,granted=false;
 function allowed(){return window.HornigoldPrivacy?.allowsMarketing?.()===true;}
 function clearCookies(){for(const name of ['_fbp','_fbc'])for(const domain of ['', '; Domain=hornigold.pl','; Domain=.hornigold.pl'])document.cookie=name+'=; Max-Age=0; Path=/; SameSite=Lax; Secure'+domain;}
 function send(name){if(!granted||!allowed()||!loaded||sent.has(name)||!crypto.randomUUID)return;sent.add(name);const eventID=crypto.randomUUID();window.fbq('track',name,{}, {eventID});}
 function enable(){
  if(!allowed())return;
  granted=true;
  if(!loaded){
   // Queue only after explicit advertising consent; no automatic advanced matching.
   const fbq=window.fbq=function(){fbq.callMethod?fbq.callMethod.apply(fbq,arguments):fbq.queue.push(arguments)};
   window._fbq=fbq;fbq.push=fbq;fbq.loaded=true;fbq.version='2.0';fbq.queue=[];
   fbq('consent','grant');fbq('set','autoConfig',false,id);fbq('init',id);
   const script=document.createElement('script');script.async=true;script.src='https://connect.facebook.net/en_US/fbevents.js';script.dataset.hornigoldMeta='';document.head.append(script);loaded=true;
  }else window.fbq('consent','grant');
  send('PageView');
  if(/^(pokoje|pokoj|apartament)/.test(document.body.dataset.pageKey||''))send('ViewContent');
 }
 function revoke(){const was=granted;granted=false;if(loaded)window.fbq('consent','revoke');clearCookies();if(was)location.reload();}
 window.addEventListener('hornigold:privacy',()=>{allowed()?enable():revoke()});
 document.addEventListener('click',e=>{if(e.target.closest?.('a[href^="tel:"],a[href^="mailto:"]'))send('Contact')});
 // No Purchase, no form content, no contact destination, no automatic CAPI endpoint.
 if(allowed())enable();
})();
