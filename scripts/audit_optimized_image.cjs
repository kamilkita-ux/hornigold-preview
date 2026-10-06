// Focused regression after lossless image transcoding; local browsers only.
const fs=require('node:fs'),path=require('node:path');
const {chromium,firefox,webkit}=require('playwright');const {default:AxeBuilder}=require('@axe-core/playwright');
const root=path.resolve(__dirname,'..');const base=process.env.AUDIT_URL||'http://127.0.0.1:4352';
if(!['127.0.0.1','localhost'].includes(new URL(base).hostname))throw Error('Local QA only');
const source=fs.readFileSync(root+'/site/pl/miasto-i-okolice/index.html','utf8');
const routes=[...source.matchAll(/<link href="https:\/\/hornigold.pl([^"]+)" hreflang="([^"]+)" rel="alternate"/g)].filter(x=>x[2]!=='x-default').map(x=>x[1]);
if(routes.length!==7)throw Error('Expected seven equivalent city routes');
const results=[];
(async()=>{for(const [engine,type] of Object.entries({chromium,firefox,webkit})){
 const browser=await type.launch({headless:true});for(const width of [375,1366]){
  const context=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();for(const route of routes){const errors=[];const handler=e=>errors.push(e.message);page.on('pageerror',handler);
   try{await page.goto(base+route,{waitUntil:'load'});const info=await page.evaluate(async()=>{const i=document.querySelector('img[src*="katowice-editorial-lossless.webp"]');if(!i)throw Error('Optimized image missing');await i.decode();return {width:i.naturalWidth,height:i.naturalHeight,alt:i.alt,overflow:document.documentElement.scrollWidth>innerWidth+1}});
    if(info.width!==1122||info.height!==1402||!info.alt||info.overflow)errors.push(JSON.stringify(info));
    const scan=engine==='chromium'?await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze():null;
    if(scan?.violations.length)errors.push(...scan.violations.map(x=>x.id));
   }catch(e){errors.push(e.message)}page.off('pageerror',handler);results.push({engine,width,route,errors});
  }await context.close();}await browser.close();}
 const report={date:new Date().toISOString(),cases:results.length,axeCases:14,failures:results.filter(x=>x.errors.length),results,limits:['Local emulated viewports only; image pixel equivalence verified separately']};
 fs.writeFileSync(root+'/docs/seo/optimized-image-regression.json',JSON.stringify(report,null,2));console.log(JSON.stringify({cases:report.cases,axeCases:14,failures:report.failures.length}));process.exitCode=report.failures.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
