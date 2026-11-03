# SEO / AI-search — wykonanie od 03.11.2026

Źródło wymagań: wersja 2.0 załączona przez właściciela, zachowana obok rejestru. 70 zadań pozostaje w zakresie; żadne nie jest usuwane, aby podnieść wynik. Praca w kolejności numerów. Osiem języków, czeski trzeci; chronione GuestSage/KWHotel/Fiserv bez zmian.

| ID | Zmiana | Pliki | Test | Dowód | Czas |
|---|---|---|---|---|---|
| T-01 | Dodano powtarzalny profil sześciu stron, progi 95/98/100/100; istniejący profil CI zachowany | scripts/audit_lighthouse.mjs, release.json | Bazowy build 793 tras, 0 błędów; sześć stron PASS: Performance97–99, pozostałe kategorie100 | T01_LIGHTHOUSE_BASELINE.json; pełne HTML/JSON prywatnie /Users/kamilkita/Documents/Hornigold-audits/2026-11-03/t01-baseline | daty w summary.json |
| T-02 | Dodano preload istniejącego obrazu hero zgodny z srcset/sizes oraz eager/high/async we wszystkich wersjach | scripts/build.py | W toku, brak odbioru T-02 | prywatny pomiar baseline: home LCP2.48s, CLS0, TBT0 | 03.11.2026 |

Wersja przygotowywana:23.33. Bump wersji w pliku nie dowodzi publikacji. Lokalne pomiary Lighthouse nie są danymi PSI ani CrUX; TBT nie jest INP. T-02 wymaga osobnego potwierdzenia terenowego i formatów AVIF; nie jest ukończone. Nie przechodzimy do T-03 przed spełnieniem jego poprzednika zgodnie ze zleceniem.

W załączniku są przykładowe ceny, czasy i klasyfikacja. Nie uznajemy ich za potwierdzony cennik ani dokument klasyfikacji. Przy zadaniach treści źródłem będą wyłącznie potwierdzone i datowane fakty. Cel TOP10/90%indeksacji nie jest wynikiem, który można zapewnić kodem lub zadeklarować przed odczytem Google.

Uruchomienie T-01: `LIGHTHOUSE_PROFILE=seo100 LIGHTHOUSE_URL=http://127.0.0.1:4403 LIGHTHOUSE_OUTPUT=/prywatny/katalog node scripts/audit_lighthouse.mjs` po lokalnym buildzie production-ready. Profil odrzuca publiczny host, aby nie generować testowego ruchu produkcji.

Końcowy powtórzony pomiar23.33: 6/6PASS, Performance97–99, Accessibility/BestPractices/SEO100; T01_RELEASE2333.json. Pierwszy przebieg nowej wersji miał ERR_SOCKET_NOT_CONNECTED w lokalnym serwerze dla czterech skryptów DE (BestPractices96); pełny ponowny przebieg po sprawdzeniu błędu przeszedł. Nie usunięto audytu ani nie obniżono progu. Audyt793tras/1343HTML/89763linków/3770obrazów: 0błędów i0ostrzeżeń;181/181testówNodePASS. PSI HTTP429: wyczerpany publiczny limit Queries per day; bez wyniku PSI/CrUX.
