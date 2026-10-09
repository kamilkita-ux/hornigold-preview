# Hornigold.pl — pakiet SEO do kontroli Cloudflare

**Status:** GOTOWE DO KONTROLI MARKA — nie jest potwierdzeniem wdrożenia produkcyjnego.

## Źródło i kontrola jakości

- GitHub commit źródłowy: `43f46f6c247ef5db8a1558198d141a98a5f2af99`.
- Zbudowano 693 kanoniczne stron w trybie `production-ready`.
- Pakiet `_cloudflare_production/` ma 1 665 plików; SHA-256 manifestu: `cd140b531b18404851d16141600431006f9df2b04613506fd6198017b406898a`.
- Audyt SEO i audyt discoverability nie zgłosiły błędów.
- Testy serwera i bramki indeksacji: 26/26 poprawne. Testy SEO: 10/10 poprawne.

## Co wdrożyć w istniejącym projekcie Cloudflare

1. Użyć tylko istniejącego projektu, bindingów i historii licznika; nie tworzyć nowego Workera, bazy ani konfiguracji DNS.
2. Wprowadzić artefakt `_cloudflare_production/`, z entrypointem `server/production-entry.mjs`, katalogiem zasobów `assets` i istniejącym bindingiem `ASSETS`.
3. Zachować istniejący binding `DB`, `run_worker_first` oraz rzeczywiste odpowiedzi HTTP 404.
4. Dla `https://hornigold.pl` umożliwić indeksowanie wyłącznie stron kanonicznych i `sitemap.xml`.
5. Zachować `noindex` dla rootowej strony wyboru języka, API, PDF-ów, aliasów i 404.
6. Zachować blokadę indeksowania dla podglądów Sites, GitHub Pages i `workers.dev`.
7. Utrzymać 301 z `www.hornigold.pl` na `hornigold.pl` z pełną ścieżką i query stringiem.

## Kontrola po wdrożeniu

Marek potwierdza odczytem publicznym: 200 dla stron kanonicznych, brak `X-Robots-Tag: noindex` na nich, robots z `Allow: /`, sitemapę z 693 URL, zachowanie 301 z `www`, wyłączenia techniczne i niezmienione podglądy. Dopiero po tym można zgłosić sitemapę w Search Console.

Rezerwacje i płatności pozostają wyłączone.
