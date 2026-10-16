# Hornigold — wdrożenie Cloudflare Workers

Gałąź `deploy/cloudflare` (CloudMentor) w worktree `C:\dev\hornigold-cloudflare`. Źródło treści: `site/`, `server/`, `drizzle/`, `scripts/` z `main` Kamila (`kamilkita-ux/hornigold-preview`, rozwijane w Sites). Ta gałąź dodaje: `wrangler.jsonc`, `scripts/cloudflare/`, ten plik, poprawkę ścieżek Windows w `scripts/seo.py` oraz rezerwacje GuestSage (`site/assets/booking.js`, panel w `site/assets/style.css`, 21 stron HTML, `scripts/kwhotel_booking_pages.py`, `tests/booking*.test.mjs`, spec i plan w `docs/superpowers/`). Konto GitHub `CloudDev-M` ma prawo zapisu od 12.10.2026; istniejący proces CloudMentor pozostaje zachowany.

## Architektura (stan na 10 października 2026 r.)

Przepływ żądania:

1. **DNS.** Rejestrator Netium → serwery `vera`/`weston` (Cloudflare, konto `Hornigold`). DNSSEC w Cloudflare włączony (`pending`) — rekord DS dopiero po przeniesieniu domeny do rejestratora, który go przyjmie (decyzja Marka).
2. **Strefa `hornigold.pl`.** TLS ≥ 1.2, `always_use_https`, HSTS 1 rok bez `includeSubDomains`, SSL `full`. `www` → 301 regułą Redirect (ścieżka i parametry zachowane); `old.hornigold.pl` proxied → stara strona PHP `91.200.185.61`; poczta Microsoft 365 (MX, SPF, DKIM, DMARC, autodiscover) bez proxy.
3. **Worker `hornigold`** (Custom Domain apeksu, `placement.region` `gcp:europe-central2` — wykonywanie najbliżej Warszawy). Wejście `_cloudflare_production/server/production-entry.mjs` (paczka z `scripts/prepare_cloudflare_production.py`): `robots.txt` zależny od hosta (`Allow` tylko na `https://hornigold.pl`), `X-Robots-Tag` zdjęty tylko z 693 tras kanonicznych i mapy strony, `/release.json` z polami produkcyjnymi; dalej `server/worker.mjs`: CSP (`script-src 'self'`) i nagłówki, `/api/site-stats` (licznik), 539 przekierowań 301 starych adresów (`server/routes.mjs`), statyki `ASSETS` z `_cloudflare_production/assets` (`run_worker_first`, `404-page`).
4. **D1 `hornigold-counter-eu`** (jurysdykcja EU) — wyłącznie zbiorczy licznik odsłon, bez danych osobowych.
5. **Rezerwacje.** Przycisk „Sprawdź dostępność i zarezerwuj” na `/{język}/rezerwacja/` → hostowany GuestSage AI Booking Engine (KWHotel); `booking.js` dokłada daty i liczbę osób z `HornigoldStay`. Umowa i płatność po stronie GuestSage. Silnik włączony w KWHotel 12.10.2026 (wcześniej 404 — sekcja „Rezerwacje GuestSage”).
6. **Logi Workera wyłączone** (dane poza UE); diagnostyka na żywo: `npx wrangler tail hornigold`.

## Zasoby

| Co | Wartość |
|---|---|
| Konto | `Hornigold` `ee23b9132a9692ab6c0e9f22aa86dda8` (osobne od FFP; od 7 października 2026 r.) |
| Worker | `hornigold`, produkcja 23.20: `03fa3ce4-c7ab-462d-8b5b-5f4ff3cc945f` (13.10.2026, 20:22 UTC); bezpośredni rollback: `28e4a217-5e1d-442f-9c8e-3007ed6a4696` (23.19-r5) |
| D1 | `hornigold-counter-eu` `23c8ca98-7e50-4a5f-98a1-1a0bfbebde7e`, **jurysdykcja EU**, migracje `drizzle/`; poprzednia `hornigold-counter` `bb927207-…` (`eeur`) = kopia |
| Strefa | `hornigold.pl` `398f3b032a51a14d095ea3d82d25c821`, Free, aktywna od 9.10.2026 |
| Adresy | `https://hornigold.pl` (Custom Domain); `www` → 301; `old.hornigold.pl` = stara strona PHP i rezerwacje Profitroom |
| `workers.dev` | wyłączony (`workers_dev: false`) |
| Logi | wyłączone (`observability.enabled: false`) |

