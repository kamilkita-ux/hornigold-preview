import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const source=fs.readFileSync(new URL('../site/assets/analytics.js',import.meta.url),'utf8');
function fixture({origin='https://hornigold.pl',enabled=true,id='G-TEST123',consent=false,search='?guests=2&email=private'}={}){
 const listeners={},scripts=[];let allowed=consent,reloads=0,cookies='_ga=sample; _ga_TEST=sample';
 const window={HornigoldGA4:{enabled,measurementId:id},HornigoldPrivacy:{allowsAnalytics:()=>allowed},addEventListener:(name,fn)=>listeners[name]=fn};
 const document={addEventListener:(name,fn)=>listeners['document:'+name]=fn,referrer:'',get cookie(){return cookies},set cookie(value){cookies=value},createElement:()=>({}),head:{appendChild:s=>scripts.push(s)}};
 vm.runInNewContext(source,{window,document,location:{origin,pathname:'/pl/',search,reload:()=>reloads++},Date,URL,URLSearchParams});
 return {window,scripts,change(value){allowed=value;listeners['hornigold:privacy']?.()},reloads:()=>reloads,cookies:()=>cookies,click(href,stay=false){listeners['document:click']?.({target:{closest:()=>({getAttribute:()=>href,hasAttribute:()=>stay})}})}};
}
test('no tag before consent or after refusal',()=>{const f=fixture();f.change(false);assert.equal(f.scripts.length,0)});
test('preview, missing ID and disabled configuration do not load Google',()=>{for(const options of [{origin:'https://kamilkita-ux.github.io'},{id:''},{enabled:false}])assert.equal(fixture({...options,consent:true}).scripts.length,0)});
test('consent loads exactly one tag and a sanitized page view',()=>{const f=fixture();f.change(true);f.change(true);assert.equal(f.scripts.length,1);const events=f.window.dataLayer.filter(a=>a[0]==='event');assert.equal(events.length,1);assert.equal(events[0][2].page_location,'https://hornigold.pl/pl/');assert.equal(events[0][2].page_referrer,'');assert.equal(JSON.stringify(f.window.dataLayer).includes('email='),false)});
test('withdrawal disables measurement, removes GA cookies and reloads',()=>{const f=fixture({consent:true});f.change(false);assert.equal(f.window['ga-disable-G-TEST123'],true);assert.match(f.cookies(),/Max-Age=0/);assert.equal(f.reloads(),1)});

test('only approved campaign labels survive URL sanitization',()=>{const f=fixture({consent:true,search:'?utm_source=instagram&utm_medium=organic_social&utm_campaign=profile&email=private&guests=3'});const event=f.window.dataLayer.find(a=>a[0]==='event');assert.equal(event[2].page_location,'https://hornigold.pl/pl/?utm_source=instagram&utm_medium=organic_social&utm_campaign=profile');});
test('contact and social clicks require consent and never send destinations',()=>{const f=fixture();f.click('mailto:private@example.com');assert.equal(f.window.dataLayer.filter(a=>a[0]==='event').length,0);f.change(true);f.click('mailto:private@example.com');f.click('tel:+48123456789');f.click('https://www.instagram.com/hornigold.apartments/');f.click('/pl/pobyt/',true);const events=f.window.dataLayer.filter(a=>a[0]==='event');assert.equal(events.length,5);assert.equal(JSON.stringify(events).includes('private@example'),false);assert.equal(JSON.stringify(events).includes('123456789'),false);assert.equal(events.at(-1)[1],'stay_planner_click');});
