# Zatwierdzenie publikacji podglądów — 07.10.2026

Po odbiorze poniższego etapu lokalnego właściciel zatwierdził publikację poprawek jako 23.3 w istniejących podglądach Sites i GitHub Pages. Poniższy raport opisuje lokalne przygotowanie i testy przed tą zgodą. Potwierdzenie publikacji wymaga osobnych wyników platform; sam plik nie stanowi dowodu wdrożenia. Production-ready pozostaje nieopublikowany, podglądy zachowują noindex i Disallow: /.

---

# Gotowość SEO PL — etap lokalny, 07.10.2026

Checkout Sites `tmp/sites-consolidated-23`, projekt `appgprj_6ac24ff4d7d08191aef99366bb3d966f`, commit wejściowy `04af54414df7d0764786dbb4d771b95c16644a3e`. Drzewo było czyste przed pracą. Poprzedni raport zachowano w `docs/seo/readiness-before-pl-local-20261007.md`.

**Bieżące zmiany pozostają lokalne. Nie wykonano push, deploy, publikacji ani zmian usług zewnętrznych.** Wcześniejsza publikacja wersji 23.2 nie obejmuje tych poprawek. `release.json`, manifest Sites, Worker, integracje i dane biznesowe pozostały bez zmian. Dotychczasowy `dist/` jest starszym pakietem, nie artefaktem tego etapu.

## GOTOWE LOKALNIE

| Wymaganie | Stan | Dowód |
|---|---|---|
| Dziewięć priorytetowych tras | Jedno H1, unikalne metadane, właściwy canonical i linkowanie | `seo/local-intents-pl.json`, `docs/seo/pl-intents-preview.json` |
| Metadane i H1 | Doprecyzowano 13 stron PL, w tym dziewięć wskazanych i cztery pomocnicze | `scripts/apply_local_intents_pl.py`, źródła `site/pl/`, `seo/metadata-overrides.json` |
| Linkowanie | 65 widocznych odnośników na 18 stronach; bez automatycznych CTA noclegowych w artykułach o miejscach pamięci | `pl-intents-preview.json`; trzy świadome wyjątki w `weakLinkCandidates` |
| Wszystkie strony PL | 99 kanonicznych stron przejrzanych; zero duplikatów title i meta description w artefaktach | `inventory` i `duplicates` w raportach PL |
| Mapa intencji | Dziewięć fraz, rozdzielenie przewodników od stron pobytu; bez nowych stron pod warianty fraz | `SEO_KEYWORD_MAP_PL.md` |
| Określenie hotel | Nie dodano do nowych metadanych/H1; dwie frazy pozostają niewdrożone | Mapa fraz i kontrola `audit_pl_intents.py` |
| Granice zmian | 16 chronionych plików bez zmian; porównano 100 źródłowych HTML PL, bez zmiany istniejących akapitów biznesowych wykrywanych skanerem | `docs/seo/pl-boundaries.json` |
| Preview | Nadal noindex,nofollow,noarchive, Disallow: /, bez sitemapy | `_site/`, `docs/seo/audit-preview.json` |
| Kontrole globalne | 693 trasy, 1241 HTML, canonicale, wzajemne hreflang, obrazy, linki i minimalny WebPage | `audit-preview.json`, `audit-production-ready.json` |

## PRZYGOTOWANE DO PRODUKCJI

| Wymaganie | Stan | Warunek / dowód |
|---|---|---|
| Osobny build | `_production_ready/` wygenerowany lokalnie; nie opublikowany | `docs/seo/pl-local-validation.json` |
| Canonical i języki | Przyszła domena https://hornigold.pl, siedem języków i x-default; adresy istnieją lokalnie | Nie potwierdza dostępności na przyszłej domenie |
| Sitemap / robots | Dotychczasowy generator: 693 kanoniczne adresy; preview niezależnie zablokowany | `_production_ready/sitemap.xml`, audyt produkcyjny |
| Błędy i aliasy | 539 aliasów i 9 HTML błędów/technicznych pozostają noindex i poza sitemapą | `futureNoindex` w `pl-intents-production-ready.json` |
| PDF | Siedem PDF poza sitemapą; istniejący szablon /documents/* przewiduje X-Robots-Tag: noindex | Potrzebny hosting obsługujący nagłówki oraz późniejsza kontrola HTTP |
| Przekierowania | Istniejący szkic mapy zachowany, bez wdrożenia lub edycji serwera | `REDIRECT_MAP_DRAFT.csv`; potrzebny eksport aktualnych starych URL |
| Schema | Tylko minimalny WebPage w artefaktach, bez nowych twierdzeń biznesowych | `seo/structured-data-policy.json` i globalne audyty |

## WYMAGA POTWIERDZENIA

- 179 istniejących fragmentów na 28 stronach dotyczy m.in. cen, parkingu, godzin śniadań, powierzchni, Wi-Fi, klimatyzacji i wellness. To heurystyczni kandydaci do sprawdzenia, nie 179 stwierdzonych niezgodności ani pełny audyt faktów. Pełna lista: `businessClaimCandidates` w `pl-intents-preview.json`.
- Rejestr podmiotu z `legal/operator-verification.json`, pobrany 06.10.2026, nie potwierdza usług, cen, wyposażenia, dostępności, odległości ani statusu hotelowego.
- Cztery ogólne/poetyckie komunikaty: `/pl/dla-firm/`, `/pl/oferty/`, `/pl/club-hornigold/`, `/pl/sniadania/`. Dalsze doprecyzowanie przekazu zależy od zatwierdzonego zakresu oferty; nie dopisano pakietów ani benefitów.
- Określenie centrum Katowic pochodzi z dotychczasowej treści. Nie wykonano nowych pomiarów geograficznych. Nie deklarowano minut/metrów ani lokalizacji przy Spodku.
- Odbiór prawny dokumentów, prawa do materiałów i profesjonalny odbiór tłumaczeń są odrębnymi zadaniami. Bieżące zmiany dotyczą PL; nie zmieniano pozostałych języków.

## WYMAGA ZEWNĘTRZNEJ DECYZJI

1. Zatwierdzenie dossier faktów przez właściciela/recepcję. Bez formalnego potwierdzenia klasyfikacji nie wdrażać określenia hotel.
2. Wybór odpowiedniego hostingu produkcyjnego z nagłówkami i przekierowaniami oraz odbiór mapy 301. Nie zmieniano DNS, GitHub Pages ani ustawień Sites.
3. Osobna zgoda na przyszłą publikację produkcji i otwarcie indeksacji, po odbiorze treści, dokumentów i wymaganych integracji.
4. Późniejsza weryfikacja Search Console/Bing, zgłoszenie sitemapy, dostęp robotów i pomiar indeksacji. Nie uruchomiono tych działań i nie obiecuje się pozycji.

## Wyniki i ograniczenia

Bieżący raport: `docs/seo/pl-local-validation.json`; logi: `docs/seo/pl-local-logs/`. Wyniki są lokalne. Audyt techniczny nie stanowi potwierdzenia faktów, audytu prawnego, pełnej certyfikacji WCAG, jakości tłumaczeń, aktualności zewnętrznych linków ani wyników SEO. Po przyszłym wdrożeniu sprawdzić rzeczywiste odpowiedzi HTTP, przekierowania i nagłówki.
