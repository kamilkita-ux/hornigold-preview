// Canonical-host indexing gate. Deploy only with the audited production assets.
import worker from './worker.mjs';
import {canonicalRoutes} from './canonical-routes.mjs';
const canonical=new Set(canonicalRoutes);
const ORIGIN='https://hornigold.pl';
// A room chosen with valid dates (/{language}/rezerwacja/?room=…&arrival=…&departure=…) goes straight to the GuestSage
// engine with 302, so the browser never paints the intermediate page. Same rules and address as bookingUrl() in
// site/assets/booking.js; tests/booking-redirect.test.mjs compares the two. Anything else gets the reservation page.
const BOOKING='https://be.guestsage.com',BOOKING_HOTEL='c98ead00-c7fd-4013-bb45-f19539b932d4';
const BOOKING_LANG={pl:'pl',en:'en',de:'de',uk:'uk',es:'es',it:'it','zh-hans':'en'};
const BOOKING_ROOMS={classic:4830,deluxe:4828,premium:4834,'deluxe-premium':4836,suite:4833,'prestige-deluxe':4835};
const validDate=v=>/^\d{4}-\d{2}-\d{2}$/.test(v||'') && !isNaN(Date.parse(v)) && new Date(v+'T12:00:00Z').toISOString().slice(0,10)===v;
function bookingRedirect(url){
 const language=url.pathname.match(/^\/(pl|en|de|zh-hans|uk|es|it)\/rezerwacja\/?$/)?.[1];
 const room=url.searchParams.get('room'),arrival=url.searchParams.get('arrival'),departure=url.searchParams.get('departure'),guests=url.searchParams.get('guests');
 if(!language || !Object.hasOwn(BOOKING_ROOMS,room))return null;
 const today=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Warsaw'}).format(new Date());
 if(!validDate(arrival) || arrival<today || !validDate(departure) || departure<=arrival)return null;
 return BOOKING+'/'+BOOKING_LANG[language]+'/'+BOOKING_HOTEL+'/offers?'+new URLSearchParams({arrivalDate:arrival,departureDate:departure,personsCount:/^[1-6]$/.test(guests||'')?guests:'2',featuredRoomTypeId:String(BOOKING_ROOMS[room])});
}
export default {async fetch(request,env,ctx){
 const url=new URL(request.url);
 const production=url.protocol==='https:' && url.hostname==='hornigold.pl';
 if(production && url.pathname==='/' && ['GET','HEAD'].includes(request.method))return Response.redirect(new URL('/pl/'+url.search,ORIGIN).href,301);
 if(url.hostname==='www.hornigold.pl'){
  const target=new URL(url.pathname+url.search,ORIGIN);
  return Response.redirect(target.href,301);
 }
 const booking=['GET','HEAD'].includes(request.method) && bookingRedirect(url);
 if(booking)return new Response(null,{status:302,headers:{'Location':booking,'Cache-Control':'no-store','X-Robots-Tag':'noindex, nofollow, noarchive','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'}});
 // Google Search Console requires 200 at the exact /google<hex>.html URL; Cloudflare assets (html_handling
 // auto-trailing-slash) would answer 307 to the extensionless path, so serve that asset's body directly.
 const verification=url.pathname.match(/^\/(google[0-9a-f]+)\.html$/);
 if(verification && ['GET','HEAD'].includes(request.method)){
  const asset=await env.ASSETS.fetch(new Request(new URL('/'+verification[1],url.origin),{method:request.method}));
  if(asset.status===200)return new Response(asset.body,{status:200,headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'}});
 }
 if(url.pathname==='/robots.txt')return new Response(production?'User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: '+ORIGIN+'/sitemap.xml\n':'User-agent: *\nDisallow: /\n',{headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'}});
 const response=await worker.fetch(request,env,ctx);
 const headers=new Headers(response.headers);
 if(production){const policy=headers.get('Content-Security-Policy');if(policy)headers.set('Content-Security-Policy',policy.replace("script-src 'self'","script-src 'self' https://www.googletagmanager.com").replace("connect-src 'self'","connect-src 'self' https://www.google-analytics.com https://region1.google-analytics.com"));}
 if(production)headers.set('Referrer-Policy','strict-origin-when-cross-origin');
 const indexable=production && [200,304].includes(response.status) && (canonical.has(url.pathname) || url.pathname==='/sitemap.xml');
 if(indexable)headers.delete('X-Robots-Tag');
 else headers.set('X-Robots-Tag','noindex, nofollow, noarchive');
 if(url.pathname==='/release.json' && request.method==='GET' && response.status===200){
  const data=await response.json();
  for(const key of ['Content-Length','Content-Encoding','ETag','Last-Modified'])headers.delete(key);
  headers.set('Cache-Control','no-store');
  return Response.json({...data,domainConnected:production,indexing:production,published:production,deploymentHost:url.hostname},{headers});
 }
 return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
}};
