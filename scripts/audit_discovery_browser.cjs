// Local regression for all fourteen updated pages, seven languages, two widths.
const fs=require('node:fs'),path=require('node:path');
const {chromium,firefox,webkit}=require('playwright');
const {default:AxeBuilder}=require('@axe-core/playwright');
const root=path.resolve(__dirname,'..'),base='http://127.0.0.1:4355';
const release=JSON.parse(fs.readFileSync(root+'/_site/release.json','utf8'));
const routes=[];
for(const key of ['informacje','faq']){
 const html=fs.readFileSync(root+'/site/pl/'+key+'/index.html','utf8');
 for(const match of html.matchAll(/<link href="https:\/\/hornigold.pl([^"]+)" hreflang="([^"]+)" rel="alternate"/g)){
  if(match[2]!=='x-default')routes.push({route:match[1],lang:match[2]});
 }
}
if(routes.length!==14)throw Error('Expected fourteen routes');
const results=[];
(async()=>{
 for(const [engine,type] of Object.entries({chromium,firefox,webkit})){
  const browser=await type.launch({headless:true});
  for(const width of [375,1366]){
   const context=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
   await context.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());
   const page=await context.newPage();
   for(const {route,lang} of routes){
    const errors=[];const handler=e=>errors.push(e.message);page.on('pageerror',handler);
    try{
     const response=await page.goto(base+release.base+route.slice(1),{waitUntil:'load'});
     if(response.status()!==200)errors.push('HTTP '+response.status());
     const details=page.locator('[data-discovery-content] details');
     for(let n=0;n<await details.count();n++)await details.nth(n).locator('summary').click();
     const state=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,sections:document.querySelectorAll('[data-discovery-content]').length,lang:document.documentElement.lang,h1:document.querySelectorAll('h1').length}));
     if(state.overflow||state.sections!==1||state.lang!==lang||state.h1!==1)errors.push(JSON.stringify(state));
     if(engine==='chromium'){
      const scan=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
      errors.push(...scan.violations.map(x=>x.id));
     }
     if(engine==='chromium'&&lang==='pl')await page.screenshot({path:root+'/docs/seo/discovery-'+(route.includes('/faq/')?'faq':'info')+'-'+width+'.png',fullPage:true});
    }catch(e){errors.push(e.message)}
    page.off('pageerror',handler);results.push({engine,width,route,lang,errors});
   }
   await context.close();
  }
  await browser.close();
 }
 const report={date:new Date().toISOString(),cases:results.length,axeCases:28,failures:results.filter(x=>x.errors.length),results,limits:['Emulated local viewports; not a complete manual accessibility audit.']};
 fs.writeFileSync(root+'/docs/seo/discovery-browser.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({cases:report.cases,axeCases:28,failures:report.failures.length}));process.exitCode=report.failures.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