Licznik odsłon liczy od zera od 7 października 2026 r. (`scripts/cloudflare/seed-counter.sql`) — decyzja Marka.

## Potwierdzone wydanie 23.20 — 13 października 2026 r.

Gotową paczkę `_cloudflare_production` z `main` `1d651a7fc08b8dcef5063ac097dec1bfbb3398ab` opublikowano bezpośrednio Wranglerem 4.149.0 do istniejącego Workera. Zachowano domenę, D1, licznik, GuestSage i Fiserv; bez migracji i seedowania. Zweryfikowano 1673 hashe paczki oraz zgodność 52 publicznych plików. Aktualna mapa ma **462 adresy indeksowalne**; 224 ilustracje i 7 wejść procesu rezerwacji pozostają celowo `noindex` przy zachowanej dostępności stron. `/` zwraca serwerowe 301 do `/pl/` z parametrami.

Kopia sprzed wdrożenia: `/Users/kamilkita/Documents/Hornigold-backups/2026-10-13_222021-pre-cloudflare-23.20` (Mac mini, 22:20 Europe/Warsaw). Potwierdzono odczyt historii i manifestu. Zapis konfiguracji oraz eksport D1 pozostają prywatnymi elementami kopii; nie dodawać ich do repozytorium.

Po bezpośrednim `wrangler deploy` kontrolę produkcji uruchamia się jawnie. Sam `--smoke` nie wykonuje rollbacku; automatyczny rollback dotyczy pełnego `cloudflare-release.mjs --deploy`. Punkt powrotu tego wydania:

```sh
npx wrangler rollback 28e4a217-5e1d-442f-9c8e-3007ed6a4696 --name hornigold --config wrangler.jsonc
```

Nie przywracać automatycznie starszych danych licznika ani nie zmieniać DNS. Po rollbacku ponownie odczytać produkcję. Aktualizacja samego monitora nie wymaga ponownego wdrożenia Workera. Monitor wykonuje wyłącznie GET, sprawdza dokładne przekierowania root/UTM i www, celowe `noindex` stron rezerwacji oraz JSON API licznika; nie zwiększa licznika ani nie wykonuje transakcji.

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

Smoke: `/pl/` 200 z `index,follow`; `/pl/nie-ma-takiej` 404 z `noindex`; `robots.txt` `Allow: /`; mapa strony 462 adresy indeksowalne; `/release.json` (`indexing: true`, `bookingEnabled: false`); GET `/api/site-stats`; stary adres z `server/routes.mjs` (301 z parametrami); root i `www` 301 z dokładnym zachowaniem parametrów; 7× `/{język}/rezerwacja/` z `a[data-booking]` i celowym `noindex`; nagłówek CSP bez zmian. Build na Windows trwa kilka minut i potrafi zostać przerwany przy braku pamięci — uruchamiać kroki osobno.

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

