// Canonical-host indexing gate. Deploy only with the audited production assets.
import worker from './worker.mjs';
import {canonicalRoutes} from './canonical-routes.mjs';
const canonical=new Set(canonicalRoutes);
const ORIGIN='https://hornigold.pl';
export default {async fetch(request,env,ctx){
 const url=new URL(request.url);
 const production=url.protocol==='https:' && url.hostname==='hornigold.pl';
 if(url.hostname==='www.hornigold.pl'){
  const target=new URL(url.pathname+url.search,ORIGIN);
  return Response.redirect(target.href,301);
 }
 if(url.pathname==='/robots.txt')return new Response(production?'User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: '+ORIGIN+'/sitemap.xml\n':'User-agent: *\nDisallow: /\n',{headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'}});
 const response=await worker.fetch(request,env,ctx);
 const headers=new Headers(response.headers);
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
