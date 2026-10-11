import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const source=fs.readFileSync(new URL('../site/assets/privacy.js',import.meta.url),'utf8');
function fixture(){
 let now=1800000000000, stored=null, timer=null;const events=[],handlers={};
 const control=()=>({checked:false,addEventListener(){},focus(){}}),maps=control(),analytics=control(),notice={hidden:false};
 const dialog={showModal(){},querySelector:s=>s==='[name=maps]'?maps:s==='[name=analytics]'?analytics:control(),addEventListener(){}};
 const window={dispatchEvent:e=>events.push(e.detail),addEventListener:(n,f)=>handlers[n]=f};
 const localStorage={getItem:()=>stored,setItem:(k,v)=>stored=v,removeItem:()=>stored=null};
 const document={querySelector:s=>s==='#privacy-dialog'?dialog:notice,querySelectorAll:()=>[],addEventListener(){}};
 vm.runInNewContext(source,{window,document,localStorage,Date:{now:()=>now},CustomEvent:class{constructor(n,o){this.detail=o.detail}},setTimeout:(f,delay)=>{timer={f,delay};return 1},clearTimeout:()=>{timer=null}});
 return {window,events,notice,set(value){stored=JSON.stringify(value)},advance(ms){now+=ms;timer?.f()},sync(){handlers.storage({key:'hornigold-privacy'})},value:(age=0)=>({version:'2026-10-11.analytics.1',time:now-age,maps:true,analytics:true}),get:()=>stored};
}
test('cross-tab consent and revocation update permissions and publish denial',()=>{const f=fixture();f.set(f.value());f.sync();assert.equal(f.window.HornigoldPrivacy.allowsAnalytics(),true);f.set({...f.value(),analytics:false});f.sync();assert.equal(f.window.HornigoldPrivacy.allowsAnalytics(),false);assert.equal(f.events.at(-1).analytics,false)});
test('active tab expiry revokes consent without navigation and deletes storage',()=>{const f=fixture();f.set(f.value(180*86400000-50));f.sync();assert.equal(f.window.HornigoldPrivacy.allowsAnalytics(),true);f.advance(51);assert.equal(f.window.HornigoldPrivacy.allowsAnalytics(),false);assert.equal(f.events.at(-1).analytics,false);assert.equal(f.get(),null);assert.equal(f.notice.hidden,false)});
test('future timestamps cannot grant permission',()=>{const f=fixture();f.set(f.value(-1000));f.sync();assert.equal(f.window.HornigoldPrivacy.allowsAnalytics(),false)});
