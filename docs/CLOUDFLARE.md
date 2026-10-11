# Hornigold — wdrożenie Cloudflare Workers

Gałąź `deploy/cloudflare` (CloudMentor) w worktree `C:\dev\hornigold-cloudflare`. Źródło treści: `site/`, `server/`, `drizzle/`, `scripts/` z `main` Kamila (`kamilkita-ux/hornigold-preview`, rozwijane w Sites). Ta gałąź dodaje: `wrangler.jsonc`, `scripts/cloudflare/`, ten plik, poprawkę ścieżek Windows w `scripts/seo.py` oraz rezerwacje GuestSage (`site/assets/booking.js`, panel w `site/assets/style.css`, 21 stron HTML, `scripts/kwhotel_booking_pages.py`, `tests/booking*.test.mjs`, spec i plan w `docs/superpowers/`). Konto GitHub `CloudDev-M` nie ma jeszcze prawa zapisu do repo Kamila — commity są lokalne.

## Architektura (stan na 10 października 2026 r.)

Przepływ żądania:

1. **DNS.** Rejestrator Netium → serwery `vera`/`weston` (Cloudflare, konto `Hornigold`). DNSSEC w Cloudflare włączony (`pending`) — rekord DS dopiero po przeniesieniu domeny do rejestratora, który go przyjmie (decyzja Marka).
2. **Strefa `hornigold.pl`.** TLS ≥ 1.2, `always_use_https`, HSTS 1 rok bez `includeSubDomains`, SSL `full`. `www` → 301 regułą Redirect (ścieżka i parametry zachowane); `old.hornigold.pl` proxied → stara strona PHP `91.200.185.61`; poczta Microsoft 365 (MX, SPF, DKIM, DMARC, autodiscover) bez proxy.
3. **Worker `hornigold`** (Custom Domain apeksu, `placement.region` `gcp:europe-central2` — wykonywanie najbliżej Warszawy). Wejście `_cloudflare_production/server/production-entry.mjs` (paczka z `scripts/prepare_cloudflare_production.py`): `robots.txt` zależny od hosta (`Allow` tylko na `https://hornigold.pl`), `X-Robots-Tag` zdjęty tylko z 693 tras kanonicznych i mapy strony, `/release.json` z polami produkcyjnymi; dalej `server/worker.mjs`: CSP (`script-src 'self'`) i nagłówki, `/api/site-stats` (licznik), 539 przekierowań 301 starych adresów (`server/routes.mjs`), statyki `ASSETS` z `_cloudflare_production/assets` (`run_worker_first`, `404-page`).
4. **D1 `hornigold-counter-eu`** (jurysdykcja EU) — wyłącznie zbiorczy licznik odsłon, bez danych osobowych.
5. **Rezerwacje.** Przycisk „Sprawdź dostępność i zarezerwuj” na `/{język}/rezerwacja/` → hostowany GuestSage AI Booking Engine (KWHotel); `booking.js` dokłada daty i liczbę osób z `HornigoldStay`. Umowa i płatność po stronie GuestSage. **Stan 10.10.2026: silnik nieaktywny w KWHotel → 404** (sekcja „Rezerwacje GuestSage”).
6. **Logi Workera wyłączone** (dane poza UE); diagnostyka na żywo: `npx wrangler tail hornigold`.

## Zasoby

| Co | Wartość |
|---|---|
| Konto | `Hornigold` `ee23b9132a9692ab6c0e9f22aa86dda8` (osobne od FFP; od 7 października 2026 r.) |
| Worker | `hornigold`, produkcja `6053200a-797c-41ba-8fb6-4238e370578e` (10.10.2026); rollback: `06015b8c` (rezerwacje bez poprawek po przeglądzie), `576f78bb` (bez rezerwacji), `2e24247c` (bez indeksowania) |
| D1 | `hornigold-counter-eu` `23c8ca98-7e50-4a5f-98a1-1a0bfbebde7e`, **jurysdykcja EU**, migracje `drizzle/`; poprzednia `hornigold-counter` `bb927207-…` (`eeur`) = kopia |
| Strefa | `hornigold.pl` `398f3b032a51a14d095ea3d82d25c821`, Free, aktywna od 9.10.2026 |
| Adresy | `https://hornigold.pl` (Custom Domain); `www` → 301; `old.hornigold.pl` = stara strona PHP i rezerwacje Profitroom |
| `workers.dev` | wyłączony (`workers_dev: false`) |
| Logi | wyłączone (`observability.enabled: false`) |

Licznik odsłon liczy od zera od 7 października 2026 r. (`scripts/cloudflare/seed-counter.sql`) — decyzja Marka.

## DNS

Strefa odtworzona 1:1 z serwerów `ns*.inten.pl` (7 października 2026 r.): poczta Microsoft 365 (MX, SPF z Profitroom, DKIM `selector1/2`, DMARC, autodiscover, Lync/SIP SRV, Intune), `mail/pop/smtp/ftp` → `91.200.185.61` bez proxy, także `apartamenty`, `_domainkey`, `x._domainkey`. Definicja: `scripts/cloudflare/zone-hornigold.json`. Apeks obsługuje Custom Domain Workera, `www` = `192.0.2.1` proxied tylko pod przekierowanie.