**Od 11 października 2026 r.:**
- **Tryb `--prepare`** wykonuje scalenie, build, audyty i testy bez publikacji. Klasyfikator trybu auto blokuje agentowi pełne `--deploy` bez wyraźnego polecenia „publikuj”. Agent robi więc `--prepare`, a po zgodzie Marka `npx wrangler deploy --config C:/dev/hornigold-cloudflare/wrangler.jsonc` i `--smoke`.
- **Automatyczne rozwiązywanie konfliktów.** Konflikty w `site/*/index.html`, `site/*/pobyt/index.html`, `site/*/rezerwacja/index.html` i `site/assets/style.css` skrypt rozwiązuje wersją Kamila, a potem uruchamia `scripts/kwhotel_booking_pages.py`. Ten skrypt idempotentnie przywraca bloki rezerwacji GuestSage i regułę `.booking-panel`. Konflikt w innym pliku zatrzymuje wydanie.
- **Audyt GA4 przed publikacją.** `scripts/audit_ga4.cjs` Kamila sprawdza zgodę na `_production_ready` i przechwytuje ruch do Google; wymaga Playwright (`npm install --no-package-lock && npx playwright install chromium`). Pozostałe `audit_*.cjs` Kamila pisał pod Linux/macOS (`/tmp`, `_site`, pomiary wydajności), dlatego nie są bramką wydania.
- **Test zgody GA4 po publikacji (smoke).** Na żywej stronie, w Chromium:
  - przed zgodą i po odmowie 0 żądań do `googletagmanager.com`/`google-analytics.com`;
  - zgoda „analityka” domyślnie odznaczona;
  - po zgodzie tag się ładuje (żądanie przerywane, do GA nic nie trafia);
  - e-mail i daty z adresu nie trafiają do `dataLayer`.

  Wyjątek w tym teście jest porażką smoke i wywołuje rollback.

Szczegóły działania:
- Wranglera skrypt woła przez `npx --yes wrangler@<wersja z package.json>`. Worktree nie ma `node_modules`, a bez `--yes` `npx` czeka na zgodę na instalację.
- Przed publikacją skrypt zapamiętuje aktywną wersję Workera i bieżący nagłówek CSP. Smoke sprawdza listę powyżej, porównuje CSP i pliki weryfikacyjne Google z `site/`.
- **Nieudany smoke → automatyczny `wrangler rollback`.**
- Po wydaniu: lokalny tag `hornigold-v<revision>-cloudflare[-rN]` (rewizja z `release.json`), wiersz w [`DEPLOY-LOG.md`](DEPLOY-LOG.md) i push gałęzi `deploy/cloudflare` z tagiem. `CloudDev-M` ma prawo zapisu od 12.10.2026 (zaproszenie Kamila z 9.10 trzeba było przyjąć na koncie — do tego czasu push kończył się 403). `main` aktualizujemy wyłącznie przez fast-forward do `deploy/cloudflare` i tylko na polecenie Marka (pierwszy raz 12.10.2026) — push na `main` uruchamia publikację Kamila na GitHub Pages i jej kontrole.
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
- 7 podstron `rezerwacja/`: blok „Zarezerwuj online” z przyciskiem (`a[data-booking=""]` z adresem `be.guestsage.com`, działa bez JS; sam napis `data-booking` nie jest znacznikiem bloku, bo sekcja nagrody Kamila ma `data-booking-award`); tekst pomocy formularzy pobytu (strony główne i `pobyt/`) zmieniony. Zmiany wprowadza idempotentny `scripts/kwhotel_booking_pages.py`.
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

## Wydanie 11 października 2026 r. (rewizja 23.11) — Google Analytics 4 po zgodzie

Trzy commity Kamila z `origin/main` (`8dab79d` 21:10, `7c3d336` 22:03, `c239af6` 22:07):

- **GA4** `G-ZJ9VJNGHGT`: konto Hornigold 93077899, property 558323228, strumień 16101873868. Działa tylko na `https://hornigold.pl`; podglądy go nie ładują.
  - `build.py` w trybie `production-ready` dopisuje `analytics-config.js` i `analytics.js`.
  - Podstawowy tryb zgody: tag Google ładuje się dopiero po zgodzie „analityka”.
  - Wyłączone: Google Signals, personalizacja reklam i enhanced measurement.
  - Zdarzenia: `page_view` (adres bez parametrów, poza dozwolonymi etykietami kampanii), kliknięcia telefonu/e-maila/rezerwacji/planera/social oraz `select_apartment`.
