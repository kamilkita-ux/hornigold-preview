import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const source=fs.readFileSync(new URL('../site/assets/analytics.js',import.meta.url),'utf8');
function fixture({origin='https://hornigold.pl',enabled=true,id='G-TEST123',consent=false,referrer='',language='pl',search='?guests=2&email=private'}={}){
 const listeners={},scripts=[];let allowed=consent,reloads=0,cookies='_ga=sample; _ga_TEST=sample';
 const window={HornigoldGA4:{enabled,measurementId:id},HornigoldPrivacy:{allowsAnalytics:()=>allowed},addEventListener:(name,fn)=>listeners[name]=fn};
 const document={documentElement:{lang:language},addEventListener:(name,fn)=>listeners['document:'+name]=fn,referrer,get cookie(){return cookies},set cookie(value){cookies=value},createElement:()=>({}),head:{appendChild:s=>scripts.push(s)}};
 vm.runInNewContext(source,{window,document,location:{origin,pathname:'/pl/',search,reload:()=>reloads++},Date,URL,URLSearchParams});
 return {window,scripts,change(value){allowed=value;listeners['hornigold:privacy']?.()},reloads:()=>reloads,cookies:()=>cookies,click(href,stay=false,targetLanguage=null){listeners['document:click']?.({target:{closest:()=>({getAttribute:name=>name==='href'?href:name==='data-language'?targetLanguage:null,hasAttribute:name=>name==='data-stay'?stay:name==='data-language'?targetLanguage!==null:false})}})}};
}
test('no tag before consent or after refusal',()=>{const f=fixture();f.change(false);assert.equal(f.scripts.length,0)});
test('preview, missing ID and disabled configuration do not load Google',()=>{for(const options of [{origin:'https://kamilkita-ux.github.io'},{id:''},{enabled:false}])assert.equal(fixture({...options,consent:true}).scripts.length,0)});
test('consent loads exactly one tag and a sanitized page view',()=>{const f=fixture();f.change(true);f.change(true);assert.equal(f.scripts.length,1);const events=f.window.dataLayer.filter(a=>a[0]==='event');assert.equal(events.length,1);assert.equal(events[0][2].page_location,'https://hornigold.pl/pl/');assert.equal(events[0][2].page_referrer,'');assert.equal(JSON.stringify(f.window.dataLayer).includes('email='),false)});
test('withdrawal disables measurement, removes GA cookies and reloads',()=>{const f=fixture({consent:true});f.change(false);assert.equal(f.window['ga-disable-G-TEST123'],true);assert.match(f.cookies(),/Max-Age=0/);assert.equal(f.reloads(),1)});

test('only approved campaign labels survive URL sanitization',()=>{const f=fixture({consent:true,search:'?utm_source=instagram&utm_medium=organic_social&utm_campaign=profile&email=private&guests=3'});const event=f.window.dataLayer.find(a=>a[0]==='event');assert.equal(event[2].page_location,'https://hornigold.pl/pl/?utm_source=instagram&utm_medium=organic_social&utm_campaign=profile');});
test('contact and social clicks require consent and never send destinations',()=>{const f=fixture();f.click('mailto:private@example.com');assert.equal(f.window.dataLayer.filter(a=>a[0]==='event').length,0);f.change(true);f.click('mailto:private@example.com');f.click('tel:+48123456789');f.click('https://www.instagram.com/hornigold.apartments/');f.click('/pl/pobyt/',true);const events=f.window.dataLayer.filter(a=>a[0]==='event');assert.equal(events.length,5);assert.equal(JSON.stringify(events).includes('private@example'),false);assert.equal(JSON.stringify(events).includes('123456789'),false);assert.deepEqual(Array.from(events,e=>e[1]),['page_view','click_email','click_phone','social_link_click','stay_planner_click']);});

test("verified GBP campaign labels survive sanitization",()=>{const f=fixture({consent:true,search:"?utm_source=google&utm_medium=organic&utm_campaign=gbp&email=private"});const event=f.window.dataLayer.find(a=>a[0]==="event");assert.equal(event[2].page_location,"https://hornigold.pl/pl/?utm_source=google&utm_medium=organic&utm_campaign=gbp")});

test('actual project social links and www aliases emit one sanitized event',()=>{
 const f=fixture({consent:true});
 for(const host of ['instagram.com','www.instagram.com','facebook.com','www.facebook.com','linkedin.com','www.linkedin.com']) f.click('https://'+host+'/profile?private=discard');
 f.click('https://instagram.com.evil.invalid/');
 const events=f.window.dataLayer.filter(a=>a[0]==='event'&&a[1]==='social_link_click');
 assert.equal(events.length,6);
 assert.deepEqual(Array.from(events,e=>e[2].action),['instagram','instagram','facebook','facebook','linkedin','linkedin']);
 assert.equal(JSON.stringify(events).includes('private'),false);
});

test('unknown or identifying referrer origins are discarded; known sources lose path and query',()=>{
 for(const referrer of ['https://private-person.example/secret?email=a','https://www.google.com.evil.invalid/private','file:///private/document']){
  const f=fixture({consent:true,referrer});const event=f.window.dataLayer.find(a=>a[0]==='event');assert.equal(event[2].page_referrer,'');
 }
 const f=fixture({consent:true,referrer:'https://www.google.pl/search?q=private'});
 assert.equal(f.window.dataLayer.find(a=>a[0]==='event')[2].page_referrer,'https://www.google.pl/');
});

test('page language is explicit, including Czech, without arbitrary values',()=>{
 for(const language of ['pl','en','cs','de','zh-Hans','uk','es','it']){
  const f=fixture({consent:true,language});
  assert.equal(f.window.dataLayer.find(a=>a[0]==='event')[2].page_language,language.toLowerCase());
 }
 const f=fixture({consent:true,language:'private-value'});
 assert.equal(f.window.dataLayer.find(a=>a[0]==='event')[2].page_language,'und');
});

test('language switching is not a stay-planner conversion and excludes saved dates',()=>{
 const f=fixture({consent:true});
 f.click('/cs/?arrival=2026-11-20&guests=3',true,'cs');
 const events=f.window.dataLayer.filter(a=>a[0]==='event'&&a[1]!=='page_view');
 assert.equal(events.length,1);
 assert.equal(events[0][1],'language_switch');
 assert.equal(events[0][2].source_language,'pl');
 assert.equal(events[0][2].target_language,'cs');
 assert.equal(JSON.stringify(events).includes('arrival'),false);
 assert.equal(JSON.stringify(events).includes('guests'),false);
});

test('language events require analytics consent and reject current or unknown languages',()=>{
 const f=fixture();f.click('/cs/',true,'cs');
 assert.equal(f.window.dataLayer.filter(a=>a[0]==='event').length,0);
 f.change(true);f.click('/pl/',true,'pl');f.click('/private/',true,'private');
 assert.equal(f.window.dataLayer.filter(a=>a[0]==='event'&&a[1]==='language_switch').length,0);
});

test('Czech search attribution retains only approved labels and safe referrer origin',()=>{
 const f=fixture({consent:true,language:'cs',search:'?utm_source=seznam&utm_medium=cpc&utm_campaign=cs_search&email=private&guests=4',referrer:'https://search.seznam.cz/?q=private'});
 const event=f.window.dataLayer.find(a=>a[0]==='event');
 assert.equal(event[2].page_location,'https://hornigold.pl/pl/?utm_source=seznam&utm_medium=cpc&utm_campaign=cs_search');
 assert.equal(event[2].page_referrer,'https://search.seznam.cz/');
 assert.equal(JSON.stringify(event).includes('private'),false);
});
