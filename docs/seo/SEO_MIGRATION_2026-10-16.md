# Migracja SEO Hornigold — stan na 16.10.2026

## Wynik kontroli publicznej

| Obszar | Wynik | Dowód |
|---|---|---|
| Domena kanoniczna | `https://hornigold.pl/pl/` zwraca 200 | publiczny odczyt HTTP, 16.10.2026 |
| wariant główny | `/` → `/pl/` 301 → 200 | publiczny odczyt HTTP |
| HTTP i `www` | prowadzą do HTTPS bez `www`, z zachowaniem ścieżki | publiczny odczyt HTTP |
| robots | zezwala na indeksację strony, blokuje wyłącznie `/api/`, wskazuje sitemap | `https://hornigold.pl/robots.txt` |
| sitemap | 529 adresów kanonicznej domeny, bez hostów podglądowych | publiczny odczyt `sitemap.xml` |
| podgląd GitHub Pages | `Disallow: /` i `noindex,nofollow,noarchive` | publiczny odczyt 16.10.2026 |
| klasyczny WordPress | `/wp-login.php`, `/wp-admin/`, `/wp-sitemap.xml`, `/sitemap_index.xml`, `/feed/` zwracają 404 | publiczny odczyt HTTP |

## Inwentaryzacja i decyzje

| Grupa starych URL | Źródło i data | Stan publiczny 16.10 | Cel / działanie | Stan |
|---|---|---:|---|---|
| `/`, HTTP oraz `www` | publiczny odczyt, 16.10 | 301 → 200 | `/pl/` | wdrożone publicznie |
| 539 wcześniejszych ścieżek językowych | `server/routes.mjs`, lokalna inwentaryzacja | reprezentatywne próbki: 301 → 200 | najbliższy odpowiednik językowy | wdrożone w aktualnej aplikacji; pełny publiczny przebieg wymaga osobnego smoke-testu |
| `?portfolio-item=` — 9 znanych kategorii | `hornigold-next/ops/migration-map.json`, 05.10 | obecnie ogólny 301 na `/pl/` | precyzyjny 301 do odpowiedniej kategorii pokoju | przygotowane lokalnie do wdrożenia |
| `?page_id=` — 10 potwierdzonych treści | `hornigold-next/ops/migration-map.json` i `legacy-migration.json`, 05.10 | obecnie ogólny 301 na `/pl/` | precyzyjny 301 do strony o zgodnej intencji | przygotowane lokalnie do wdrożenia |
| nieznane `page_id` / `portfolio-item` | Search Console raportuje 1 200 adresów 404, stan 12.10 | dotąd ogólny 301 na `/pl/` dla URL głównego | 410 Gone, bez zastępowania stroną główną | przygotowane lokalnie do wdrożenia |
| `apartamenty.hornigold.pl` | DNS/publiczny odczyt, 16.10 | 404 z dawnego hosta | pozostawić 404 do czasu poznania historycznych URL i logów; nie kierować masowo na główną | potwierdzone publicznie |
| aliasy `hornigold.com.pl`, `hotel-hornigold.com.pl`, `hotel-hornigold.pl`, `zielona-kamienica.hornigold.pl` | audyt INTEN 15.10, DNS 16.10 | brak publicznego DNS | wymagają potwierdzenia aktywnej rejestracji i decyzji o przywróceniu DNS tylko dla kontrolowanego 301 | niezweryfikowane poza DNS |

## Search Console — stan początkowy

Właściwość `https://hornigold.pl/` jest dostępna na koncie `hotelhornigold@gmail.com`.

* Raport skuteczności za 8–13.10: 51 kliknięć, 489 wyświetleń, CTR 10,4%, średnia pozycja 4.
* Zgłoszona mapa `/sitemap.xml`: sukces; zgłoszona 11.10, odczytana 14.10, 462 wykryte strony.
* Raport stron (aktualizacja 12.10): 68 zindeksowanych; 3,4 tys. niezaindeksowanych. Największe grupy: 2 127 alternatyw kanonicznych, 1 200 adresów 404, 50 zeskanowanych lecz niezaindeksowanych, 2 adresy z przekierowaniem.

Te liczby są raportem Google o historycznie znanych adresach — nie są listą adresów, które aktualnie zwracają 200.

## Zmiana kodu i rollback

Zmiana w `server/production-entry.mjs` używa jawnej listy w `server/legacy-wordpress-redirects.mjs`.

* Potwierdzone stare adresy otrzymują 301 do treściowo najbliższego adresu.
* Parametry kampanii są zachowywane, a `page_id`, `portfolio-item` oraz `lang` są usuwane.
* Nieznany, historyczny identyfikator otrzymuje 410 oraz `X-Robots-Tag: noindex, nofollow, noarchive`.
* Rezerwacje, Fiserv, webhooki, API i ich ścieżki nie są objęte regułą: dotyczy wyłącznie `GET`/`HEAD` pod `/` z historycznymi parametrami WordPressa.

Rollback: wycofać import `legacyWordpressRedirect` oraz przywrócić wcześniejszy blok obsługi `/` w `server/production-entry.mjs`; nie zmieniać DNS, poczty, Cloudflare bindings ani integracji rezerwacyjnej.

## Dalsze czynności po potwierdzonym wdrożeniu

1. Publicznie przetestować wszystkie potwierdzone query-URL oraz pięć nieznanych identyfikatorów.
2. W Search Console sprawdzić reprezentatywne stare i nowe URL narzędziem kontroli adresu.
3. Nie używać globalnego usuwania URL. Istniejąca mapa witryny jest już zgłoszona; ponowna wysyłka ma sens tylko po zmianie jej zawartości.
4. Po 2–6 tygodniach porównać liczbę 404 i „stron z przekierowaniem”.