- **Prywatność:**
  - w oknie zgód nowa, domyślnie odznaczona kategoria „analityka” w 7 językach;
  - wygasanie zgody w trakcie wizyty;
  - teksty prawne HTML i PDF z datą 2026-10-11;
  - `independentLegalReview: false`.
- **CSP** (nagłówek w `production-entry.mjs` i meta w HTML): `script-src` + `https://www.googletagmanager.com`, `connect-src` + `https://www.google-analytics.com https://region1.google-analytics.com`. Przyjęte świadomie `--accept CSP` po przeglądzie i za zgodą Marka („publikuj”).
- Audyty i narzędzia QA Kamila (mobile, zgody, SEO, monitoring) oraz poprawki SEO w `scripts/seo.py`. Nasza poprawka `.as_posix()` zachowana.

Scalenie: konflikty w 21 stronach rezerwacji i w `style.css` (obie strony dopisały kod na końcu). Rozwiązane automatycznie wersją Kamila + `kwhotel_booking_pages.py`. Bloki GuestSage, zgoda „analityka” i reguła `.booking-panel` obecne.

Wyniki:
- build 693 stron; `audit_static`, `audit_seo` i `audit_discovery` bez błędów;
- testy node i `test_seo*` zielone;
- `audit_ga4.cjs` zielony.

Worker `b6522385-6671-4430-b8c7-6872d90f6c8f`; poprzedni `84eaa0a1` przywraca `wrangler rollback`. Smoke 23/23, w tym test zgody GA4 na żywej stronie.

**Do zrobienia po stronie właściciela (z przekazania Kamila):**
- w panelu GA (konto `hotelhornigold@gmail.com`) ponownie sprawdzić, że enhanced measurement, automatyczne zdarzenia formularzy i linków wychodzących oraz Google Signals są wyłączone;
- sprawdzić warunki przetwarzania i transferu Google dla konta;
- wykonać test w DebugView/Realtime z sesji z wyraźną zgodą.

Meta, Ads, rezerwacje i płatności pozostają wyłączone.

## Wydanie 12 października 2026 r. (rewizja 23.19)

27 commitów Kamila z `origin/main` (23.16–23.19, ostatni `c164364` o 02:56):
- 21 tagowanych PDF-ów prawnych z ujednoliconymi informacjami w 7 językach (`taggedPDFs: true`, `pdfUAValidated: false`);
- sekcja nagrody Booking.com 2026 nad stopką: lokalny obraz i link do źródła, bez zmian CSP, `bookingAward2026: true`;
- numer rewizji i data wydania w stopce z `release.json`;
- monitoring i audyty publiczne Kamila (`monitor_public.py`, workflow `post-publication`, `quality`). Sprawdzają jego podglądy, a hornigold.pl tylko odczytują;
- dependabot;
- `server/worker.mjs`: nagłówki bezpieczeństwa także na odpowiedziach 403/503 licznika.

Bez zmian przełączników właściciela, `wrangler.jsonc`, CSP i D1. Scalenie bez konfliktów.

Wydanie zrobione przez `cloudflare-release.mjs --prepare` i `npx wrangler deploy`:
- build 693 stron, audyty bez błędów;
- testy node i `test_seo*` zielone, `audit_ga4.cjs` zielony.

Worker `28d62822-4bd1-4c73-82ad-728da81160de`; poprzedni `b6522385` przywraca `wrangler rollback`. Smoke 23/23, w tym test zgody GA4 na żywej stronie.

Uwaga: upload zmienił wszystkie strony i PDF-y, a proces `wrangler deploy` zakończył się dopiero ok. 12 minut po aktywacji wersji. Cloudflare aktywował ją o 06:37 UTC; strona pokazywała 23.19 od razu. Przy długim deployu stan sprawdzać przez `wrangler deployments list` i `/release.json`, nie czekać w ciemno.

