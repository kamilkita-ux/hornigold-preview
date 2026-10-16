# Snapshot rollbacku — przed migracją SEO 16.10.2026

Ten plik jest kopią **wcześniejszej logiki źródłowej** dla obsługi `GET` i `HEAD` pod `/` w `server/production-entry.mjs`. Nie jest kopią ustawień Cloudflare, nie zmienia DNS, poczty ani bindingów.

```js
if (production && url.pathname === '/' && ['GET', 'HEAD'].includes(request.method)) {
  const query = new URLSearchParams(url.search);
  query.delete('lang');
  query.delete('page_id');
  const target = new URL('/pl/', ORIGIN);
  target.search = query;
  return Response.redirect(target.href, 301);
}
```

Rollback zmiany migracyjnej: przywrócić powyższy blok, usunąć import oraz użycie `legacyWordpressRedirect`, a następnie przygotować nowy artefakt Cloudflare i wykonać publiczny odczyt kontrolny. Nie usuwać historii ani backupów.
