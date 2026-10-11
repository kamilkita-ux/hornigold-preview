# Rejestr wdrożenia Hornigold — 2026-10-11

23.15: oba podglądy potwierdzone, mail do Marka w Wysłanych; produkcja nadal 23.11. Rezerwacja i Fiserv chronione.

Stan verified dotyczy wyłącznie wskazanego zakresu i środowiska.

| ID | Zakres | Stan | Zmiana / wynik | Bariera |
|---|---|---|---|---|
| A1 | Sprawdzenie środowisk | verified | Potwierdzono produkcję 23.11 oraz oba podglądy 23.15. GitHub main: a5fdacdfaa6872491911635881f881c576b136ab. | — |
| A2 | Identyfikacja pipeline Cloudflare | blocked | Sprawdzono oba dostępne konta; brak Workera Hornigold. | Marek: wskazać konto, Worker, gałąź, build i katalog wynikowy; potwierdzić dostęp. |
| A3 | Porównanie i wybór zmian | verified | Porównano sześć skryptów bajtowo; CSS ma dodatkowy moduł CloudMentor, a booking.js pochodzi od Marka. Przygotowano minimalną poprawkę Workera, która ich nie nadpisuje. | — |
| A4 | Kopia i rollback | local_ready | Kopia 23.15 na Mac mini: 1986 plików ze zweryfikowanymi hashami i historia Git. Odtworzenie poprzedniej 23.14: build 693 tras bez błędów. Kopia nie obejmuje konfiguracji ani bazy Cloudflare. | Marek: kopia konfiguracji i bazy Cloudflare. |
| A5 | Publikacja produkcyjna | partial | Bieżący odczyt produkcji nadal 23.11; oba podglądy 23.15. Nie potwierdzono aktualizacji Cloudflare. Zachować istniejącą rezerwację i Fiserv. | Marek: potwierdzić pipeline i wdrożyć minimalny patch serwera. |
| A6 | Podglądy | verified | Oba podglądy 23.15: po 693 trasy, zero błędów publicznego audytu; zatwierdzony Instagram na każdej stronie, noindex i brak analityki. | — |
| A7 | Ochrona pozostałych zmian | verified | Nie nadpisano pierwotnego checkoutu, DNS ani poczty. Właściciel dodatkowo chroni istniejący moduł rezerwacji i Fiserv: bez zmian kodu, konfiguracji i połączeń bez nowego polecenia. Dodano lokalną kontrolę hashy wskazanych chronionych plików; 6 testów. Nie podłączono do nieznanego pipeline. | — |
| B1 | GuestSage, PMS i operator | blocked | Sprawdzono publiczne UI sześciu języków: EN/DE/ES/IT bez opisów obiektu obecnych w PL; UK częściowo po angielsku. Chiński kierowany produkcyjnie do EN. Mapowanie typów apartamentów ROOMS pozostaje puste. | Recepcja/dostawca: aktualna usługa, PMS, płatności, siedem języków i środowisko testowe. |
| B2 | Spójność kontaktu i dokumentów | local_ready | Siedem języków HTML/PDF rozróżnia zapytanie, przekierowanie i potwierdzenie. Formularz uczciwie przygotowuje e-mail. | Recepcja: potwierdzić odbiór oznaczonej wiadomości; API wysyłki przyjęło zlecenie, doręczenie niezweryfikowane. |
| B3 | Rezerwacja i płatność end-to-end | blocked | Nie wykonano fikcyjnego testu płatności ani rezerwacji produkcyjnej. | Dostawcy: sandbox, dokumentacja, scenariusze sukces/odmowa/powtórzony webhook/zwrot; recepcja: potwierdzona taryfa. |
| C1 | Konto i ustawienia GA4 | verified | Właściwa usługa/strumień; pomiar zaawansowany wyłączony, Signals wyłączone, retencja 14 miesięcy bez resetu. | — |
| C2 | Zgody i ich cykl życia | verified | Cykl zgód testowany lokalnie; na produkcji 14 przypadków bez Google przed zgodą, rzeczywista akceptacja i wycofanie w Safari. Po ponownym otwarciu oba checkboxy odznaczone. | — |
| C3 | Zdarzenia i minimalizacja danych | partial | Produkcja ma zgody i sanitację parametrów. Potwierdzono page_view i stay_planner_click w GA4; opublikowano w podglądach poprawkę aliasów linków społecznościowych. Brak fałszywych lead/purchase. W 23.13 referrer ograniczony do jawnej listy znanych domen bez ścieżek i parametrów; nowe regresje przeszły. | Pomiar między domenami i przychód wymagają potwierdzonej integracji dostawcy. |
| C4 | Odbiór rzeczywistych zdarzeń | verified | Właściwa usługa GA4 pokazała kontrolowaną sesję: 2 page_view, first_visit, session_start i stay_planner_click. Zgoda po teście wycofana. | — |
| D1 | Układ mobile i CLS | verified | Produkcja ma skrócony układ i poprawioną propozycję języka; 14 przypadków mobile/desktop bez błędów. Laboratoryjny CLS maks. 0,075463. | — |
| D2 | Obrazy i wydajność | partial | 361 obrazów dekoduje się; 12 pomiarów laboratoryjnych po zmianach bez błędów. | Właściciel: komplet praw do obrazów. PSI ma limit; INP i rzeczywiste CWV wymagają ruchu i obserwacji. |
| D3 | Dostępność | partial | 1386 przypadków wszystkich tras (mobile/desktop) bez wykrytych naruszeń axe po ponowieniu testów przeciążonego serwera. 63 przypadki dokumentów/formularzy Chromium/Firefox/WebKit przeszły; HTML jest odpowiednikiem PDF. | Manualny odbiór czytnikiem ekranu i pełna przyszła ścieżka dostawcy. PDF-y nie mają znaczników; dostępny odpowiednik HTML zachowano. |
| E1 | SEO wszystkich adresów | verified | Publiczny audyt wszystkich 693 tras produkcji: 0 błędów i 0 ostrzeżeń; canonical, hreflang, metadane, statusy i nagłówki. | — |
| E2 | Linki i fragmenty | local_ready | 8582 fragmenty bez błędów; 172 linki zewnętrzne sprawdzono, wykryty adres 404 naprawiono we wszystkich 7 językach; 3 odpowiedzi wymagają ręcznej weryfikacji. | — |
| E3 | Search Console | partial | Sprawdzono siedem stron głównych w GSC: PL/EN/DE/ES/IT w indeksie, zh-Hans/UK nieznane; prośby o indeksację obu przyjęte przez Google. Sitemap nadal: nie udało się pobrać; publiczny XML 200 i 693 URL. | Google: pierwszy odczyt sitemapy nieudany; obserwacja 12.10, Marek: logi jeśli powtarzalne. |
| E4 | GSC, GA4 i stare dane | verified | Właściwe GSC połączone z nowym strumieniem GA4. Nie migrowano starych danych ani przekierowań. | Ads wymaga jednoznacznego konta i późniejszej decyzji; nie aktywowano. |
| F1 | Fakty i siedem języków | partial | Datowane źródła, zachowane intencje i odpowiedniki językowe; zewnętrzna rezerwacja ma jawne ograniczenie językowe. | Recepcja: potwierdzenie bieżącej oferty. Właściciel wcześniej zatwierdził własną kontrolę tłumaczeń; nie deklarujemy native review. |
| F2 | Schema i odpowiedzi AI | local_ready | ImageObject opublikowane w obu podglądach 23.14: 1911 encji na 546 stronach, publiczna kontrola 693 tras bez błędów. Pozostałe typy zachowane; bez niepotwierdzonych twierdzeń o prawach/licencjach. | Marek: wdrożenie Cloudflare i publiczny odbiór produkcji; prawa do zdjęć pozostają odrębnym G5. |
| G1 | Dostęp do istniejącego GBP | verified | Google pokazuje Zarządzasz tym profilem na koncie obiektu; zachowano profil i opinie. | — |
| G2 | NAP, kategorie, godziny | partial | Nazwa, Kopernika 6 i 608662707 zgodne; publiczne oznaczenie 4-gwiazdkowy wymaga wyjaśnienia. | Recepcja: formalna klasyfikacja/kategoria i godziny przed zmianą profilu. |
| G3 | Linki i profile zewnętrzne | partial | Zatwierdzony Instagram hornigold.zielona.kamienica opublikowano i sprawdzono na wszystkich 693 stronach obu podglądów 23.15. Produkcja nadal wskazuje poprzedni profil. | Marek: aktualizacja produkcji przez właściwy pipeline z zachowaniem rezerwacji i Fiserv. |
| G4 | Autentyczne opinie | local_ready | Przygotowano neutralny proces recepcji bez nagród/selekcji, z ochroną danych. | — |
| G5 | Zdjęcia i lokalne wzmianki | partial | Inwentaryzacja obrazów i wymóg weryfikacji praw. | Właściciel/partnerzy: prawa, faktyczne partnerstwa i publikacje; nie wymyślono wzmianek. |
| H1 | Bezpieczeństwo i odtworzenie | partial | Skan sekretów bez trafień; 3572/3572 plików odtworzono i zbudowano. Aktualizacja zależności: 10 high → 0 high; w 23.13 usunięto również ostatnie moderate po celowanej aktualizacji i teście zgodności migracji. Wymaganie pypdf 6.20.0 usuwa 31 zgłoszonych podatności biblioteki dokumentów; izolowany build PDF zgodny tekstowo 7/7. Audyt kodu: 48 testów JS, 10 Python, 21 plików JS i 30 Python bez błędów składni; skan 1539 plików tekstowych bez wykrytych sekretów. Patch 403/503 opublikowany w podglądach; produkcja oczekuje. | Marek: konfiguracja i kopia bazy Cloudflare oraz wdrożenie poprawki odpowiedzi 403/503. |
| I1 | Monitoring dostępności | partial | Rzeczywisty aktywny heartbeat Codex codziennie 07:30; checker 10/10. | Pierwszy zaplanowany przebieg 12.10; doręczenie alarmu jeszcze niepotwierdzone. |
| I2 | Kontrolowany alarm | partial | Kontrolowana symulacja została wykryta i zakończyła checker kodem 1. | Weryfikacja faktycznego kanału alertu przy pierwszym wykonaniu automatyzacji. |
| I3 | Dashboard | partial | Wewnętrzny panel pokazuje źródła, aktualność i brak danych zamiast zmyślonych liczb. | Dostęp do eksportów GA4/GSC i sprzedaży dla aktualizacji automatycznej. |
| J1 | Rejestr i dowody | verified | 34 pozycje, trwałe dowody i rozdzielenie stanów. | — |
| J2 | Utrzymanie i obserwacja | verified | Instrukcja publikacji, rollbacku, kopii i przeglądów; właściciele i terminy. | — |

Liczba pozycji: 34. {"verified": 13, "blocked": 3, "local_ready": 5, "partial": 13}. Nie jest to procent wykonania.