## Stan na 12 października 2026 r. (po południu): repo i rezerwacje KWHotel

- **Produkcję `hornigold.pl` wydaje się wyłącznie z gałęzi `deploy/cloudflare`.** Do 12.10.2026 `main` Kamila nie miał `wrangler.jsonc`, bloków rezerwacji GuestSage/KWHotel (`site/assets/booking.js`, `scripts/kwhotel_booking_pages.py`, 21 stron), poprawki weryfikacji Search Console w `server/production-entry.mjs` ani poprawki Windows w `scripts/seo.py`. Wydanie zbudowane z samego `main` zdjęłoby rezerwacje ze strony. Publikacja Kamila na GitHub Pages (`kamilkita-ux.github.io/hornigold-preview`) jest budowana z `main`, więc rezerwacji nie ma — to oczekiwane.
- Na koncie Cloudflare Hornigold jest jeden Worker (`hornigold`) i jeden członek konta; 12.10 jedynym wdrożeniem było nasze z 06:37 UTC (`28d62822`). Smoke 23/23, bloki rezerwacji w 7 językach.
- Gałąź `deploy/cloudflare` i tagi `hornigold-v*-cloudflare*` są od dziś na GitHubie. Scalenie z `main` — patrz niżej.
- Smoke i `kwhotel_booking_pages.py` rozpoznają blok po `a[data-booking=""]` z adresem GuestSage. Wcześniejsze sprawdzenie samego `data-booking` po wejściu sekcji nagrody (23.19) przepuściłoby stronę bez rezerwacji, a skrypt po konflikcie scalania nie odtworzyłby bloków.
- Silnik po stronie KWHotel nadal wyłączony: `configurations?hotelId=…` zwraca `enabled: false`, `hotel.active: false`. Przycisk prowadzi do silnika, ale wyszukiwanie ofert ruszy dopiero po włączeniu przez KWHotel.

## Wydanie 12 października 2026 r. po południu (23.19-r2) i scalenie z `main`

Polecenie Marka: wdrożyć, a gdy działa — scalić z `main`.

- Wydanie z `deploy/cloudflare` na commicie `b01ec20` (kod strony i serwera bez zmian wobec 23.19; zmienił się tylko `release.json` z nowym commitem). `origin/main` bez nowych commitów, więc `cloudflare-release.mjs` kończy na „brak nowego kodu” — build, audyty i testy uruchomione tymi samymi krokami ręcznie, dodatkowo wszystkie `tests/*.test.mjs` (110) i `check_repository.py`.
- Worker `cd5a3f2a-1937-4665-a847-ccc2280f0e06`; poprzedni `28d62822` przywraca `wrangler rollback`. Smoke 23/23, CSP bez zmian.
- `wrangler deploy` zakończył się błędem `504 Gateway Timeout` na `POST …/deployments`, ale wersja została aktywowana (`deployments list`: 100% `cd5a3f2a`, `/release.json` z nowym commitem). Przy takim błędzie najpierw sprawdzić stan, nie ponawiać w ciemno.
- Przed scaleniem kontrole Kamila `quality.yml` uruchomione ręcznie (`workflow_dispatch`) na `deploy/cloudflare`: zielone, łącznie z audytem mobilnym i Lighthouse. Lokalnie jedyny błąd testów Pythona to `test_traversal_and_symlink_rejected` (Windows bez uprawnienia do dowiązań symbolicznych) — nie dotyczy CI.
- `main` przesunięty fast-forward do `deploy/cloudflare`. Od tej chwili `main` zawiera rezerwacje KWHotel, `wrangler.jsonc`, runbook i skrypt wydań, a publikacja Kamila na GitHub Pages pokazuje blok „Zarezerwuj online”.
- Dalej bez zmian: produkcję wydaje się z `deploy/cloudflare` po scaleniu `origin/main`. Jeśli Sites Kamila nadpisze strony rezerwacji wersją bez bloków, konflikt lub smoke to wychwyci, a `scripts/kwhotel_booking_pages.py` odtworzy bloki.
- Materiały hotelu w lokalnym `kwhotel/` nadal poza repozytorium (repo publiczne, dane osób trzecich); katalog jest w `.git/info/exclude`.

