import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const code=readFileSync(new URL('../site/assets/site-stats.js',import.meta.url),'utf8');
const texts=JSON.parse(readFileSync(new URL('../content/counter-labels.json',import.meta.url),'utf8'));
async function render(lang, data) {
  const label={textContent:texts[lang].neutral,dataset:{neutralLabel:texts[lang].neutral,sinceLabel:texts[lang].since}};
  const counter={hidden:true,textContent:''}, unavailable={hidden:false}, calls=[];
  const elements={'[data-view-count]':counter,'[data-view-unavailable]':unavailable,'[data-view-label]':label,'meta[name=hornigold-counter-endpoint]':{content:'/api/site-stats'}};
  vm.runInNewContext(code,{document:{querySelector:s=>elements[s],documentElement:{lang},visibilityState:'visible',addEventListener(){}},location:new URL('https://example.invalid/pl/'),URL,Intl,Date,AbortController,setTimeout,clearTimeout,fetch:async(url,options)=>{calls.push({url:String(url),options});return {ok:true,json:async()=>data};}});
  await new Promise(setImmediate);
  return {label,counter,unavailable,calls};
}

test('all eight locales use the API start date without an extra increment',async()=>{
  for(const lang of Object.keys(texts)) {
    const r=await render(lang,{total:1234,metric:'pageviews',startedAt:'2020-10-07'});
    assert.equal(r.counter.hidden,false,lang);
    assert.equal(r.unavailable.hidden,true,lang);
    assert.notEqual(r.label.textContent,texts[lang].neutral,lang);
    assert.match(r.label.textContent,/2020/,lang);
    assert.equal(r.label.textContent.includes('{date}'),false,lang);
    assert.equal(r.calls.length,1,lang);
    assert.equal(r.calls[0].options.method,'POST');
    assert.equal(r.calls[0].options.credentials,'omit');
    assert.equal(r.calls[0].options.headers['X-Hornigold-View'],'1');
  }
});

test('missing, invalid, impossible and future dates never display an invented start',async()=>{
  for(const startedAt of [undefined,null,'not a date','2020-02-30','2020-13-01','9999-01-01','<img src=x onerror=alert(1)>']) {
    const r=await render('pl',{total:12,metric:'pageviews',startedAt});
    assert.equal(r.label.textContent,texts.pl.neutral,String(startedAt));
    assert.equal(r.counter.hidden,false);
  }
});

test('invalid counts remain unavailable even when a date is supplied',async()=>{
  const r=await render('pl',{total:-1,metric:'pageviews',startedAt:'2020-10-07'});
  assert.equal(r.counter.hidden,true);
  assert.equal(r.unavailable.hidden,false);
  assert.equal(r.label.textContent,texts.pl.neutral);
});
