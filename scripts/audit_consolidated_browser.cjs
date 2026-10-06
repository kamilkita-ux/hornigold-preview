const fs=require('fs'),path=require('path');const {chromium,firefox,webkit}=require('playwright');
const base=process.env.AUDIT_URL||'http://127.0.0.1:4334',results=[];
(async()=>{for(const [engine,type] of Object.entries({chromium,firefox,webkit})){const b=await type.launch();for(const lang of ['pl','en','de','zh-hans','uk','es','it'])for(const width of [375,1366]){const c=await b.newContext({viewport:{width,height:900}});let calls=0;await c.route('**/api/site-stats',r=>{calls++;return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({total:1234,metric:'pageviews',startedAt:'2026-10-05'})})});const p=await c.newPage();try{
 await p.goto(base+'/'+lang+'/club-hornigold/');await p.waitForFunction(()=>!document.querySelector('[data-view-count]').hidden);if(calls!==1)throw Error('counter duplicated');
 if(await p.locator('main article.guide-step').count()!==4)throw Error('club benefits missing');
 if(!await p.locator('main a[href^="mailto:"]').first().isVisible())throw Error('club contact missing');
 if(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('overflow');
 if(await p.locator('footer [data-club-link]').count()!==1)throw Error('club footer link');
 await p.evaluate(()=>document.dispatchEvent(new Event('visibilitychange')));if(calls!==1)throw Error('count on visibility replay');
 await c.unroute('**/api/site-stats');await c.route('**/api/site-stats',r=>r.fulfill({status:503,contentType:'application/json',body:'{}'}));await p.reload();await p.waitForFunction(()=>!document.querySelector('[data-view-unavailable]').hidden);if(!await p.locator('[data-view-count]').isHidden())throw Error('fabricated count');
 if(lang==='pl'&&engine==='chromium')await p.screenshot({path:'/tmp/hornigold-club-'+width+'.png',fullPage:true});
 results.push({engine,lang,width,pass:true});
 }catch(e){results.push({engine,lang,width,error:e.message})}await c.close();}await b.close();}
const report={cases:results.length,results,failures:results.filter(x=>!x.pass),counterRequestsMocked:true};fs.writeFileSync('/tmp/hornigold-consolidated-interactions.json',JSON.stringify(report,null,2));console.log(JSON.stringify({cases:report.cases,failures:report.failures}));process.exitCode=report.failures.length?1:0;})();
