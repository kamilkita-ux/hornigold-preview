# Hornigold — wdrożenie Cloudflare Workers

Gałąź `deploy/cloudflare` (CloudMentor). Źródło treści bez zmian: `site/`, `server/`, `drizzle/` z `main` Kamila.
Ta gałąź dodaje tylko `wrangler.jsonc`, `scripts/cloudflare/` i ten plik. Wzorzec: wdrożenie FFP Inwestor
(`inwestor.farmyfotowoltaiki.pl`), ale na osobnym koncie Cloudflare `Hornigold`.

## Zasoby (od 7 października 2026 r.)

| Co | Wartość |
|---|---|
| Konto | `Hornigold` `ee23b9132a9692ab6c0e9f22aa86dda8` (osobne od FFP; przeniesione 7 października 2026 r.) |
| Worker | `hornigold` (`server/worker.mjs` + statyczne `_site/` jako `ASSETS`, `run_worker_first`) |
| D1 | `hornigold-counter` `bb927207-d7e2-4ebf-bbfa-a540704d6495`, region `eeur`, migracje `drizzle/` |
| Strefa | `hornigold.pl` `398f3b032a51a14d095ea3d82d25c821`, plan Free, SSL `full` |
| Adresy | `https://hornigold.pl` (Custom Domain Workera); `www` → 301 regułą Redirect na `hornigold.pl` |
| Adres techniczny | `https://hornigold.hornigold-cm.workers.dev` — wyłączony 9 października 2026 r. (`workers_dev: false`) |
| Stara strona PHP | `old.hornigold.pl` → `91.200.185.61` (proxied) |

Licznik odsłon liczy od zera od 7 października 2026 r. (`scripts/cloudflare/seed-counter.sql`); suma ze starego
Sites nie została przeniesiona — decyzja Marka.

## DNS

Strefa odtworzona 1:1 z serwerów `ns*.inten.pl` (7 października 2026 r.): poczta Microsoft 365 (MX, SPF z
Profitroom, DKIM `selector1/2`, DMARC, autodiscover, Lync/SIP SRV, Intune), `mail/pop/smtp/ftp` → `91.200.185.61`
bez proxy. Rekordy z eksportu inten.pl także `apartamenty`, `_domainkey`, `x._domainkey`; stare `_acme-challenge` pominięte. Definicja: `scripts/cloudflare/zone-hornigold.json`. Apeks obsługuje Custom Domain, `www` = `192.0.2.1` proxied tylko pod
przekierowanie.

**Aktywacja**: u rejestratora zmienić serwery nazw `ns.inten.pl, ns2.inten.pl, ns3.inten.pl` na
`vera.ns.cloudflare.com` i `weston.ns.cloudflare.com`. Dopiero wtedy `hornigold.pl` zaczyna wskazywać na
Workera. Po aktywacji sprawdzić: HTTPS apeksu i `www` (301), pocztę (wysłanie i odbiór), `old.hornigold.pl`,
licznik `/api/site-stats`. Potem `workers_dev: false` i ponowny deploy.

**Wycofanie**: przywrócić NS inten.pl u rejestratora (stara strefa nie była zmieniana) albo w Cloudflare usunąć
Custom Domain i dodać `A hornigold.pl 91.200.185.61` proxied.

## Wdrożenie nowej wersji z `main`

Na Windows w Git Bash: `MSYS_NO_PATHCONV=1` (inaczej `--base /` zamienia się na ścieżkę Gita) i
`core.autocrlf=false` w repo (pliki mają być LF).

```sh
git fetch origin && git merge origin/main          # w C:\dev\hornigold-cloudflare
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # raz
export MSYS_NO_PATHCONV=1 PYTHONUTF8=1
GITHUB_SHA=$(git rev-parse HEAD) .venv/Scripts/python scripts/build.py --base / --counter
.venv/Scripts/python scripts/audit_static.py --base /
node --test tests/server.test.mjs
npx wrangler d1 migrations apply hornigold-counter --remote   # tylko gdy przybyło coś w drizzle/
npx wrangler deploy
```

Smoke: `/`, `/pl/`, `/pl/nie-ma-takiej` (404), `/release.json` (wersja i commit), `/api/site-stats`,
jeden adres z `server/routes.mjs` (301 z zachowaniem parametrów), nagłówek `X-Robots-Tag`.

