(() => {
 'use strict';
 const current=document.documentElement.lang.toLowerCase(),links=[...document.querySelectorAll('[data-language]')];
 let choice;try{choice=localStorage.getItem('hornigold-language');if(choice||sessionStorage.getItem('hornigold-language-suggestion-dismissed'))return;}catch{}
 const supported=['pl','en','de','zh-hans','uk','es','it'];
 const preferred=(navigator.languages||[navigator.language]).map(x=>x.toLowerCase()).map(x=>x.startsWith('zh')?'zh-hans':x.split('-')[0]).find(x=>supported.includes(x));
 if(!preferred||preferred===current)return;
 const peer=links.find(x=>x.dataset.language===preferred);if(!peer)return;
 const source=document.currentScript.src;
 fetch(new URL('browser-language.json',source)).then(r=>{if(!r.ok)throw Error();return r.json()}).then(labels=>{
  const text=labels[preferred],local=labels[current]||labels.pl;if(!text)return;
  const box=document.createElement('aside');box.className='browser-language-suggestion';box.setAttribute('aria-label',text[2]);
  const a=document.createElement('a');a.textContent=text[2];a.lang=preferred==='zh-hans'?'zh-Hans':preferred;a.href=peer.href;
  a.addEventListener('click',()=>{try{localStorage.setItem('hornigold-language',preferred)}catch{}});
  const button=document.createElement('button');button.type='button';button.textContent=local[3];button.addEventListener('click',()=>{try{localStorage.setItem('hornigold-language',current);sessionStorage.setItem('hornigold-language-suggestion-dismissed','1')}catch{}box.remove()});
  box.append(a,button);document.querySelector('header').after(box);
 }).catch(()=>{});
})();