**Wycofanie** na starą stronę: w Cloudflare usunąć Custom Domain i dodać `A hornigold.pl 91.200.185.61` proxied (strefa u Cloudflare zostaje). Zmiany DNS przez MCP Cloudflare wymagają reguły `mcp__plugin_cloudflare_cloudflare__execute` w `/permissions`; usuwać rekord dopiero, gdy wiadomo, że deploy przejdzie (9.10.2026 apeks był ok. minuty bez rekordu).

## Wdrożenie nowej wersji z `main`

Na Windows w Git Bash: `export MSYS_NO_PATHCONV=1 PYTHONUTF8=1`, `core.autocrlf=false` (pliki LF). Przy scaleniu sprawdzić, czy Kamil przeniósł poprawkę `scripts/seo.py` (`.as_posix()`) — bez niej build produkcyjny kończy się błędami „… indexing”. Po scaleniu uruchomić `scripts/kwhotel_booking_pages.py` (idempotentny), jeśli Kamil zmienił strony rezerwacji lub formularzy pobytu — testy `booking-pages` to wykryją.

```sh
git fetch origin && git merge origin/main          # w C:\dev\hornigold-cloudflare
P=.venv/Scripts/python; export GITHUB_SHA=$(git rev-parse HEAD)
$P scripts/build.py --base / --counter                                   # podgląd _site — dla audit_static
$P scripts/audit_static.py --base /
$P scripts/build.py --mode production-ready --base / --counter --production-counter
$P scripts/audit_seo.py --mode production-ready
$P scripts/audit_discovery.py --mode production-ready
$P scripts/prepare_cloudflare_production.py                              # -> _cloudflare_production/
node --test tests/production-indexing.test.mjs tests/server.test.mjs tests/booking.test.mjs tests/booking-pages.test.mjs
$P -m unittest discover -s tests -p 'test_seo*.py'
git checkout -- docs/seo/                                                # raporty audytów — nie commitować
npx wrangler deploy --config C:/dev/hornigold-cloudflare/wrangler.jsonc  # musi zaczynać się od „npx wrangler deploy” (reguła uprawnień)
```

Migracje D1 (tylko gdy przybyło coś w `drizzle/`): `CLOUDFLARE_ACCOUNT_ID=ee23b9132a9692ab6c0e9f22aa86dda8 npx wrangler d1 migrations apply hornigold-counter-eu --remote --config wrangler.jsonc` (wrangler widzi dwa konta).

Smoke: `/pl/` 200 z `index,follow`; `/pl/nie-ma-takiej` 404 z `noindex`; `robots.txt` `Allow: /`; mapa strony 693 adresy; `/release.json` (`indexing: true`, `bookingEnabled: false`); `/api/site-stats`; stary adres z `server/routes.mjs` (301 z parametrami); `www` 301; 7× `/{język}/rezerwacja/` z `a[data-booking]`; nagłówek CSP bez zmian. Build na Windows trwa kilka minut i potrafi zostać przerwany przy braku pamięci — uruchamiać kroki osobno.

### Automatycznie: `scripts/cloudflare-release.mjs` (od 10 października 2026 r.)

Ten sam runbook jako skrypt, w worktree `C:\dev\hornigold-cloudflare`:

```sh
node scripts/cloudflare-release.mjs              # przegląd: nowe commity z origin/main i wynik kontroli, nic nie zmienia
node scripts/cloudflare-release.mjs --deploy     # scalenie, build, audyty, testy, migracje, deploy, smoke, tag, dziennik
node scripts/cloudflare-release.mjs --smoke      # same testy dymne produkcji
```

Skrypt zatrzymuje się w tych przypadkach:
- `WRANGLER` — zmiana `wrangler.jsonc`;
- `MIGRATION_CHANGED` — zmiana istniejącej migracji D1;
- `OWNER_SWITCH` — zmiana przełączników właściciela w `release.json`: `indexing`, `bookingEnabled`, `paymentsEnabled`, `counterEnabled`;
- `CSP` — zmiana `Content-Security-Policy` w `server/`, np. przy aktywacji pomiaru Meta;
- utrata poprawki `.as_posix()` w `scripts/seo.py`;
- konflikt scalania;
- dowolny błąd buildu, audytu lub testu.

`--accept CSP` przepuszcza zmianę CSP po przeglądzie. Inne kody wymagają ręcznej decyzji.

Szczegóły działania:
- Wranglera skrypt woła przez `npx --yes wrangler@<wersja z package.json>`. Worktree nie ma `node_modules`, a bez `--yes` `npx` czeka na zgodę na instalację.
- Przed publikacją skrypt zapamiętuje aktywną wersję Workera i bieżący nagłówek CSP. Smoke sprawdza listę powyżej, porównuje CSP i pliki weryfikacyjne Google z `site/`.
- **Nieudany smoke → automatyczny `wrangler rollback`.**
- Po wydaniu: lokalny tag `hornigold-v<revision>-cloudflare[-rN]` (rewizja z `release.json`), wiersz w [`DEPLOY-LOG.md`](DEPLOY-LOG.md) i próba push. Dopóki `CloudDev-M` nie ma prawa zapisu, push kończy się 403, a gałąź i tag zostają lokalnie.
- Testy skryptu: `node --test tests/cloudflare-release.test.mjs`.

