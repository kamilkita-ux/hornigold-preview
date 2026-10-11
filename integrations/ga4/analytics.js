// Load only after the CMP and translated privacy documents support analytics.
(() => {
  'use strict';
  const config=window.HornigoldGA4;
  if(location.origin!=='https://hornigold.pl'||config?.enabled!==true||!/^G-[A-Z0-9]+$/.test(config.measurementId||''))return;
  const id=config.measurementId;
  let loaded=false, granted=false;
  window.dataLayer=window.dataLayer||[];
  function tag(){window.dataLayer.push(arguments);}
  window['ga-disable-'+id]=true;
  tag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
  function apply(){
    const allow=window.HornigoldPrivacy?.allowsAnalytics?.()===true;
    if(allow===granted)return;
    granted=allow;
    window['ga-disable-'+id]=!allow;
    if(!allow){
      // Block collection before clearing first-party GA cookies and unloading the tag.
      for(const item of document.cookie.split(';')){
        const name=item.split('=')[0].trim();
        if(!/^_ga(?:_|$)/.test(name))continue;
        for(const domain of ['', '; domain=hornigold.pl', '; domain=.hornigold.pl'])document.cookie=name+'=; Max-Age=0; path=/'+domain+'; Secure; SameSite=Lax';
      }
      location.reload();
      return;
    }
    tag('consent','update',{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
    if(loaded)return;
    loaded=true;
    tag('js',new Date());
    // Only allow known campaign labels; never transmit booking or arbitrary URL parameters.
    tag('config',id,{send_page_view:false,allow_google_signals:false,allow_ad_personalization_signals:false,cookie_expires:15552000,cookie_update:false,page_location:location.origin+location.pathname,page_referrer:'',page_title:'Hornigold'});
    const page=new URL(location.origin+location.pathname);
    const incoming=new URLSearchParams(location.search||'');
    const allowed={utm_source:['instagram','facebook','linkedin','google_business'],utm_medium:['organic_social','paid_social','organic'],utm_campaign:['profile','room_guide','city_guide','stay_enquiry']};
    for(const [key,values] of Object.entries(allowed))if(values.includes(incoming.get(key)))page.searchParams.set(key,incoming.get(key));
    let referrer='';try{const ref=new URL(document.referrer);if(['http:','https:'].includes(ref.protocol))referrer=ref.origin+'/';}catch{}
    tag('event','page_view',{page_location:page.href,page_referrer:referrer});
    const script=document.createElement('script');
    script.async=true;
    script.src='https://www.googletagmanager.com/gtag/js?id='+id;
    document.head.appendChild(script);
  }
  document.addEventListener('click',event=>{
    if(!granted||window.HornigoldPrivacy?.allowsAnalytics?.()!==true)return;
    const link=event.target?.closest?.('a[href]');if(!link)return;
    const raw=link.getAttribute('href')||'';
    let action;
    if(raw.startsWith('tel:'))action='phone';
    else if(raw.startsWith('mailto:'))action='email';
    else if(raw.startsWith('https://be.guestsage.com/'))action='booking';
    else if(/\/rezerwacja\//.test(raw))action='booking';
    else if(link.hasAttribute('data-stay'))action='stay_planner';
    else{try{const url=new URL(raw,location.origin);const domains={'www.instagram.com':'instagram','www.facebook.com':'facebook','www.linkedin.com':'linkedin'};action=domains[url.hostname];}catch{}}
    if(action)tag('event',({phone:'click_phone',email:'click_email',booking:'booking_click',stay_planner:'stay_planner_click'}[action]||'social_link_click'),{action,language:document.documentElement?.lang||'und',page_location:location.origin+location.pathname,page_referrer:''});
  });
  document.addEventListener('change',event=>{
    if(!granted||window.HornigoldPrivacy?.allowsAnalytics?.()!==true)return;
    const input=event.target;if(!input?.matches?.('[data-compare]')||!input.checked)return;
    const allowed=['classic','suite','premium','deluxe','prestige','deluxe-premium','apartament-deluxe','prestige-deluxe','hornigold'];
    if(allowed.includes(input.value))tag('event','select_apartment',{apartment_id:input.value,language:document.documentElement.lang,page_location:location.origin+location.pathname,page_referrer:''});
  });
  window.addEventListener('hornigold:privacy',apply);
  apply();
})();
