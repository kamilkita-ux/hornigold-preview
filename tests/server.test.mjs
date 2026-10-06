import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import worker from '../server/worker.mjs';
import {redirects} from '../server/routes.mjs';
function database(file=':memory:',init=true){const sql=new DatabaseSync(file);if(init)sql.exec(readFileSync(new URL('../drizzle/0000_quiet_overlord.sql',import.meta.url),'utf8'));return {sql,prepare(q){return {bind(...args){return {async first(){return sql.prepare(q).get(...args)??null;}}}}}};}
const req=(method='GET',extra={})=>new Request('https://example.com/api/site-stats',{method,headers:method==='POST'?{Origin:'https://example.com','X-Hornigold-View':'1',...extra}:extra});
test('existing counter survives concurrent increments and database reopen',async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'hornigold-counter-'));try{
 const file=path.join(dir,'count.sqlite');let DB=database(file);DB.sql.prepare('INSERT INTO site_counters VALUES (?,?,?)').run('pageviews',122,'2026-10-05');
 let r=await worker.fetch(req(),{DB});assert.equal((await r.json()).total,122);
 await Promise.all(Array.from({length:80},()=>worker.fetch(req('POST'),{DB})));DB.sql.close();DB=database(file,false);
 r=await worker.fetch(req(),{DB});assert.deepEqual(await r.json(),{total:202,startedAt:'2026-10-05',metric:'pageviews'});assert.equal(r.headers.get('set-cookie'),null);assert.equal(r.headers.get('cache-control'),'no-store');
 assert.deepEqual(DB.sql.prepare('PRAGMA table_info(site_counters)').all().map(x=>x.name),['key','total','started_at']);DB.sql.close();
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test('foreign origins and missing headers cannot increment',async()=>{
 const DB=database();for(const headers of [{Origin:'https://evil.example'},{'X-Hornigold-View':''},{'Sec-Fetch-Site':'cross-site'}])assert.equal((await worker.fetch(req('POST',headers),{DB})).status,403);
 assert.equal((await worker.fetch(req('DELETE'),{DB})).status,405);assert.equal((await(await worker.fetch(req(),{DB})).json()).total,0);DB.sql.close();
});
test('failed database never returns a fake count',async()=>assert.equal((await worker.fetch(req('POST'),{})).status,503));
test('every legacy alias redirects with the selected dates and guests',async()=>{
 for(const [p,to] of Object.entries(redirects))for(const pathname of [p,p.replace(/\/$/,'')]){
 const r=await worker.fetch(new Request('https://example.com'+pathname+'?arrival=2027-05-12&departure=2027-05-15&guests=3'),{});
 assert.equal(r.status,301,pathname);const u=new URL(r.headers.get('location'));assert.equal(u.pathname,to);assert.equal(u.searchParams.get('guests'),'3');assert.equal(u.searchParams.get('arrival'),'2027-05-12');
 }
});
test('root uses saved-language document and standard pages have protective headers',async()=>{
 const r=await worker.fetch(new Request('https://example.com/'),{ASSETS:{fetch:async()=>new Response('remember-language')}});
 assert.equal(r.status,200);assert.equal(await r.text(),'remember-language');assert.match(r.headers.get('Content-Security-Policy'),/frame-ancestors 'none'/);assert.equal(r.headers.get('X-Frame-Options'),'DENY');assert.equal(r.headers.get('Referrer-Policy'),'no-referrer');assert.match(r.headers.get('X-Robots-Tag'),/noindex/);
});
test('all language errors preserve HTTP404, correct language and no stale conditional request',async()=>{
 for(const lang of ['pl','en','de','zh-hans','uk','es','it']){
 let calls=0;const r=await worker.fetch(new Request('https://example.com/'+lang+'/missing/',{headers:{'If-None-Match':'old'}}),{ASSETS:{fetch:async req=>{if(++calls===1)return new Response('missing',{status:404});assert.equal(new URL(req.url).pathname,'/'+lang+'/404');assert.equal(req.headers.get('If-None-Match'),null);return new Response('<html lang="'+lang+'">Error</html>')}}});
 assert.equal(r.status,404);assert.match(await r.text(),new RegExp('lang="'+lang+'"'));
 }
});