## Silnik rezerwacji włączony (12 października 2026 r., ok. 14:50)

Marek włączył silnik w panelu KWHotel (cloud.kwhotel.com → Moduły → Silnik rezerwacyjny). Sprawdzone z zewnątrz przeglądarką (Playwright), bez wybierania oferty i bez rezerwacji:

- Przed włączeniem `POST be.guestsage.com/bookingengine/api/guestsage/offers` zwracał 403 „Enable booking engine before querying offers”, a gość widział „404 Oferta jest niedostępna”. Po włączeniu: 200 z ofertami.
- Przejście `hornigold.pl/{język}/rezerwacja/` z datami → przycisk → silnik: 6 ofert na 11–13.11.2026 dla 2 osób w pl, en, de, uk, es, it; `zh-hans` otwiera silnik po angielsku. Oferty są także na terminy za 3, 14 i 90 dni.
- Publiczna konfiguracja (`…/guestsage/configurations?hotelId=…`) nadal pokazuje `enabled: false`, `hotel.active: false`, `company.active: false`, mimo że silnik działa — tych pól nie traktować jako wyznacznika. Wyznacznikiem jest odpowiedź `/guestsage/offers`.
- Języki silnika po zmianie w panelu: pl, en, de, it, uk, es.
- Wszystkie oferty były na jednym planie cenowym (10205), bezzwrotne, z przedpłatą 100%. W ofertach dla 2 osób nie pojawiły się typy 4837 (Apartment Deluxe) i 4838 (Apartament nr 128).
- Typy pokoi z `…/guestsage/hotels/<obiekt>/roomtypes` (wartości `featuredRoomTypeId` do mapy `ROOMS` w `site/assets/booking.js`): 4830 Classic, 4828 Deluxe, 4834 Premium, 4836 Premium Deluxe, 4833 Apt Suite, 4837 Apartment Deluxe, 4835 Apartament 2 bedrooms, 4838 Apartament nr 128. Mapa `ROOMS` nadal pusta — przypisanie do stron `pokoje/` (zwłaszcza `prestige`, `prestige-deluxe`, `hornigold`) wymaga potwierdzenia hotelu.
- Nie sprawdzono: formularza danych gościa, płatności i zapisu rezerwacji w KWHotel — to próbna rezerwacja po stronie hotelu.

## Wydanie 12 października 2026 r. (23.19-r3): wybrany pokój trafia do silnika

Polecenie Marka: gość wybiera termin i pokój na stronie, a silnik KWHotel ma to pamiętać (wariant A, publikacja po testach).

