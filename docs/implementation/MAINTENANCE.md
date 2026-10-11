# Hornigold — utrzymanie i powrót do poprzedniej wersji
Aktualizacja: 2026-10-12. Właściciel decyzji: Kamil. Wdrożenie Cloudflare: Marek. Treści i fakty sprzedażowe: recepcja/Beata.

## Publikacja
1. Odczytaj AGENTS.md, git status i ostatni REGISTER.json. Nie nadpisuj równoległych zmian.
2. Uruchom scripts/backup_release.py na Mac mini i sprawdź readbackVerified oraz manifest SHA-256 poza repozytorium.
3. Zbuduj preview, wykonaj audit_static.py, audit_seo.py, audit_discovery.py, testy Node/Python i test przeglądarkowy zgód. Podglądy pozostają noindex, bez GA i transakcji.
4. Osobno zbuduj production-ready poleceniem `python3 scripts/build.py --mode production-ready --base / --counter --production-counter`, zachowując istniejący licznik i DB. Następnie oraz uruchom audit_seo.py. scripts/prepare_cloudflare_production.py przygotowuje pakiet, nie publikuje.
5. Marek potwierdza konto, Worker, źródło/gałąź, komendę i katalog budowania. Zachowaj istniejące ASSETS, DB, domeny, pocztę i sekrety. Nie używaj projektu FFP.
6. Przed podmianą porównaj bieżący zewnętrzny odnośnik GuestSage i zmiany wykonane poza GitHub. Istniejący moduł rezerwacji i Fiserv są nietykalne bez nowego wyraźnego polecenia właściciela. Nie kopiuj całego podglądu na produkcję. Stosuj PROTECTED_INTEGRATIONS.md dla jawnie wskazanych plików; kontrola hashy nie zastępuje ochrony konfiguracji i połączeń.
7. Publikuj przetestowane kolejne wersje do istniejących podglądów niezależnie od Cloudflare: przygotowanie codex/cloudflare-production-seo-20261009, publikacja main. Zachowaj noindex i wyłączoną analitykę podglądów. Marek aktualizuje produkcję osobno. Zapisz identyfikatory wdrożeń, commit i wyniki publicznego odczytu. Push GitHub nie dowodzi aktualizacji Cloudflare. Po publikacji wyślij Markowi podsumowanie z lu@farmyfotowoltaiki.pl i potwierdź Wysłane.
8. Po wdrożeniu odczytaj release.json bez cache, robots, sitemap, HTML i zasoby oraz uruchom monitor_public.py. Porównaj wszystkie 693 trasy. Sprawdź zgody i rzeczywisty odbiór GA4 po świadomej zgodzie testera. Nie składaj rezerwacji produkcyjnych w ramach QA.

## Rollback
Zachowaj poprzedni identyfikator wdrożenia Cloudflare i jego konfigurację. W razie regresji przywróć ten identyfikator w tym samym Workerze, bez zmian DNS ani bazy. Ponownie odczytaj stronę i monitoring. Do powrotu kodu użyj osobnego checkoutu z history.bundle i working-source.tar.gz; sprawdź wszystkie hashe manifestu, zbuduj i zwaliduj. Nie wykonuj reset --hard ani force-push wspólnej gałęzi. GitHub: revert konkretnego commitu, ponowny build i kontrola Pages. Sites: wdrożenie zachowanej poprzedniej wersji tego samego projektu, bez usuwania DB.

## Faktyczne odtwarzanie
Odtworzono 3572 pliki źródłowe z kopii Mac mini, sprawdzono 3572 hashe, build 693 stron przeszedł. Dowód evidence/restore-test.json. Nie odtworzono konfiguracji Cloudflare, sekretów ani bazy produkcyjnej — wymagają dostępu Marka i osobnej kopii konfiguracji/bazy.

## Harmonogram i reakcja
Aktywny heartbeat Codex: hornigold-kontrola-produkcji-i-seo, codziennie 07:30 Europe/Warsaw, kanał: ten czat, odbiorca Kamil; problemy wdrożenia przekazuje Markowi. Stan prawidłowy pozostaje cichy. Po wdrożeniu: regresja; poniedziałki: GSC/GA4; miesięcznie: wydajność, treści i konwersje; kwartalnie: dostępność, bezpieczeństwo, uprawnienia i odtworzenie. Kontrolowany błąd wykrył checker, nie potwierdzono jeszcze doręczenia alarmu pierwszego zaplanowanego uruchomienia. Pierwsza obserwacja 12.10.2026.

## Obsługa treści i opinii
Recepcja co miesiąc potwierdza fakty, cenniki i warunki w datowanym dossier. Po zmianie usług aktualizuje 7 języków i odpowiadające PDF-y równocześnie. Od 23.18 PDF-y zawierają znaczniki struktury; HTML pozostaje dodatkowym odpowiednikiem. Nie deklarujemy PDF/UA ani ukończonego odbioru czytnikiem. Starszy generator odmawia nadpisania oznaczonych plików; kontroluj strukturę w CI przed publikacją. Nie kopiuj cen i usług ze starej strony. Materiały historyczne są archiwum, nie źródłem nowej oferty.
Poproś każdego rzeczywistego gościa neutralnie o dobrowolną opinię; bez nagród, selekcji pozytywnych ocen i pisania opinii za gościa. Propozycja recepcji: „Dziękujemy za pobyt. Jeśli chcesz, podziel się swoim doświadczeniem w naszym istniejącym profilu Google”. Odpowiedzi na opinie nie mogą ujawniać danych pobytu. Prawa do zdjęć i aktualność profili należy potwierdzić przed nowymi publikacjami.

## Automatyczne kontrole GitHub — potwierdzony przebieg
Po zakończonej sukcesem publikacji Pages uruchamia się Hornigold publication check. Run 38180305635 po wersji 23.17 zakończył się sukcesem: 693 trasy podglądu bez błędów, odczytowy monitor produkcji i Lighthouse dla /pl/, /pl/pokoje/ oraz /en/. Raporty pobrano trwale do evidence; artefakty GitHub wygasają po 7 dniach. Nie jest to test transakcji ani potwierdzenie aktualizacji Cloudflare. Workflow raportowania błędów pozostaje niezweryfikowany w zakresie rzeczywistego dostarczenia alarmu. Codzienny heartbeat 07:30 oraz tygodniowe kontrole mają oddzielny harmonogram; sukces kontroli po publikacji nie dowodzi ich wykonania.

Próba odtworzenia 23.17 (12.10.2026): 2015/2015 hashy, kompletna historia Git, build 693 tras, 24 testy Python oraz kontrola 75106 linków i SEO bez błędów. Dowód: evidence/restore-23.17.json. Próba nie obejmuje konfiguracji, bazy ani rzeczywistych transakcji Cloudflare.

## Tożsamość audytowanego wdrożenia
Kontrola Pages otrzymuje oczekiwany commit z uruchomienia publikacji. Odczytuje release.json przed audytem wszystkich tras i po nim; wymagane są poprawny transport, ten sam commit i revision, zgodność oczekiwanego commitu oraz istniejące kontrole noindex, canonical i wyłączonej analityki. Rozbieżność zatrzymuje kontrolę; nie oznaczamy jej automatycznie jako nieszkodliwej nowszej publikacji, ponieważ to wymaga osobnego dowodu. Sites może używać osobnego commitu źródeł; nie porównujemy go z commitem GitHub.
