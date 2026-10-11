# Przekazanie wydania 23.11

Kolejność publikacji, odtworzenia i testów: docs/implementation/MAINTENANCE.md. Pełny rejestr: docs/implementation/REGISTER.json.

1. Potwierdź właściwe konto, Worker, repozytorium/gałąź, build, katalog ASSETS i binding DB z Markiem. Obecne dostępne projekty FFP nie są projektem Hornigold.
2. Wykonaj kopię Mac mini, zachowaj poprzedni identyfikator wdrożenia oraz konfigurację i bazę. Nie nadpisuj zmian GuestSage poza repozytorium bez porównania.
3. Build preview / audyt, następnie production-ready / audyt i scripts/prepare_cloudflare_production.py. Oddziel oba artefakty. Schema dopuszczone zgodnie z datowanym dossier; bez cen, ocen i autorstwa bez źródła.
4. Wdrożenie wyłącznie potwierdzonym pipeline. Nie zmieniaj DNS, poczty ani pozostałych usług. Nie wdrażaj historycznej mapy przekierowań starej strony.
5. Odczyt publicznego release.json i commitu/manifestu; całe 693 trasy sitemap, canonical, hreflang, robots, 404, nagłówki i zasoby. Zweryfikuj brak noindex wyłącznie na kanonicznych stronach hornigold.pl. Podglądy pozostają zablokowane.
6. Test zgód przed/po odmowie/zgodzie/wycofaniu/wygaśnięciu, CSP i odbioru zdarzeń w GA4. Bez produkcyjnych rezerwacji i obciążeń. GuestSage/PMS/płatności testuj w sandboxie dostawcy.
7. GSC: ponów odczyt statusu zgłoszonej sitemapy i reprezentatywnych języków. Jeśli nadal niepobrana, sprawdź logi Cloudflare dla rzeczywistego Googlebota. Podrobiony user-agent nie dowodzi dostępu Google.
8. Monitoring po wdrożeniu i rollback przy regresji; zapisz wyniki i wersję środowiska. Nie deklaruj pozycji ani skuteczności sprzedaży bez danych.
