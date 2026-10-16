import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {legacyWordpressRedirect} from '../server/legacy-wordpress-redirects.mjs';

const origin='https://hornigold.pl';
test('six reported inherited-key URLs are gone, never redirect targets',()=>{
  for(const query of ['?page_id=__proto__','?lang=__proto__','?portfolio-item=constructor','?portfolio-item=toString','?page_id=constructor','?page_id=toString']) {
    assert.deepEqual(legacyWordpressRedirect(new URL(query,origin)),{kind:'gone'},query);
  }
});

test('all Object prototype property names are rejected in every legacy field',()=>{
  for(const key of Object.getOwnPropertyNames(Object.prototype))for(const field of ['page_id','portfolio-item','lang']) {
    const url=new URL(origin);url.searchParams.set(field,key);
    assert.deepEqual(legacyWordpressRedirect(url),{kind:'gone'},field+'='+key);
  }
});

test('all 19 approved inventory destinations and repeated attribution parameters survive',()=>{
  const csv=readFileSync(new URL('../docs/seo/URL_MIGRATION_TABLE.csv',import.meta.url),'utf8');
  const rows=csv.split('\n').map(line=>[...line.matchAll(/"((?:[^"]|"")*)"(?:,|$)/g)].map(m=>m[1].replaceAll('""','"')))
    .filter(row=>row[2]?.startsWith('known WordPress')&&row[3]==='301');
  assert.equal(rows.length,19);
  const canonical=new Set(JSON.parse(readFileSync(new URL('../routes.json',import.meta.url),'utf8')));
  for(const row of rows) {
    const url=new URL(row[0]);url.searchParams.append('utm_source','first');url.searchParams.append('utm_source','second');url.searchParams.set('arrival','2099-11-01');url.searchParams.set('guests','3');
    const actual=legacyWordpressRedirect(url),expected=new URL(row[4]);
    assert.equal(actual.kind,'redirect',row[0]);
    assert.equal(actual.target.origin,origin);
    assert.equal(actual.target.pathname,expected.pathname,row[0]);
    assert.ok(canonical.has(expected.pathname)||canonical.has(decodeURI(expected.pathname)),expected.pathname);
    assert.deepEqual(actual.target.searchParams.getAll('utm_source'),['first','second']);
    assert.equal(actual.target.searchParams.get('arrival'),'2099-11-01');
    assert.equal(actual.target.searchParams.get('guests'),'3');
    for(const field of ['page_id','portfolio-item','lang'])assert.equal(actual.target.searchParams.has(field),false);
  }
});

test('the nine approved language aliases retain their home destinations',()=>{
  for(const [language,path] of Object.entries({pl:'/pl/',en:'/en/',de:'/de/',uk:'/uk/',es:'/es/',it:'/it/',zh:'/zh-hans/','zh-hans':'/zh-hans/',cs:'/cs/'})) {
    const result=legacyWordpressRedirect(new URL('?lang='+language.toUpperCase(),origin));
    assert.equal(result.kind,'redirect');assert.equal(result.target.pathname,path);
  }
});

test('ordinary attribution is not classified as a retired WordPress URL',()=>{
  assert.deepEqual(legacyWordpressRedirect(new URL('?utm_source=google&guests=3',origin)),{kind:'none'});
});
