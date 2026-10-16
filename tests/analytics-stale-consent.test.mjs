import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../site/assets/analytics.js',import.meta.url),'utf8');
function run({allow=false,origin='https://hornigold.pl'}={}){
 const writes=[],scripts=[],listeners={};let reloads=0;
 const document={get cookie(){return '_ga=old; _ga_X=old; essential=keep'},set cookie(value){writes.push(value)},head:{appendChild(s){scripts.push(s)}},createElement(){return {}},addEventListener(){},referrer:'',documentElement:{lang:'pl'}};
 const window={HornigoldGA4:{enabled:true,measurementId:'G-TEST123'},HornigoldPrivacy:{allowsAnalytics:()=>allow},addEventListener(name,fn){listeners[name]=fn}};
 vm.runInNewContext(source,{window,document,location:{origin,pathname:'/pl/',search:'',reload(){reloads++}},URL,URLSearchParams});
 return {writes,scripts,window,listeners,setAllow(value){allow=value},reloads:()=>reloads};
}
test('CMP reports no valid analytics consent: stale cookies removed before any tag load',()=>{const r=run();assert.equal(r.writes.length,6);assert.ok(r.writes.every(v=>v.startsWith('_ga')&&v.includes('Max-Age=0')));assert.equal(r.scripts.length,0);assert.equal(r.reloads(),0);assert.equal(r.window['ga-disable-G-TEST123'],true)});
test('valid consent loads once; withdrawal clears cookies and disables collection',()=>{const r=run({allow:true});assert.equal(r.writes.length,0);assert.equal(r.scripts.length,1);r.setAllow(false);r.listeners['hornigold:privacy']();assert.equal(r.writes.length,6);assert.equal(r.reloads(),1);assert.equal(r.window['ga-disable-G-TEST123'],true)});
test('preview cannot load tracking',()=>{const r=run({origin:'https://kamilkita-ux.github.io',allow:true});assert.equal(r.scripts.length,0);assert.equal(r.writes.length,0)});