- `site/assets/booking.js`: mapa `ROOMS` dla sześciu kategorii, które silnik sprzedaje — `classic` 4830, `deluxe` 4828, `premium` 4834, `deluxe-premium` 4836, `suite` 4833, `prestige-deluxe` 4835. Przycisk na stronie Rezerwacja otwiera silnik z terminem, liczbą osób i `featuredRoomTypeId`; silnik pokazuje wtedy tylko tę kategorię (sprawdzone: żądanie `/guestsage/offers` dostaje `roomTypeIds: [id]`).
- `apartament-deluxe` (4837), `prestige` i `hornigold` są bez identyfikatora: w silniku nie mają oferty online, więc z identyfikatorem gość zobaczyłby „Brak dostępności”. Bez niego widzi wszystkie wolne pokoje. Dopisać po uzupełnieniu oferty w KWHotel (dla `prestige` i `hornigold` hotel musi wskazać typ; wolny został 4838 „Apartament nr 128”).
- Blok rezerwacji ma drugi, domyślnie ukryty odnośnik `a[data-booking-all=""]` („Zobacz wszystkie dostępne pokoje”, 7 języków). `booking.js` odkrywa go, gdy przycisk zawęża silnik do jednej kategorii — silnik przy zajętym pokoju nie proponuje innych. Odnośnik dodaje `scripts/kwhotel_booking_pages.py` (także do stron już zmienionych; wynik identyczny jak przy generowaniu od wersji Kamila).
- Testy: `tests/booking.test.mjs` (mapa, adresy, zachowanie odnośników na atrapie dokumentu), `tests/booking-pages.test.mjs` (odnośnik w 7 językach). Build, audyty i 122 testy node zielone; przed wdrożeniem sprawdzenie w przeglądarce na lokalnej paczce.
- Worker `4afa9184-c403-4372-ba7e-3009627c026c`; poprzedni `cd5a3f2a` przywraca `wrangler rollback`. Pierwsza próba `wrangler deploy` skończyła się `504` na `assets-upload-session` — przed wysłaniem plików, produkcja bez zmian; ponowienie przeszło. Smoke 23/23.
- Na żywej stronie (Playwright, bez rezerwacji): dla każdej z sześciu kategorii silnik zwraca jedną ofertę właściwego typu; dla trzech apartamentów bez oferty i dla wejścia bez pokoju — 6 ofert.
- Silnik nie ma żadnego odnośnika powrotnego do strony hotelu (nazwa obiektu w nagłówku nie jest linkiem). Powrót: „Wstecz” przeglądarki — strona pamięta termin, liczbę osób i pokój.

## Wydanie 12 października 2026 r. (23.19-r4): po wyborze pokoju od razu do silnika

Polecenie Marka: zrezygnować ze strony pośredniej — klik w pokój ma od razu przenosić do KWHotel (publikacja po testach).

- `site/assets/booking.js`: gdy gość trafia na `/{język}/rezerwacja/?room=…` z ważnym terminem i kategorią z mapy `ROOMS`, skrypt wykonuje `location.replace()` na adres silnika z terminem, liczbą osób i `featuredRoomTypeId`. Strona Rezerwacja nie zostaje w historii, więc „Wstecz” z silnika wraca na listę pokoi albo stronę pokoju — to zastępuje przycisk powrotu, którego silnik nie ma.
- Strona Rezerwacja nadal się pokazuje: bez terminu, dla `apartament-deluxe`, `prestige` i `hornigold` (brak oferty online), przy wejściu bez parametru `room` (wtedy widać też odnośnik „Zobacz wszystkie dostępne pokoje”) i bez JavaScriptu. Formularz zapytania jest też na stronach Kontakt, Dla firm i stronach pobytów.
- Świadomy koszt: strona Rezerwacja mignie przed przeniesieniem (`booking.js` ładuje się z `defer`), a gość, którego pokój jest zajęty, widzi w silniku „Brak dostępności” bez propozycji innych pokoi i wraca przyciskiem „Wstecz”. Wariant z bezpośrednimi odnośnikami na 84 stronach z przyciskami pokoi odrzucony — te strony Kamil generuje na nowo.
- Audyt mobilny Kamila (`audit_mobile_release.cjs`) odwiedza `/pl/pobyt/?…&room=classic`, nie stronę Rezerwacja — przeniesienie go nie dotyczy.
- Testy: `tests/booking.test.mjs` (przeniesienie i cztery przypadki, w których strona zostaje); 125 testów node zielonych. Przed wdrożeniem i po nim przejście w przeglądarce (Playwright, bez rezerwacji): 6 kategorii z listy pokoi → silnik z jedną ofertą właściwego typu → „Wstecz” na listę; strona pokoju z terminem z sesji; 3 apartamenty bez oferty i wejście bez terminu zostają na stronie Rezerwacja.
- Worker `1a25e28a-5601-4ca8-9aa1-e6f6a0c8ea1a`; poprzedni `4afa9184` przywraca `wrangler rollback`. Smoke 23/23 w drugim przebiegu; w pierwszym test zgody GA4 nie wykonał się (`page.goto` przekroczył 20 s tuż po wdrożeniu), pozostałe kontrole były zielone.

