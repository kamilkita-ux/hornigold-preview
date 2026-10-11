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


## Revision 23.10 — GA4 handoff, 2026-10-11

GitHub Pages remains a nontracking preview. Build production with `python3 scripts/build.py --mode production-ready --base / --counter --production-counter`, then `python3 scripts/prepare_cloudflare_production.py`. Preserve the actual existing ASSETS and DB bindings. Do not deploy `_site` to production. The production entrypoint includes Google tag/collection CSP exceptions only for hornigold.pl; both HTTP and HTML policies must match. `site/assets/analytics.js` is the tested runtime, injected only into production-ready HTML with generated analytics-config.js.

Verified new measurement ID: G-ZJ9VJNGHGT. This is a separate new property (558323228) and stream (16101873868); do not reuse or alter historical streams. Enhanced measurement was disabled when created; reread its current setting before launch because another administrator may have changed it. Disable automatic form/outbound tracking and Google Signals/advertising personalization. Analytics cookies are configured for 180 days without renewal; the recorded property retention is 14 months without resetting on new activity. Recheck actual settings and account-specific Google processing/transfer terms before live activation.

Run `node scripts/audit_ga4.cjs` with Playwright available. The test intercepts the Google tag and is not proof of GA receipt. On the public site verify zero Google requests before consent/refusal, one tag load after analytics consent, sanitized page_location/referrer, contact/planner/social click events, consent expiry and cross-tab withdrawal, cookie cleanup and no further collection after withdrawal. Then perform an explicitly consented GA4 DebugView/Realtime check. Check seven languages and 375/1366px layouts. Do not enable Meta, Ads, reservations or payments as part of this release. Contact clicks are not leads or purchases. Campaign URLs and the future PMS/payment measurement plan are in integrations/ga4/. No Google access permission or social account connection has been granted by this code.
