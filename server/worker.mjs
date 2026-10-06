import { readCount, countView } from './counter.mjs';
import { redirects, siteMode } from './routes.mjs';
function headersFor(response,path){
 const headers=new Headers(response.headers);
 headers.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-src https://www.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'");
 headers.set('X-Content-Type-Options','nosniff');headers.set('Referrer-Policy','no-referrer');
 headers.set('X-Frame-Options','DENY');
 headers.set('Permissions-Policy','camera=(), microphone=(), geolocation=()');
 if(siteMode==='preview')headers.set('X-Robots-Tag','noindex, nofollow, noarchive');
 if(path==='/llms.txt')headers.set('Content-Type','text/plain; charset=utf-8');
 return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
}
const json=(data,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store','X-Robots-Tag':'noindex','X-Content-Type-Options':'nosniff'}});
export default {
  async fetch(request, env) {
    const url=new URL(request.url);
    if(['GET','HEAD'].includes(request.method)){
      // The root document remembers an explicit language choice; do not force Polish here.
      const destination=redirects[url.pathname]||redirects[url.pathname.replace(/\/?$/,'/')];
      if(destination){const target=new URL(destination,url.origin);target.search=url.search;return headersFor(Response.redirect(target.href,301),url.pathname)}
    }
    if(url.pathname!=='/api/site-stats') {
      const response=await env.ASSETS.fetch(request);
      const language=url.pathname.match(/^\/(pl|en|de|zh-hans|uk|es|it)(?:\/|$)/)?.[1];
      if(response.status!==404 || !language || !['GET','HEAD'].includes(request.method)) return headersFor(response,url.pathname);
      const errorUrl=new URL('/'+language+'/404',url.origin);
      const headers=new Headers(request.headers);
      headers.delete('If-None-Match');headers.delete('If-Modified-Since');
      const localized=await env.ASSETS.fetch(new Request(errorUrl,{method:request.method,headers}));
      if(localized.status!==200) return headersFor(response,url.pathname);
      const errorHeaders=new Headers(localized.headers);errorHeaders.set('Cache-Control','no-store');
      return headersFor(new Response(localized.body,{status:404,headers:errorHeaders}),url.pathname);
    }
    if(!['GET','POST'].includes(request.method)) return headersFor(json({error:'method_not_allowed'},405),url.pathname);
    if(request.method==='POST' && (request.headers.get('Origin')!==url.origin || request.headers.get('X-Hornigold-View')!=='1' || request.headers.get('Sec-Fetch-Site')==='cross-site')) return json({error:'invalid_origin'},403);
    try {
      if(!env.DB) throw new Error('Missing DB binding');
      const result=request.method==='POST'?await countView(env.DB):await readCount(env.DB);
      return headersFor(json({...result,metric:'pageviews'}),url.pathname);
    } catch {
      console.error('site_counter_unavailable');
      return json({error:'counter_unavailable'},503);
    }
  }
};