## Wydanie 12 października 2026 r. (23.19-r5): bez stron pośrednich

Zgłoszenie Marka: po wejściu na `hornigold.pl` widać napis „Polski”, zanim pojawi się strona główna; po wyborze terminu i pokoju przez chwilę widać stronę Rezerwacja, zanim otworzy się silnik.

Przyczyna w obu miejscach ta sama: o przejściu decydował skrypt z `defer`, uruchamiany po namalowaniu strony. Pomiar w przeglądarce (zdarzenie `first-contentful-paint`): dokument `/` był malowany z tekstem „Polski”, a `/pl/rezerwacja/?…&room=classic` z całą treścią strony.

- **`/`** (`site/index.html`): odnośnik zapasowy „Polski” jest w `<noscript>`, a `root-language.js` ładuje się w `<head>` bez `defer`. Przeglądarka z JavaScriptem nie ma czego malować i przechodzi od razu do języka; zapamiętany wybór języka (`localStorage`) działa jak dotąd. Przekierowanie po stronie serwera byłoby o jedno żądanie szybsze, ale serwer nie zna zapamiętanego języka — do decyzji, gdyby zależało na czasie bardziej niż na tej funkcji.
- **Wybór pokoju** (`server/production-entry.mjs`): `GET`/`HEAD` na `/{język}/rezerwacja/?room=…&arrival=…&departure=…` z kategorią sprzedawaną w silniku i ważnym terminem dostaje `302` (`Cache-Control: no-store`) na adres silnika. Reguły i adres są te same co w `bookingUrl()` z `site/assets/booking.js`; mapy pokoi i języków są w obu plikach, a `tests/booking-redirect.test.mjs` porównuje wynik Workera z `bookingUrl()` dla 7 języków × 6 pokoi. **Przy zmianie `ROOMS` lub `LANG` zmienić oba pliki** — test to wymusi. Przeniesienie w `booking.js` zostaje jako zapas tam, gdzie nie ma Workera (GitHub Pages Kamila).
- Odnośniki z przyciskami pokoi zawsze niosą termin w adresie (`app.js` `updateLinks()` dopisuje cały stan pobytu), więc Worker ma wszystko, czego potrzebuje, bez dostępu do `sessionStorage`.
- Smoke (`cloudflare-release.mjs`) ma trzy nowe kontrole: `/` bez widocznego tekstu, wybór pokoju → `302` do silnika, pokój bez oferty online → `200`.
- Po wdrożeniu (Playwright, bez rezerwacji): `/` nie jest malowany; klik w pokój dostaje `302` i przeglądarka nie maluje strony Rezerwacja; 6 kategorii → silnik z jedną ofertą właściwego typu, „Wstecz” wraca na listę pokoi. Czas od kliknięcia do pojawienia się silnika zależy już tylko od KWHotel (w pomiarach 2–5 s) — w tym czasie gość widzi listę pokoi.
- Worker `28e4a217-5e1d-442f-9c8e-3007ed6a4696`; poprzedni `1a25e28a` przywraca `wrangler rollback`. Smoke 26/26. Build przeliczył wszystkie strony, więc `wrangler deploy` kończył wysyłkę jeszcze kilkanaście minut po aktywacji wersji.
- Test lokalny całego Workera przed wdrożeniem: `npx wrangler dev --config C:/dev/hornigold-cloudflare/wrangler.jsonc --port 8791` (z katalogu z lokalnym `wrangler`), potem pomiary pod `http://127.0.0.1:8791`.