## Granice

- Build w trybie `preview`: `noindex` i `Disallow: /` zostają, dopóki właściciel osobno nie zgodzi się na
  indeksowanie (`README.md`, `SEO_PRODUCTION_HANDOFF.md`). Tryb `production-ready` nie ma licznika i nie jest
  tu wdrażany.
- Rezerwacje i płatności wyłączone. PMS/Fiserv: `docs/PMS-FISERV.md` — osobne wdrożenie po umowach z dostawcami.
- Sites Kamila i GitHub Pages działają dalej niezależnie od tego wdrożenia.

## Stan przejściowy (7–9 października 2026 r.) — cofnięty 9 października

Inten wpisał `vera`/`weston` jako rekordy NS w swojej strefie, ale nie zmienił delegacji w NASK (rejestr nadal
`ns.inten.pl`, `ns2.inten.pl`). Resolwery dostawały mieszane NS, a nieaktywna strefa Cloudflare nie miała adresu
IPv4 dla apeksu. Za zgodą Marka strefa w Cloudflare tymczasowo odpowiada tak jak inten:

- Custom Domain `hornigold.pl` odpięta od Workera; `A hornigold.pl 91.200.185.61` bez proxy, TTL 300;
- `www` → `91.200.185.61` bez proxy (zamiast `192.0.2.1` proxied + Redirect); `old` bez proxy.

**Nie robić `wrangler deploy` przed aktywacją strefy** — `routes` w `wrangler.jsonc` ponownie podepnie apeks.
Po aktywacji (rejestr .pl wskazuje `vera`/`weston`, strefa `active`): usunąć tymczasowy `A` apeksu, `www` z
powrotem na `192.0.2.1` proxied, `old` proxied, `workers_dev: false`, `npx wrangler deploy` (podpina Custom Domain),
smoke testy.

**8 października 2026 r.:** rejestratorem hornigold.pl jest Netium.pl sp. z o.o. (WHOIS NASK, ostatnia modyfikacja
2026-04-07) — inten obsługuje tylko DNS i hosting, więc delegację na `vera`/`weston` trzeba zmienić w Netium.
Usunięcie adresów IP w strefie inten nie aktywuje Cloudflare (aktywacja zależy wyłącznie od delegacji w NASK).

## Aktywacja strefy (9 października 2026 r.)

Marek zmienił delegację w Netium; rejestr .pl (`a-dns.pl`) wskazuje `vera`/`weston`. Po `PUT /zones/…/activation_check`
strefa `active` od 09:19 UTC, certyfikat Universal SSL (`hornigold.pl`, `*.hornigold.pl`) wydany. Stan przejściowy
cofnięty za zgodą Marka: usunięty tymczasowy `A hornigold.pl 91.200.185.61`, `www` → `192.0.2.1` proxied (reguła
Redirect 301 zachowuje ścieżkę i parametry), `old` proxied, `workers_dev: false`. Wdrożona wersja Kamila 23.9
(`origin/main` `b40f5b5` scalone do `deploy/cloudflare`, 693 strony w 7 językach, audyt bez błędów, `tests/server.test.mjs`
6/6), Worker `be6953c5-5225-4d96-b329-bf7d3c464938`, Custom Domain `hornigold.pl` podpięta. Przerwa apeksu ok. minuty
(między usunięciem rekordu a deployem).

Smoke: `/`, `/pl/` 200, `/pl/nie-ma-takiej` 404, `www` 301 z parametrami, stary adres `/de/catering/` 301 z `utm_*`,
`/release.json` wersja 23 / `stage: review` / `indexing: false`, `/api/site-stats` 200, `X-Robots-Tag: noindex`,
`robots.txt` `Disallow: /`, `old.hornigold.pl` 200, `workers.dev` 404. Poczta: MX, SPF, DKIM `selector1/2`, DMARC,
autodiscover na serwerach Cloudflare bez zmian. Do decyzji: `always_use_https` w strefie jest `off` (HTTP apeksu
odpowiada 200 zamiast 301 na HTTPS).

