// Headless app QA; isolated browser contexts, no personal browser/profile access.
const fs=require('node:fs');const path=require('node:path');
const {chromium,firefox,webkit}=require('playwright');
const base=process.env.AUDIT_URL||'http://127.0.0.1:4329/';
const root=path.resolve(__dirname,'..');const report={started:new Date().toISOString(),base,cases:[],failures:[],limits:['Emulated viewports; not physical devices','WebKit is not the released Safari app','Automated checks are not a full WCAG or linguistic certification']};
const plRoutes=['/pl/','/pl/pokoje/','/pl/pokoje/classic/','/pl/lokalizacja/','/pl/kontakt/','/pl/dokumenty/','/pl/miasto-i-okolice/','/pl/miasto-i-okolice/ilustracje/','/pl/miasto-i-okolice/gastronomia/','/pl/pobyt/','/pl/rezerwacja/','/pl/faq/'];
function localized(route){const html=fs.readFileSync(path.join(root,'site',decodeURI(route),'index.html'),'utf8');return [...html.matchAll(/<link href="https:\/\/hornigold.pl([^"]+)" hreflang="([^"]+)" rel="alternate"/g)].filter(m=>m[2]!=='x-default').map(m=>({route:m[1],lang:m[2]}));}
const routes=plRoutes.flatMap(localized);const views=[{width:375,height:812},{width:768,height:1024},{width:1366,height:900}];
const urlFor=r=>base.replace(/\/$/,'')+r;
(async()=>{
for(const [engine,browserType] of Object.entries({chromium,firefox,webkit})){
 const browser=await browserType.launch({headless:true});
 for(const viewport of views){
 const context=await browser.newContext({viewport});const page=await context.newPage();let errors=[];
 page.on('pageerror',e=>errors.push('JS '+e.message));page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url())});page.on('console',m=>{if(m.type()==='error')errors.push('console '+m.text())});
 for(const {route,lang} of routes){errors=[];try{
 await page.goto(urlFor(route),{waitUntil:'load',timeout:30000});
 const info=await page.evaluate(()=>({lang:document.documentElement.lang,version:document.querySelector('[data-site-version]')?.textContent,banner:!!document.querySelector('.preview-bar'),overflow:document.documentElement.scrollWidth>innerWidth+1,missing:[...document.images].filter(i=>i.loading!=='lazy'&&(!i.complete||i.naturalWidth===0)).map(i=>i.src),languages:document.querySelectorAll('a[data-language]').length,noindex:document.querySelector('meta[name=robots]')?.content.includes('noindex')}));
 if(info.version!=='22'||info.lang!==lang||info.banner||info.languages!==7||!info.noindex||info.overflow||info.missing.length)errors.push(JSON.stringify(info));
 if(route==='/pl/'&&viewport.width===375){await page.screenshot({path:process.env.AUDIT_SHOTS?path.join(process.env.AUDIT_SHOTS,engine+'-mobile.png'):'/tmp/hornigold-'+engine+'-mobile.png',fullPage:false});}
 report.cases.push({engine,viewport,route,errors:[...errors]});
 }catch(e){report.cases.push({engine,viewport,route,errors:[e.message]})}}
 // Stay selection, equivalent-page switching, refresh and keyboard-accessible controls in each language.
 for(const {route,lang} of localized('/pl/')){try{
 await page.goto(urlFor(route));const form=page.locator('form[data-search]').first();
 await form.locator('input[name=arrival]').fill('2027-05-12');await form.locator('input[name=departure]').fill('2027-05-15');await form.locator('select[name=guests]').selectOption('3');
 await form.locator('button[type=submit]').click();await page.waitForLoadState();
 if(!page.url().includes('guests=3'))throw Error('stay not carried');
 if(viewport.width<=760)await page.locator('.language-picker > summary').click();
 const target=page.locator('a[data-language="en"]');await target.click();await page.waitForLoadState();await page.reload();
 const stay=await page.evaluate(()=>window.HornigoldStay.get());if(stay.arrival!=='2027-05-12'||stay.departure!=='2027-05-15'||stay.guests!=='3')throw Error('language/refresh loses stay');
 if(viewport.width<=760){const toggle=page.locator('.menu-toggle');await toggle.click();await page.keyboard.press('Escape');if(await toggle.getAttribute('aria-expanded')!=='false')throw Error('menu escape');}
 await page.keyboard.press('Tab');
 report.cases.push({engine,viewport,route,interaction:'dates-language-menu-refresh',errors:[]});
 }catch(e){report.cases.push({engine,viewport,route,interaction:true,errors:[e.message]})}}
 await context.close();
 }
 await browser.close();console.log(engine+' complete');
}
report.finished=new Date().toISOString();report.failures=report.cases.filter(c=>c.errors.length);fs.writeFileSync(process.env.AUDIT_OUTPUT||'/tmp/hornigold-browser-audit.json',JSON.stringify(report,null,2));console.log(JSON.stringify({cases:report.cases.length,failures:report.failures.length,examples:report.failures.slice(0,3)}));process.exitCode=report.failures.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
