import test from 'node:test';
import assert from 'node:assert/strict';
import worker from '../_cloudflare_production/server/production-entry.mjs';

test('GET and HEAD reject inherited identifiers with 410 and no Location',async()=>{
  for(const method of ['GET','HEAD'])for(const field of ['page_id','portfolio-item','lang'])for(const key of ['__proto__','constructor','toString']) {
    const url=new URL('https://hornigold.pl/');url.searchParams.set(field,key);
    const response=await worker.fetch(new Request(url,{method}),{});
    assert.equal(response.status,410,method+' '+url.search);
    assert.equal(response.headers.get('Location'),null);
    assert.match(response.headers.get('X-Robots-Tag'),/noindex/);
    assert.equal(response.headers.get('Cache-Control'),'no-store');
  }
});

test('legacy-looking parameters do not intercept the existing counter API',async()=>{
  const DB={prepare(){return {bind(){return {async first(){return {total:12,started_at:'2020-10-07'};}};}};}};
  const response=await worker.fetch(new Request('https://hornigold.pl/api/site-stats?page_id=__proto__'),{DB});
  assert.equal(response.status,200);
  assert.deepEqual(await response.json(),{total:12,startedAt:'2020-10-07',metric:'pageviews'});
});

test('legacy-looking parameters do not change protected booking handoff',async()=>{
  const response=await worker.fetch(new Request('https://hornigold.pl/pl/rezerwacja/?room=classic&arrival=2099-11-01&departure=2099-11-03&guests=2&page_id=__proto__'),{});
  assert.equal(response.status,302);
  assert.ok(response.headers.get('Location').startsWith('https://be.guestsage.com/'));
  assert.equal(response.headers.get('Referrer-Policy'),'no-referrer');
  assert.match(response.headers.get('X-Robots-Tag'),/noindex/);
});