## Granice

- Indeksowanie włączone tylko dla `https://hornigold.pl` (zgoda właściciela opisana przez Kamila w `README.md`, `docs/CLOUDFLARE_SEO_DEPLOYMENT_2026-10-09.md`); inne hosty i podglądy `noindex` + `Disallow: /`. Zgłoszenie mapy strony w Search Console / Bing — właściciel.
- Rezerwacje: tylko przekazanie do GuestSage; płatności i umowa po stronie silnika. Własny koszyk i Fiserv (`docs/PMS-FISERV.md`, `ONLINE_SALES_LAUNCH_GATES.md`) nie są wdrażane; `release.json` `bookingEnabled: false` oznacza brak sprzedaży na samej stronie.
- Etap Kamila: teksty prawne w 7 językach (regulamin i `/dokumenty/` mówią, że sprzedaż online nie jest uruchomiona), prywatność (GuestSage/KWHotel jako odbiorca), `llms/*.txt`, znaczenie `bookingEnabled`, identyfikatory pokoi.
- Materiały KWHotel w lokalnym `kwhotel/` — poza repozytorium (repo publiczne, dane kontaktowe dostawcy).
- Sites Kamila i GitHub Pages działają niezależnie od tego wdrożenia.

# Dziennik zmian

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

## Wydanie 10 października 2026 r. (rewizja 23.9-r2)

Scalone 7 commitów Kamila z `origin/main` (`d5acac0`, 9 października wieczorem):
- linki do kanałów społecznościowych w stopce wszystkich 7 języków (`content/social-channels.json`; Instagram `hornigold.apartments`, nowy Facebook, LinkedIn), wstawiane przez `build.py`;
- plik weryfikacyjny Google Search Console `site/google6078b276ecb15bd4.html`, pomijany przez build i audyt SEO;
- przygotowany pomiar Meta w `integrations/meta/`, poza `site/`, więc **nieaktywny**. Według README Kamila aktywacja wymaga teksty prawne w 7 językach, rozszerzenia CMP o zgodę marketingową, CSP z `connect.facebook.net` i testów Meta Test Events. To decyzja właściciela; CAPI wyłączone.

Bez zmian `server/`, `wrangler.jsonc`, CSP, `release.json` i D1. Poprawka `scripts/seo.py` (`.as_posix()`) zachowana.

Wyniki:
- build 693 stron; `audit_static`, `audit_seo` i `audit_discovery` bez błędów;
- paczka 1666 plików;
- testy node 87/87 (w tym `meta-staged`), `test_seo*` 10/10.

Worker `29de95ba-b100-49a3-ab1b-c7c024e7135b`; poprzedni `6053200a-797c-41ba-8fb6-4238e370578e` przywraca `wrangler rollback`. Smoke `scripts/cloudflare-release.mjs --smoke` przeszedł w całości: 18/18, CSP identyczny jak przed wdrożeniem, brak skryptów Meta na stronach.

**Search Console: plik weryfikacyjny — poprawione w 23.9-r3 (11 października 2026 r.).**

Problem:
- Po 23.9-r2 adres `/google6078b276ecb15bd4.html` zwracał 307 na `/google6078b276ecb15bd4`. Wynikało to z domyślnego `assets.html_handling` (`auto-trailing-slash`) Cloudflare.
- Pomoc Google opisuje przekierowania niespójnie, więc weryfikacja plikiem mogła nie przejść.
- Zmiana `html_handling` na `none` odpadła, bo zepsułaby `/pl/` → `/pl/index.html` na całej stronie.

Poprawka w `server/production-entry.mjs` (warstwa tylko dla produkcji Cloudflare):
- `GET`/`HEAD` na `/google<hex>.html` pobiera z `ASSETS` ten sam plik pod adresem bez `.html` i oddaje jego treść z kodem 200;
- gdy pliku nie ma, żądanie idzie zwykłą ścieżką i kończy się 404;
- źródłem treści zostaje plik w `site/`.

Testy i weryfikacja:
- `tests/search-console-verification.test.mjs` używa atrapy assetów z 307. Razem z resztą testów node 91/91.
- Smoke w `cloudflare-release.mjs` znów wymaga 200 bez przekierowania.
- Na produkcji `GET`/`HEAD` → 200 `text/html`, treść `google-site-verification: google6078b276ecb15bd4.html`. CSP bez zmian.
- Worker `84eaa0a1-8645-4607-83ca-179488cf2fef`; poprzedni `29de95ba` przywraca `wrangler rollback`.

**Kamil:** to odstępstwo od Twojego kodu. Przy kolejnym scaleniu proszę przenieść blok z `production-entry.mjs` do Sites, inaczej scalenie go cofnie i smoke zatrzyma wydanie.
