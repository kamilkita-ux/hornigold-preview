# Update: revision 23.2, 2026-10-07

The owner subsequently authorized publishing preview improvements. The earlier local-only audit below is retained as historical evidence, not the current publication status. See `docs/AI_DISCOVERY_READINESS.md` and `docs/seo/discovery-*.json` for the multilingual discovery work. Production-ready remains unpublished and preview indexing protections remain mandatory. Publication success must be confirmed by the deployment platforms, not inferred from this document.

---

# SEO_RELEASE_READINESS

Stan lokalny: 6 października 2026. Repozytorium `hornigold-github-preview`, bezpieczny worktree `hornigold-seo-readiness-review`, gałąź `codex/seo-readiness-verified-20261006`.

Nie wykonano publikacji, push, zmian DNS, CMS, Search Console, analityki, profili Google, cen, dostępności ani integracji płatniczych. Plik źródłowy `release.json` nadal ma `indexing: false`. Tryb production-ready oznacza lokalny artefakt indeksowalny po późniejszym odbiorze, a nie uruchomioną produkcję.

Stan wejściowy zawierał niezapisane prace SEO. Zachowano go w zweryfikowanej kopii Mac mini i przeniesiono do osobnego worktree. Część rozwiązań została przejęta z tego snapshotu, następnie sprawdzona i uzupełniona. Nie nadpisano pierwotnego drzewa. Pochodzenie: `docs/seo/snapshot-provenance.json`.

| Wymaganie | Status | Dowód | Właściciel | Blocker |
|---|---|---|---|---|
| Oddzielne artefakty i jawny wybór trybu | GOTOWE LOKALNIE | `scripts/build.py`, `_site/`, `_production_ready/` | Wykonawca techniczny | Brak |
| Preview: noindex/nofollow/noarchive i Disallow: / | GOTOWE LOKALNIE | `docs/seo/audit-preview.json`, `site/robots.txt` | Wykonawca techniczny | Brak |
| Preview bez sitemapy | GOTOWE LOKALNIE | Audyt preview; brak XML w `_site/` | Wykonawca techniczny | Brak |
| Workflow publikuje wyłącznie preview | GOTOWE LOKALNIE | `.github/workflows/pages.yml`, `tests/test_seo.py` | Wykonawca techniczny | Lokalna zmiana nie jest wypchnięta |
| Ochrona przed pakowaniem production-ready przez Sites | GOTOWE LOKALNIE | `scripts/build_sites.mjs`, testy bezpieczeństwa | Wykonawca techniczny | Brak |
| Produkcyjny robots dla hornigold.pl | PRZYGOTOWANE DO PRODUKCJI | `_production_ready/robots.txt` | Wykonawca techniczny / wdrażający | Późniejszy odbiór hostingu |
| Sitemap: 693 unikalne kanoniczne URL | PRZYGOTOWANE DO PRODUKCJI | `_production_ready/sitemap.xml`, audyt production-ready | Wykonawca techniczny | Późniejsza publikacja właściwego artefaktu |
| Canonicale tylko https://hornigold.pl | GOTOWE LOKALNIE | Oba raporty SEO, pełny inwentarz 693 tras | Wykonawca techniczny | Brak |
| 7 języków, wzajemne hreflang i x-default | GOTOWE LOKALNIE | 8 wpisów na każdą trasę; x-default = polski odpowiednik | Wykonawca techniczny | Brak |
| URL canonical/hreflang/sitemap istnieją i nie są blokowane w production-ready | GOTOWE LOKALNIE | `scripts/audit_seo.py`, lokalna analiza robots | Wykonawca techniczny | Statusy HTTP na przyszłym hostingu sprawdzić po wdrożeniu |
| Unikalne title i meta description | GOTOWE LOKALNIE | `seo/metadata-overrides.json`, oba audyty | Redakcja / wykonawca | Ocena jakości językowej przez native speakerów jest osobnym odbiorem |
| Dokładnie jeden niepusty H1 na każdej kanonicznej stronie | GOTOWE LOKALNIE | Oba audyty | Wykonawca techniczny | Brak |
| Open Graph i Twitter Card, dostępne obrazy i etykiety | GOTOWE LOKALNIE | `scripts/seo.py`, oba audyty | Wykonawca techniczny | Podgląd kart w usługach zewnętrznych poza zakresem |
| Opisy alternatywne obrazów | GOTOWE LOKALNIE | Kontrola 2604 wystąpień img; źródła niezmienione | Redakcja / wykonawca | Prawa i fakty zdjęciowe podlegają odbiorowi redakcyjnemu |
| Grafika: optymalizacja formatu bez zmiany pikseli | GOTOWE LOKALNIE | `seo/asset-optimizations.json`: -23,6%, 7 języków; `optimized-image-regression.json`: 42 przypadki i 14 axe bez błędów | Wykonawca techniczny | Oryginał zachowany |
| Linki, fragmenty, zasoby CSS i mixed content | GOTOWE LOKALNIE | 68963 odwołania na artefakt; zero błędów | Wykonawca techniczny | Linków zewnętrznych nie odpytywano |
| Brak osieroconych tras, duplikatów głównej treści i pętli aliasów | GOTOWE LOKALNIE | 693 osiągalne trasy, 539 aliasów | Wykonawca techniczny | Brak |
| JSON-LD tylko WebPage bez twierdzeń biznesowych | GOTOWE LOKALNIE | `seo/structured-data-policy.json`, `source-schema-review.json` | Wykonawca techniczny | Brak dla minimalnego zakresu |
| Telefon, godziny, pokoje, udogodnienia, opinie i ceny w rozszerzonym schema | WYMAGA POTWIERDZENIA; POMINIĘTE | `source-schema-review.json`, datowane źródło rejestrowe tylko w `legal/operator-verification.json` | Hornigold / redakcja | Datowany dossier z potwierdzeniem każdego pola; schema biznesowe nie jest warunkiem technicznej indeksowalności |
| Szkic 301: 1078 wierszy dla 539 aliasów | PRZYGOTOWANE DO PRODUKCJI | `REDIRECT_MAP_DRAFT.csv`, `redirect-map.json` | Wdrażający / Hornigold | Eksport URL starego serwisu, zatwierdzenie mapy i obsługa HTTP 301 na hostingu |
| Responsywność i dostępność | GOTOWE LOKALNIE: 1386 AXE + 819 PRZYPADKÓW; PO OPTYMALIZACJI 42 DODATKOWE I 14 AXE | `docs/seo/accessibility-production-ready.json`, `browser-preview.json` | Wykonawca / odbiór ręczny | Automaty nie zastępują pełnego WCAG ani fizycznych urządzeń |
| Wydajność lokalna | GOTOWE LOKALNIE: 38 WIDOKÓW, ZERO BŁĘDÓW | `docs/seo/performance-local.json` | Wykonawca / wdrażający | Dane od rzeczywistych użytkowników dopiero po uruchomieniu |
| Skan sekretów i prywatnych plików | GOTOWE LOKALNIE: BEZ WYKRYTYCH SEKRETÓW | `docs/seo/secrets-scan.json` | Wykonawca techniczny | Skan wzorców nie dowodzi nieobecności każdego możliwego sekretu |
| Testy ochrony trybów i regresji | GOTOWE LOKALNIE | `safety-tests.txt`: 10; `server-regression.txt`: 6 | Wykonawca techniczny | Brak |
| Wdrożenie, domena, Search Console i pomiar | WYMAGA ZEWNĘTRZNEJ DECYZJI | `SEO_PRODUCTION_HANDOFF.md` | Właściciel / wdrażający | Wybór hostingu, zgoda na domenę i indeksowanie, dostęp do właściwych usług |
| Kompletna sprzedaż online | POZA ZAKRESEM SEO; NIEAKTYWNA | `release.json`, `docs/PMS-FISERV.md` | Hornigold / dostawcy | Odbiór PMS, płatności i dokumentów przed sprzedażą |

