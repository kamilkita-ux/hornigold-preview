// Basic Consent Mode: no Google Ads request before separate advertising consent.
(() => {
  'use strict';
  if(location.origin!=='https://hornigold.pl'||window.HornigoldGA4?.enabled!==true)return;
  const id='AW-18507796156';let granted=false,configured=false;
  window.dataLayer=window.dataLayer||[];
  const tag=(...args)=>window.dataLayer.push(args);
  function clear(){
    for(const item of document.cookie.split(';')){
      const name=item.split('=')[0].trim();if(!/^_gcl_/.test(name))continue;
      for(const domain of ['', '; domain=hornigold.pl', '; domain=.hornigold.pl'])document.cookie=name+'=; Max-Age=0; path=/'+domain+'; Secure; SameSite=Lax';
    }
  }
  if(!window.HornigoldGoogleConsentInitialized){tag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});window.HornigoldGoogleConsentInitialized=true;}
  tag('set','ads_data_redaction',true);
  function apply(){
    const allow=window.HornigoldPrivacy?.allowsMarketing?.()===true;
    if(!allow)clear();
    if(allow===granted)return;
    granted=allow;
    if(!allow){location.reload();return;}
    tag('consent','update',{analytics_storage:window.HornigoldPrivacy?.allowsAnalytics?.()===true?'granted':'denied',ad_storage:'granted',ad_user_data:'granted',ad_personalization:'denied'});
    if(configured)return;configured=true;
    tag('js',new Date());
    tag('config',id,{page_location:location.origin+location.pathname,page_referrer:'',page_title:'Hornigold',allow_ad_personalization_signals:false,cookie_expires:7776000,cookie_update:false});
    if(document.querySelector('script[data-hornigold-google-tag]'))return;
    const script=document.createElement('script');script.async=true;script.setAttribute('data-hornigold-google-tag','');
    script.src='https://www.googletagmanager.com/gtag/js?id='+id;document.head.appendChild(script);
  }
  window.addEventListener('hornigold:privacy',apply);apply();
})();
