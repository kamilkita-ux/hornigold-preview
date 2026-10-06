(() => {
  const supported = ['pl','en','de','zh-hans','uk','es','it'];
  let language = 'pl';
  try { const saved = localStorage.getItem('hornigold-language'); if(supported.includes(saved)) language = saved; } catch {}
  // Only an explicit saved choice changes the default. Direct language URLs are never redirected.
  const query = new URLSearchParams();
  const existing = new URLSearchParams(location.search);
  for(const key of ['arrival','departure','guests','room','utm_source','utm_medium','utm_campaign','utm_term','utm_content','gclid','gbraid','wbraid','fbclid']) {
    const value=existing.get(key);if(value&&value.length<=512)query.set(key,value);
  }
  location.replace('/'+language+'/'+(query.size?'?'+query:'')+location.hash);
})();