Raporty nie dowodzą indeksacji, pozycji w Google, rzeczywistych Core Web Vitals ani zgodności prawnej lub pełnego WCAG. Przekierowania w mapie są szkicem; nie wdrożono żadnych nowych przekierowań.

## Przebieg testów przeglądarek

Pierwszy przebieg 819 przypadków, równoległy z axe, zgłosił pojedynczy komunikat Firefoksa o dekodowaniu obrazu. Pełne dekodowanie wszystkich 360 plików rastrowych nie wykazało uszkodzeń. Powtórzenie całego przebiegu bez równoległego axe zakończyło się 819/819 bez błędów. Pierwszy wynik zachowano w `docs/seo/browser-preview-first-run.json`; nie ustalono jednoznacznej przyczyny incydentu i nie ukryto go w raporcie. Nie zmieniano fotografii.

## Wydajność laboratoryjna

38 widoków, zimny kontekst przeglądarki, localhost na Mac mini, bez ograniczenia sieci lub CPU. Mediana obserwowanego LCP 68 ms, maksimum 112 ms; maksimum obserwowanego CLS 0. Największy transfer spadł z 3 026 377 do 2 338 814 bajtów po bezstratnej zmianie formatu ilustracji. Wyniki dotyczą tylko lokalnej próby i 1 sekundy obserwacji po załadowaniu. Nie zmierzono INP ani danych rzeczywistych użytkowników. Docelowy hosting, sieć, kompresja i cache wymagają ponownego pomiaru.

## Odczyt wizualny i zapis

Obejrzano aktualne zrzuty `docs/seo/home-375.png` i `home-1366.png`: nagłówek, kontakt, formularz i podgląd przewodnika pozostają czytelne w tych dwóch widokach. To ograniczona kontrola wizualna, nie odbiór wszystkich ekranów ani fizycznych urządzeń. Pełny protokół zbiorczy: `docs/seo/final-summary.json`. Wszystkie zmiany tej gałęzi pozostają lokalne.
