# Hornigold — utrzymanie i powrót do poprzedniej wersji
Aktualizacja: 2026-10-11. Właściciel decyzji: Kamil. Wdrożenie Cloudflare: Marek. Treści i fakty sprzedażowe: recepcja/Beata.

## Publikacja
1. Odczytaj AGENTS.md, git status i ostatni REGISTER.json. Nie nadpisuj równoległych zmian.
2. Uruchom scripts/backup_release.py na Mac mini i sprawdź readbackVerified oraz manifest SHA-256 poza repozytorium.
3. Zbuduj preview, wykonaj audit_static.py, audit_seo.py, audit_discovery.py, testy Node/Python i test przeglądarkowy zgód. Podglądy pozostają noindex, bez GA i transakcji.
4. Osobno zbuduj production-ready oraz uruchom audit_seo.py. scripts/prepare_cloudflare_production.py przygotowuje pakiet, nie publikuje.
5. Marek potwierdza konto, Worker, źródło/gałąź, komendę i katalog budowania. Zachowaj istniejące ASSETS, DB, domeny, pocztę i sekrety. Nie używaj projektu FFP.
6. Przed podmianą porównaj bieżący zewnętrzny odnośnik GuestSage i zmiany wykonane poza GitHub. Nie zastępuj nieznanych zmian pakietem w ciemno.
7. Publikuj wyłącznie w potwierdzonym pipeline. Zapisz identyfikator wdrożenia i commit/manifest. Push GitHub nie dowodzi aktualizacji Cloudflare.
8. Po wdrożeniu odczytaj release.json bez cache, robots, sitemap, HTML i zasoby oraz uruchom monitor_public.py. Porównaj wszystkie 693 trasy. Sprawdź zgody i rzeczywisty odbiór GA4 po świadomej zgodzie testera. Nie składaj rezerwacji produkcyjnych w ramach QA.

## Rollback
Zachowaj poprzedni identyfikator wdrożenia Cloudflare i jego konfigurację. W razie regresji przywróć ten identyfikator w tym samym Workerze, bez zmian DNS ani bazy. Ponownie odczytaj stronę i monitoring. Do powrotu kodu użyj osobnego checkoutu z history.bundle i working-source.tar.gz; sprawdź wszystkie hashe manifestu, zbuduj i zwaliduj. Nie wykonuj reset --hard ani force-push wspólnej gałęzi. GitHub: revert konkretnego commitu, ponowny build i kontrola Pages. Sites: wdrożenie zachowanej poprzedniej wersji tego samego projektu, bez usuwania DB.

## Faktyczne odtwarzanie
Odtworzono 3572 pliki źródłowe z kopii Mac mini, sprawdzono 3572 hashe, build 693 stron przeszedł. Dowód evidence/restore-test.json. Nie odtworzono konfiguracji Cloudflare, sekretów ani bazy produkcyjnej — wymagają dostępu Marka i osobnej kopii konfiguracji/bazy.

## Harmonogram i reakcja
Aktywny heartbeat Codex: hornigold-kontrola-produkcji-i-seo, codziennie 07:30 Europe/Warsaw, kanał: ten czat, odbiorca Kamil; problemy wdrożenia przekazuje Markowi. Stan prawidłowy pozostaje cichy. Po wdrożeniu: regresja; poniedziałki: GSC/GA4; miesięcznie: wydajność, treści i konwersje; kwartalnie: dostępność, bezpieczeństwo, uprawnienia i odtworzenie. Kontrolowany błąd wykrył checker, nie potwierdzono jeszcze doręczenia alarmu pierwszego zaplanowanego uruchomienia. Pierwsza obserwacja 12.10.2026.

## Obsługa treści i opinii
Recepcja co miesiąc potwierdza fakty, cenniki i warunki w datowanym dossier. Po zmianie usług aktualizuje 7 języków i odpowiadające PDF-y równocześnie. Dokumenty HTML pozostają dostępnym odpowiednikiem nieoznaczonych PDF-ów. Nie kopiuj cen i usług ze starej strony. Materiały historyczne są archiwum, nie źródłem nowej oferty.
Poproś każdego rzeczywistego gościa neutralnie o dobrowolną opinię; bez nagród, selekcji pozytywnych ocen i pisania opinii za gościa. Propozycja recepcji: „Dziękujemy za pobyt. Jeśli chcesz, podziel się swoim doświadczeniem w naszym istniejącym profilu Google”. Odpowiedzi na opinie nie mogą ujawniać danych pobytu. Prawa do zdjęć i aktualność profili należy potwierdzić przed nowymi publikacjami.
