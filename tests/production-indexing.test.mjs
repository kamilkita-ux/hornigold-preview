import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import worker from '../_cloudflare_production/server/production-entry.mjs';
const env={ASSETS:{async fetch(request){
 const path=new URL(request.url).pathname;
 if(path.includes('missing-page'))return new Response('Missing',{status:404});
 if(path==='/release.json')return Response.json(JSON.parse(await readFile(new URL('../_production_ready/release.json',import.meta.url),'utf8')));
 return new Response('<html><head><meta name="robots" content="index,follow"></head><body>Source</body></html>',{headers:{'Content-Type':'text/html','X-Robots-Tag':'noindex'}});
}}};
for(const host of ['hornigold.pl','hornigold-przeglad-beata.ai-bd6d706867.chatgpt.site','hornigold.ffp-inwestor-accpunt.workers.dev']){
 test(host+' canonical page indexing gate',async()=>{const r=await worker.fetch(new Request('https://'+host+'/pl/'),env);assert.equal(r.status,200);assert.equal(r.headers.get('X-Robots-Tag'),host==='hornigold.pl'?null:'noindex, nofollow, noarchive');assert.equal(r.headers.get('X-Frame-Options'),'DENY');});
 test(host+' robots gate',async()=>{const r=await worker.fetch(new Request('https://'+host+'/robots.txt'),env);const text=await r.text();assert.ok(text.includes(host==='hornigold.pl'?'Allow: /':'Disallow: /'));});
 test(host+' actual runtime release state',async()=>{const r=await worker.fetch(new Request('https://'+host+'/release.json'),env);const d=await r.json();assert.equal(d.indexing,host==='hornigold.pl');assert.equal(d.domainConnected,host==='hornigold.pl');assert.equal(d.bookingEnabled,false);assert.equal(d.paymentsEnabled,false);});
}
for(const path of ['/documents/hornigold-policies-pl.pdf','/pl/404.html','/pl/missing-page/','/api/site-stats','/release.json','/'])test('technical path stays excluded: '+path,async()=>{const r=await worker.fetch(new Request('https://hornigold.pl'+path),env);assert.match(r.headers.get('X-Robots-Tag'),/noindex/);if(path.includes('missing-page'))assert.equal(r.status,404);});
test('www redirects with path and query',async()=>{const r=await worker.fetch(new Request('https://www.hornigold.pl/en/?guests=2'),env);assert.equal(r.status,301);assert.equal(r.headers.get('location'),'https://hornigold.pl/en/?guests=2');});
test('HTTP cannot activate indexing',async()=>{const r=await worker.fetch(new Request('http://hornigold.pl/pl/'),env);assert.match(r.headers.get('X-Robots-Tag'),/noindex/);});
test('preview source remains unchanged',async()=>{const source=await readFile(new URL('../server/routes.mjs',import.meta.url),'utf8');assert.match(source,/siteMode="preview"/);assert.match(await readFile(new URL('../site/robots.txt',import.meta.url),'utf8'),/Disallow: \//);});

test('conditional canonical responses cannot acquire noindex',async()=>{const r=await worker.fetch(new Request('https://hornigold.pl/pl/'),{ASSETS:{fetch:async()=>new Response(null,{status:304,headers:{'X-Robots-Tag':'noindex'}})}});assert.equal(r.status,304);assert.equal(r.headers.get('X-Robots-Tag'),null);});

test('HEAD release response never parses an empty body',async()=>{const r=await worker.fetch(new Request('https://hornigold.pl/release.json',{method:'HEAD'}),{ASSETS:{fetch:async()=>new Response(null,{status:200})}});assert.equal(r.status,200);});
