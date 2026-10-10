import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {buildMetaEvent} from '../integrations/meta/capi-payload.mjs';
const code=fs.readFileSync(new URL('../integrations/meta/pixel.js',import.meta.url),'utf8');
function browser({origin='https://hornigold.pl',search='',hash='',consent=false,configured=true,pageKey='pokoje'}={}){
 const handlers={},scripts=[],cookies=[],reloads=[];let allowed=consent;
 const document={querySelector:()=>configured?{content:'2174344740165965'}:null,head:{append:s=>scripts.push(s)},body:{dataset:{pageKey}},createElement:()=>({dataset:{}}),addEventListener:(n,f)=>handlers[n]=f,set cookie(v){cookies.push(v)}};
 const window={HornigoldPrivacy:{allowsMarketing:()=>allowed},addEventListener:(n,f)=>handlers[n]=f};
 vm.runInNewContext(code,{window,document,location:{origin,search,hash,reload:()=>reloads.push(true)},crypto:{randomUUID:()=> '3aa16e9c-46c0-4922-b807-9d8ffebf3734'}});
 return {window,scripts,cookies,reloads,allow(v){allowed=v;handlers['hornigold:privacy']?.()},click(){handlers.click?.({target:{closest:()=>true}})},events(){return Array.from(window.fbq?.queue||[],x=>Array.from(x)).filter(x=>x[0]==='track')}};
}
test('no script or events before advertising consent, including map-only legacy CMP',()=>{const b=browser();assert.equal(b.scripts.length,0);b.click();b.allow(false);assert.equal(b.events().length,0)});
test('previews, unconfigured documents and query/fragment URLs cannot track',()=>{for(const args of [{origin:'https://kamilkita-ux.github.io',consent:true},{configured:false,consent:true},{search:'?arrival=2026-10-10',consent:true},{hash:'#private',consent:true}])assert.equal(browser(args).scripts.length,0)});
test('grant loads once and sends distinct PageView/ViewContent/Contact only once',()=>{const b=browser();b.allow(true);b.allow(true);b.click();b.click();assert.equal(b.scripts.length,1);assert.deepEqual(b.events().map(x=>x[1]),['PageView','ViewContent','Contact']);assert.ok(b.events().every(x=>x[3].eventID));assert.ok(b.events().every(x=>Object.keys(x[2]).length===0))});
test('non-room route does not send ViewContent',()=>{assert.deepEqual(browser({consent:true,pageKey:'kontakt'}).events().map(x=>x[1]),['PageView'])});
test('withdrawal revokes, removes first-party Meta cookies and reloads SDK context',()=>{const b=browser({consent:true});b.allow(false);assert.equal(b.reloads.length,1);assert.ok(b.cookies.some(x=>x.startsWith('_fbp=; Max-Age=0')));assert.ok(b.cookies.some(x=>x.startsWith('_fbc=; Max-Age=0')));const n=b.events().length;b.click();assert.equal(b.events().length,n)});
const input=()=>({name:'Contact',eventId:'3aa16e9c-46c0-4922-b807-9d8ffebf3734',time:Math.floor(Date.now()/1000),url:'https://hornigold.pl/pl/kontakt/',consent:true,userAgent:'Test agent',fbp:'fb.1.1791571961000.12345'});
test('CAPI payload preserves shared event ID without transmitting',()=>{const p=buildMetaEvent(input());assert.equal(p.event_id,input().eventId);assert.equal(p.action_source,'website');assert.equal(p.event_name,'Contact');assert.deepEqual(Object.keys(p.user_data).sort(),['client_user_agent','fbp'])});
test('CAPI denies missing consent and unverified Purchase',()=>{assert.throws(()=>buildMetaEvent({...input(),consent:false}));assert.throws(()=>buildMetaEvent({...input(),name:'Purchase'}))});
test('CAPI rejects polluted URL, identifiers and stale timestamp',()=>{for(const patch of [{url:'https://hornigold.pl/pl/?email=private'},{url:'https://user:password@hornigold.pl/pl/'},{url:'https://preview.example/pl/'},{eventId:'------------------------------------'},{fbp:'private@example.com'},{time:0}])assert.throws(()=>buildMetaEvent({...input(),...patch}))});
test('no secret or public CAPI endpoint is shipped',()=>{assert.ok(!fs.existsSync(new URL('../site/assets/pixel.js',import.meta.url)));assert.ok(!fs.existsSync(new URL('../site/api/meta',import.meta.url)))});
