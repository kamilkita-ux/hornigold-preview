# Dziennik wydań hornigold.pl (Cloudflare)

Zapisuje `scripts/cloudflare-release.mjs --deploy`; bezpośrednie wdrożenia Wrangler dopisywane są po potwierdzeniu aktywnej wersji i odczycie produkcji. Procedura: [`CLOUDFLARE.md`](CLOUDFLARE.md).

| Data (UTC) | Tag | Rewizja | Worker | Poprzedni Worker | Commit Kamila | Migracje |
|---|---|---|---|---|---|---|
| 2026-10-10 21:28 | `hornigold-v23.9-cloudflare-r2` | 23.9 | `29de95ba-b100-49a3-ab1b-c7c024e7135b` | `6053200a-797c-41ba-8fb6-4238e370578e` | `d5acac0` | — |
| 2026-10-11 | `hornigold-v23.9-cloudflare-r3` | 23.9 | `84eaa0a1-8645-4607-83ca-179488cf2fef` | `29de95ba-b100-49a3-ab1b-c7c024e7135b` | `d5acac0` + poprawka weryfikacji Google | — |
| 2026-10-11 20:26 | `hornigold-v23.11-cloudflare` | 23.11 | `b6522385-6671-4430-b8c7-6872d90f6c8f` | `84eaa0a1-8645-4607-83ca-179488cf2fef` | `c239af6` | — |
| 2026-10-12 06:37 | `hornigold-v23.19-cloudflare` | 23.19 | `28d62822-4bd1-4c73-82ad-728da81160de` | `b6522385-6671-4430-b8c7-6872d90f6c8f` | `c164364` | — |
| 2026-10-12 12:36 | `hornigold-v23.19-cloudflare-r2` | 23.19 | `cd5a3f2a-1937-4665-a847-ccc2280f0e06` | `28d62822-4bd1-4c73-82ad-728da81160de` | `c164364` + poprawka znacznika rezerwacji | — |
| 2026-10-12 13:29 | `hornigold-v23.19-cloudflare-r3` | 23.19 | `4afa9184-c403-4372-ba7e-3009627c026c` | `cd5a3f2a-1937-4665-a847-ccc2280f0e06` | `c164364` + wybrany pokój w silniku KWHotel | — |
| 2026-10-12 14:45 | `hornigold-v23.19-cloudflare-r4` | 23.19 | `1a25e28a-5601-4ca8-9aa1-e6f6a0c8ea1a` | `4afa9184-c403-4372-ba7e-3009627c026c` | `c164364` + po wyborze pokoju od razu do silnika | — |
| 2026-10-12 16:06 | `hornigold-v23.19-cloudflare-r5` | 23.19 | `28e4a217-5e1d-442f-9c8e-3007ed6a4696` | `1a25e28a-5601-4ca8-9aa1-e6f6a0c8ea1a` | `c164364` + bez stron pośrednich (`/`, wybór pokoju) | — |
| 2026-10-13 20:22 | — (bezpośredni Wrangler, bez nowego tagu) | 23.20 | `03fa3ce4-c7ab-462d-8b5b-5f4ff3cc945f` | `28e4a217-5e1d-442f-9c8e-3007ed6a4696` | `1d651a7` | — |

23.20: potwierdzone 100% ruchu nowej wersji, 462 adresy w sitemapie, `/` → 301 do `/pl/` z zachowaniem parametrów. Publiczny odczyt 52 plików (21 HTML, 10 JS/CSS, 21 PDF) zgadzał się z SHA-256 paczki. Kopia sprzed wdrożenia: `2026-10-13_222021-pre-cloudflare-23.20` na Mac mini (22:20 Europe/Warsaw, 20:20 UTC), odczyt manifestu i historii zweryfikowany. Nie zmieniano DNS, konfiguracji D1, istniejących rezerwacji ani Fiserv; nie wykonywano migracji lub resetu licznika. Rollback Workera: `28e4a217-5e1d-442f-9c8e-3007ed6a4696`, bez automatycznego przywracania danych licznika. Dowody i kopia pozostają poza publicznym repozytorium.
