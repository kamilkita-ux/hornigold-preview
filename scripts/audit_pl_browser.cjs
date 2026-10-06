const fs=require('node:fs'),path=require('node:path'),{execFileSync}=require('node:child_process');
const {chromium}=require('playwright'),{default:AxeBuilder}=require('@axe-core/playwright');
const root=path.resolve(__dirname,'..'),origin='http://127.0.0.1:4356';
const release=JSON.parse(fs.readFileSync(root+'/_site/release.json'));
const files=execFileSync('git',['diff','--name-only','--','site/pl'],{cwd:root,encoding:'utf8'}).trim().split('\n').filter(x=>x.endsWith('/index.html'));
const results=[];
(async()=>{const browser=await chromium.launch();for(const width of [375,1366]){
 const context=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
 await context.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());
 const page=await context.newPage();
 for(const file of files){const route='/'+file.slice(5,-10),errors=[];const handler=e=>errors.push(e.message);page.on('pageerror',handler);
  try{const response=await page.goto(origin+release.base+route.slice(1),{waitUntil:'load'});if(response.status()!==200)errors.push('HTTP '+response.status());
   const state=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('h1').length,hiddenLinks:[...document.querySelectorAll('[data-local-intent-links] a')].some(x=>!x.getClientRects().length)}));
   if(state.overflow||state.h1!==1||state.hiddenLinks)errors.push(JSON.stringify(state));
   const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();errors.push(...axe.violations.map(x=>x.id));
   if(route==='/pl/pobyt/'||route==='/pl/pobyt/wydarzenie/')await page.screenshot({path:root+'/docs/seo/pl-'+(route.includes('wydarzenie')?'event':'stay')+'-'+width+'.png',fullPage:true});
  }catch(e){errors.push(e.message)}page.off('pageerror',handler);results.push({route,width,errors});
 }await context.close();}await browser.close();const report={date:new Date().toISOString(),pages:files.length,cases:results.length,axeCases:results.length,failures:results.filter(x=>x.errors.length),results,limits:['Local Chromium emulation only; not full manual WCAG certification or field metrics.']};fs.writeFileSync(root+'/docs/seo/pl-browser.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({pages:files.length,cases:results.length,failures:report.failures.length}));process.exitCode=report.failures.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