**Uwaga do deployu z sesji Claude Code:** reguła `Bash(npx wrangler deploy*)` pasuje tylko do polecenia zaczynającego
się od `npx wrangler deploy` — z innego katalogu używać `npx wrangler deploy --config C:/dev/hornigold-cloudflare/wrangler.jsonc`.

## Dane w UE i zabezpieczenia (9 października 2026 r.)

Na prośbę Marka („całkowicie w EU”) w granicach planu Free:

- **D1 z jurysdykcją EU:** nowa baza `hornigold-counter-eu` `23c8ca98-7e50-4a5f-98a1-1a0bfbebde7e` (`jurisdiction: eu` — baza działa i przechowuje dane wyłącznie w UE; jurysdykcji nie da się dodać istniejącej bazie). Skopiowane `d1_migrations` i licznik (`total` 2). Stara `hornigold-counter` (`bb927207…`, tylko wskazówka `eeur`) zostaje jako kopia — do usunięcia decyzją Marka.
- **Wykonywanie Workera:** `placement.region = gcp:europe-central2` (centrum danych Cloudflare najbliższe Warszawie; API: `placement_mode: targeted`). To wskazówka, nie gwarancja; TLS kończy się w centrum danych najbliższym odwiedzającemu.
- **Strefa:** `min_tls_version` 1.2, `always_use_https` on, HSTS `max-age=31536000` bez `includeSubDomains` i bez preload (subdomeny poczty i `old` nie są objęte), DNSSEC włączony — **status `pending` do czasu wpisania rekordu DS u rejestratora (Netium):** `hornigold.pl. 3600 IN DS 2371 13 2 5A760E3F2AF39F426E90AC2646039FAE4F196605F5E05F444E0F9919E3C504C9`.
- Worker `2e24247c-7e31-485c-9fbf-1061d6a78b06`.

Poza zasięgiem planu Free (Enterprise Data Localization Suite): Regional Services (TLS i wykonywanie tylko w UE) oraz Customer Metadata Boundary (logi i analityka tylko w UE). Workers Logs (`observability`) pozostają włączone — wyłączenie zablokował filtr uprawnień sesji; decyzja Marka.

## Produkcja z indeksowaniem (9 października 2026 r., wieczór)

