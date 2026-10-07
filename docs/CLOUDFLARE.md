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
| Adres techniczny | `https://hornigold.hornigold-cm.workers.dev` (wyłączyć po aktywacji strefy) |
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

## Stan przejściowy (7 października 2026 r., ok. 20:15) — do cofnięcia po aktywacji

Inten wpisał `vera`/`weston` jako rekordy NS w swojej strefie, ale nie zmienił delegacji w NASK (rejestr nadal
`ns.inten.pl`, `ns2.inten.pl`). Resolwery dostawały mieszane NS, a nieaktywna strefa Cloudflare nie miała adresu
IPv4 dla apeksu. Za zgodą Marka strefa w Cloudflare tymczasowo odpowiada tak jak inten:

- Custom Domain `hornigold.pl` odpięta od Workera; `A hornigold.pl 91.200.185.61` bez proxy, TTL 300;
- `www` → `91.200.185.61` bez proxy (zamiast `192.0.2.1` proxied + Redirect); `old` bez proxy.

**Nie robić `wrangler deploy` przed aktywacją strefy** — `routes` w `wrangler.jsonc` ponownie podepnie apeks.
Po aktywacji (rejestr .pl wskazuje `vera`/`weston`, strefa `active`): usunąć tymczasowy `A` apeksu, `www` z
powrotem na `192.0.2.1` proxied, `old` proxied, `workers_dev: false`, `npx wrangler deploy` (podpina Custom Domain),
smoke testy.
