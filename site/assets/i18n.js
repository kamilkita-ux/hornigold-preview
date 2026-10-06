(() => {
  'use strict';
  const tag = document.documentElement.lang;
  const language = tag === 'zh-Hans' ? 'zh-hans' : tag;
  const locales = {pl:'pl-PL',en:'en-GB',de:'de-DE','zh-hans':'zh-CN',uk:'uk-UA',es:'es-ES',it:'it-IT'};
  const t = (pl, en) => {
    if (language === 'pl') return pl;
    if (language === 'en') return en;
    const key = en.trim(), value = window.HornigoldMessages?.[key];
    if (typeof value !== 'string') throw new Error('Missing localized message: ' + key);
    return (en.match(/^\s*/)[0]) + value + (en.match(/\s*$/)[0]);
  };
  function setError(form,field,message){
    field.setAttribute('aria-invalid','true');
    const error=form.querySelector('.form-error');
    if(error){error.textContent=message;const ids=new Set((field.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean));ids.add(error.id);field.setAttribute('aria-describedby',[...ids].join(' '));}
    field.focus();
  }
  function validate(form) {
    for (const field of form.querySelectorAll('input,select,textarea')) {
      field.setCustomValidity(''); field.removeAttribute('aria-invalid');
      let message = '';
      if (field.validity.valueMissing) message = t('Uzupełnij to pole.', 'Please complete this field.');
      else if (field.type === 'date' && !field.validity.valid) message = t('Wybierz prawidłową datę.', 'Choose a valid date.');
      else if (!field.validity.valid) message = t('Wpisz liczbę całkowitą z dozwolonego zakresu.', 'Enter a whole number within the permitted range.');
      if (message) {
        field.setCustomValidity(message);setError(form,field,message);return false;
      }
    }
    return true;
  }
  document.querySelectorAll('form').forEach((form,index) => {
    form.noValidate = true;
    const error=form.querySelector('.form-error');if(error&&!error.id)error.id='form-error-'+index;
    form.addEventListener('input', e => {if(e.target.setCustomValidity){e.target.setCustomValidity('');e.target.removeAttribute('aria-invalid');if(error)error.textContent='';}});
  });
  document.querySelectorAll('[data-language]').forEach(link => link.addEventListener('click', () => {
    try { localStorage.setItem('hornigold-language', link.dataset.language); } catch {}
  }));
  window.HornigoldI18n = {language, locale:locales[language] || 'pl-PL', t, validate,setError};
})();