Kamil (PR #1, `75f7095`/`37a7a67`) przygotował paczkę produkcyjną z indeksowaniem hornigold.pl — zgoda właściciela opisana w `README.md` i `docs/CLOUDFLARE_SEO_DEPLOYMENT_2026-10-09.md`. Wdrożenie w istniejącym Workerze `hornigold`, z tym samym D1 (`hornigold-counter-eu`) i domeną; bez zmian DNS, poczty, rezerwacji i płatności.

Build (Windows, Git Bash, `MSYS_NO_PATHCONV=1 PYTHONUTF8=1`):

```sh
GITHUB_SHA=$(git rev-parse HEAD) .venv/Scripts/python scripts/build.py --mode production-ready --base / --counter --production-counter
.venv/Scripts/python scripts/audit_seo.py --mode production-ready
.venv/Scripts/python scripts/audit_discovery.py --mode production-ready
.venv/Scripts/python scripts/prepare_cloudflare_production.py      # -> _cloudflare_production/ (gitignored)
node --test tests/production-indexing.test.mjs tests/server.test.mjs
.venv/Scripts/python -m unittest discover -s tests -p 'test_seo*.py'
npx wrangler deploy --config C:/dev/hornigold-cloudflare/wrangler.jsonc
```

`wrangler.jsonc`: `main` = `_cloudflare_production/server/production-entry.mjs`, `assets.directory` = `_cloudflare_production/assets` (`run_worker_first`, `404-page` bez zmian). Tryb `preview` (`_site/`) nie jest już wdrażany.

**Poprawka Windows w `scripts/seo.py` (do przeniesienia przez Kamila):** `route_for_file` składał trasę przez `str(path.relative_to(...))` — na Windows `\pl\` zamiast `/pl/`, żadna strona nie pasowała do `routes.json` i build produkcyjny dawał 693× `noindex` (błąd „indexing” w `build.py`). Zmienione na `.as_posix()`.

Wynik: build 693 stron, `audit_seo`/`audit_discovery` bez błędów, testy 26/26 i 10/10. Worker `bc527290-e755-4ce7-83b4-16f8acee67fd` (poprzedni `2e24247c` — rollback). Odczyt z produkcji: `robots.txt` `Allow: /`, `Disallow: /api/`, `Sitemap`; kanoniczne strony `index,follow` bez `X-Robots-Tag` (także 304); 404, aliasy 301, `/api/`, PDF i `/` (przekierowanie języka) z `noindex`; `release.json` `indexing: true`, `bookingEnabled/paymentsEnabled: false`; `www` 301 z parametrami. Zgłoszenie mapy strony w Google Search Console / Bing — po stronie właściciela (dostęp do kont niepotwierdzony).

## Rezerwacje GuestSage (9 października 2026 r.)

Hotel sprzedaje pobyty przez hostowany **GuestSage AI Booking Engine** (KWHotel), identyfikator obiektu `c98ead00-c7fd-4013-bb45-f19539b932d4`; silnik, ceny, płatności i regulamin są skonfigurowane po stronie hotelu, zarząd zgodził się na start (potwierdzenie Marka). Wersja minimalna — przekazanie linkiem, bez obcych skryptów i bez zmian CSP:

- `site/assets/booking.js` buduje adres `https://be.guestsage.com/{język}/{obiekt}/offers?arrivalDate&departureDate&personsCount` z `HornigoldStay` (bez dat → strona główna silnika; `zh-hans` → `en`; mapa pokoi `ROOMS` pusta do czasu otrzymania `featuredRoomTypeId` z panelu KWHotel).
- 7 podstron `rezerwacja/`: blok „Zarezerwuj online” z przyciskiem (`a[data-booking]`, działa bez JS); tekst pomocy formularzy pobytu (strony główne i `pobyt/`) zmieniony. Zmiany wprowadza idempotentny `scripts/kwhotel_booking_pages.py`.
- Testy: `tests/booking.test.mjs` (9), `tests/booking-pages.test.mjs` (28); build, `audit_static`, `audit_seo`, `audit_discovery`, testy node 63/63, `test_seo*` OK. Chrome bez okna na produkcji: przycisk dostaje daty i liczbę osób.
- Worker `06015b8c-4945-434d-adba-109fe71ea7fe` (rollback → `576f78bb`).
- Spec: `docs/superpowers/specs/2026-10-09-kwhotel-guestsage-booking-design.md`, plan: `docs/superpowers/plans/2026-10-09-kwhotel-guestsage-booking.md`. Materiały hotelu w lokalnym `kwhotel/` (poza repo).

**Etap Kamila (otwarte):** teksty prawne w 7 językach (sprzedaż online, prywatność — GuestSage/KWHotel jako odbiorca), `seo/discovery-content.json` → `llms/*.txt`, znaczenie `release.json` `bookingEnabled` i audytów, `ONLINE_SALES_LAUNCH_GATES.md`/`PAD_*`/`PMS-FISERV.md`, identyfikatory pokoi i kategorii wiekowych dzieci.

**Poprawki po przeglądzie (9.10.2026, Worker `6053200a-797c-41ba-8fb6-4238e370578e`):** język linku liczony z pierwszego znanego segmentu ścieżki (działa pod `/hornigold-preview/`); blok rezerwacji jako `.booking-panel` bez `role="status"` (app.js:65 nie wstawia już „brak terminu” nad przycisk); reguła `.booking-panel` dopisana na końcu `style.css`. Testy 72/72.

**Silnik GuestSage zwraca 404 „Oferta jest niedostępna” (9.10.2026, wieczór).** Każde wyszukiwanie (`/offers` i `/apartments`, z datami i bez) kończy się 404, strona główna silnika działa. Przyczyna po stronie KWHotel: publiczna konfiguracja `GET https://cloud.kwhotel.com/bookingengine/api/guestsage/configurations?hotelId=c98ead00-…` zwraca `enabled: false`, `hotel.active: false`, `hotel.company.active: false`; `availableLanguages: ["pl","en"]`. Do aktywacji w panelu KWHotel / przez wsparcie KWHotel (sales@kwhotel.pl). Instrukcja z kwietnia 2025 (`/offers?arrivalDate&departureDate&personsCount`) zgadza się z obecnym kodem silnika (trasa `/$locale/$hotelGuid/offers`, te same parametry).
