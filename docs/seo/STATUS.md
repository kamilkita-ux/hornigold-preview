# STATUS — migracja SEO Hornigold, 16.10.2026

## Potwierdzone publicznie

* `hornigold.pl` jest działającą domeną kanoniczną, z HTTPS, poprawnym `www` → apex i aktywną mapą witryny.
* Publiczne podglądy GitHub Pages pozostają wyłączone z indeksacji.
* Klasyczne ścieżki WordPressa nie udostępniają starej treści: badane endpointy zwracają 404.
* Search Console widzi aktywną sitemapę i ruch organiczny, ale nadal utrzymuje historyczne adresy 404 oraz duplikaty.

## Przygotowane lokalnie

* Precyzyjne 301 dla potwierdzonych adresów WordPress `page_id` i `portfolio-item`.
* 410 dla nieznanych, wycofanych identyfikatorów zamiast przekierowania na stronę główną.
* Tabela migracji `URL_MIGRATION_TABLE.csv`: 577 pozycji — 539 historycznych aliasów ścieżek, potwierdzone query-URL, hosty historyczne i grupa bez bezpiecznego odpowiednika.
* Snapshot rollbacku poprzedniej logiki źródłowej przed zmianą, bez ingerencji w DNS, pocztę i bindingi Cloudflare.
* Lokalny artefakt Cloudflare zawiera nowy moduł migracyjny; 34 testy serwera i indeksacji przeszły, podobnie jak 3 testy artefaktu. Audyt offline production-ready: 793 tras, 539 aliasów przekierowań, 0 błędów i 0 ostrzeżeń.

## Niewdrożone / blokery

* Ta gałąź nie została wypchnięta ani wdrożona; `hornigold.pl` nadal wykonuje poprzednią regułę ogólnego przekierowania.
* Brak aktualnego eksportu pełnej listy URL z Search Console i starych logów/backupów WordPressa. Bez nich nie wolno tworzyć masowych reguł dla całej puli 1 200 adresów 404.
* Brak dostępu do aktywnej konfiguracji Cloudflare w tym zadaniu; po zaakceptowaniu kodu wdrożenie musi przejść zwykłą ścieżką GitHub → kontrola Marka → Cloudflare → publiczny odczyt.

## Następny krok

Przekazać gałąź `codex/seo-migration-20261016` do kontroli Marka. Dopiero po potwierdzonym publicznym odczycie można zgłosić wdrożenie w Search Console jako wykonane.
