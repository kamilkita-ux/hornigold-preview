import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const code=fs.readFileSync(new URL('../site/assets/google-ads.js',import.meta.url),'utf8');
function fixture({origin='https://hornigold.pl',marketing=false,analytics=false,existing=false}={}){
 let allowed=marketing;const scripts=[],handlers={},cookies=[],reloads=[];
 const window={HornigoldGA4:{enabled:true},HornigoldPrivacy:{allowsMarketing:()=>allowed,allowsAnalytics:()=>analytics},addEventListener:(n,f)=>handlers[n]=f};
 const document={get cookie(){return '_gcl_aw=old; _ga=keep'},set cookie(v){cookies.push(v)},querySelector:()=>existing||scripts.length?{}:null,createElement:()=>({setAttribute(){}}),head:{appendChild:s=>scripts.push(s)}};
 vm.runInNewContext(code,{window,document,location:{origin,pathname:'/pl/',search:'?email=private&arrival=secret',reload:()=>reloads.push(true)},Date});
 return {window,scripts,cookies,reloads,allow(v){allowed=v;handlers['hornigold:privacy']?.()},commands:()=>Array.from(window.dataLayer||[],a=>Array.from(a))};
}
test('no advertising script or config before separate consent; analytics consent alone insufficient',()=>{for(const analytics of [false,true]){const f=fixture({analytics});assert.equal(f.scripts.length,0);assert.equal(f.commands().filter(a=>a[0]==='config').length,0);assert.ok(f.cookies.some(v=>v.startsWith('_gcl_aw=;')))}});
test('marketing consent configures supplied Ads ID once without private URL parameters',()=>{const f=fixture();f.allow(true);f.allow(true);assert.equal(f.scripts.length,1);assert.ok(f.scripts[0].src.endsWith('AW-18507796156'));const config=f.commands().find(a=>a[0]==='config');assert.equal(config[1],'AW-18507796156');assert.equal(config[2].page_location,'https://hornigold.pl/pl/');assert.equal(config[2].allow_ad_personalization_signals,false);assert.ok(!JSON.stringify(f.commands()).includes('secret'))});
test('withdrawal clears advertising cookies and reloads loaded context',()=>{const f=fixture({marketing:true});f.allow(false);assert.equal(f.reloads.length,1);assert.ok(f.cookies.length);assert.ok(f.cookies.every(v=>!v.startsWith('_ga=')))});
test('previews never load or configure Ads',()=>{const f=fixture({origin:'https://kamilkita-ux.github.io',marketing:true});assert.equal(f.commands().length,0);assert.equal(f.scripts.length,0)});
test('existing GA4 loader is reused',()=>{const f=fixture({marketing:true,existing:true});assert.equal(f.scripts.length,0);assert.equal(f.commands().filter(a=>a[0]==='config').length,1)});
test('Ads commands use the Google tag Arguments protocol rather than array records',()=>{const f=fixture({marketing:true});assert.ok(f.window.dataLayer.length>=5);assert.ok(f.window.dataLayer.every(command=>Object.prototype.toString.call(command)==='[object Arguments]'));assert.ok(f.commands().some(command=>command[0]==='config'&&command[1]==='AW-18507796156'));});
test('production CSP permits the documented Ads endpoints without weakening preview',async()=>{
 const worker=(await import('../_cloudflare_production/server/production-entry.mjs')).default;
 const env={ASSETS:{fetch:async()=>new Response('<html><body>Page</body></html>',{headers:{'Content-Type':'text/html'}})}};
 const response=await worker.fetch(new Request('https://hornigold.pl/pl/'),env);const csp=response.headers.get('Content-Security-Policy');
 for(const host of ['https://www.googleadservices.com','https://pagead2.googlesyndication.com','https://ad.doubleclick.net','https://www.googletagmanager.com','https://www.google.pl'])assert.ok(csp.includes(host));
 assert.ok(!csp.includes('unsafe-eval'));assert.ok(!/script-src[^;]*unsafe-inline/.test(csp));
 const preview=await worker.fetch(new Request('https://kamilkita-ux.github.io/pl/'),env);assert.ok(!preview.headers.get('Content-Security-Policy').includes('googleadservices'));
});
