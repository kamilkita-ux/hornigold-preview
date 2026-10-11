# Rejestr wdrożenia Hornigold — 2026-10-11

Stan local_ready nie oznacza publikacji produkcyjnej.

| ID | Zakres | Stan | Zmiana / wynik | Bariera |
|---|---|---|---|---|
| A1 | Sprawdzenie środowisk | verified | Odczyt produkcji 23.9, Pages 23.10, Sites 23.9 i źródeł. | — |
| A2 | Identyfikacja pipeline Cloudflare | blocked | Sprawdzono oba dostępne konta; brak Workera Hornigold. | Marek: wskazać konto, Worker, gałąź, build i katalog wynikowy; potwierdzić dostęp. |
| A3 | Porównanie i wybór zmian | local_ready | Zachowano istniejący odnośnik GuestSage; neutralne dokumenty, zgody, mobilny układ i schema. | Nieznane zmiany wdrożone przez Marka poza źródłem należy uzgodnić przed podmianą. |
| A4 | Kopia i rollback | local_ready | Kopia na Mac mini; 3572/3572 hashy i odtworzony build. | Marek: kopia konfiguracji i bazy Cloudflare. |
| A5 | Publikacja produkcyjna | blocked | Przygotowany izolowany pakiet Cloudflare; nie wdrożono do produkcji. | Właściwy pipeline i dostęp Marka. |
| A6 | Podglądy | local_ready | Preview pozostaje noindex, Disallow /, bez pomiaru produkcyjnego i transakcji. | — |
| A7 | Ochrona pozostałych zmian | verified | Nie nadpisano pierwotnego brudnego checkoutu; nie zmieniono DNS i poczty. | — |
| B1 | GuestSage, PMS i operator | blocked | Zewnętrzny link odpowiada 200; odbiór funkcjonalny niepotwierdzony. Wysłano zapytanie do recepcji. | Recepcja/dostawca: aktualna usługa, PMS, płatności, siedem języków i środowisko testowe. |
| B2 | Spójność kontaktu i dokumentów | local_ready | Siedem języków HTML/PDF rozróżnia zapytanie, przekierowanie i potwierdzenie. Formularz uczciwie przygotowuje e-mail. | Recepcja: potwierdzić odbiór oznaczonej wiadomości; API wysyłki przyjęło zlecenie, doręczenie niezweryfikowane. |
| B3 | Rezerwacja i płatność end-to-end | blocked | Nie wykonano fikcyjnego testu płatności ani rezerwacji produkcyjnej. | Dostawcy: sandbox, dokumentacja, scenariusze sukces/odmowa/powtórzony webhook/zwrot; recepcja: potwierdzona taryfa. |
| C1 | Konto i ustawienia GA4 | verified | Właściwa usługa/strumień; pomiar zaawansowany wyłączony, Signals wyłączone, retencja 14 miesięcy bez resetu. | — |
| C2 | Zgody i ich cykl życia | local_ready | 14 przypadków GA4 w przeglądarce, 3 testy jednostkowe cyklu oraz rzeczywista synchronizacja dwóch kart i aktywne wygaśnięcie; przed zgodą brak Google. | — |
| C3 | Zdarzenia i minimalizacja danych | local_ready | click_phone, click_email, booking_click, select_apartment; bez fałszywych lead/purchase. UTM allowlist; brak dowolnego referrera. | Pomiar między domenami i przychód wymagają potwierdzonej integracji dostawcy. |
| C4 | Odbiór rzeczywistych zdarzeń | blocked | Lokalne testy nie wysyłały do Google; produkcja nadal nie ma nowego kodu. | Po wdrożeniu: świadoma zgoda testera i odczyt właściwego GA4. |
| D1 | Układ mobile i CLS | local_ready | Usunięto przesunięcie wywołane propozycją języka; 3 pokoje i krótsza strona główna. | — |
| D2 | Obrazy i wydajność | partial | 361 obrazów dekoduje się; 12 pomiarów laboratoryjnych po zmianach bez błędów. | Właściciel: komplet praw do obrazów. PSI ma limit; INP i rzeczywiste CWV wymagają ruchu i obserwacji. |
| D3 | Dostępność | partial | 28 przypadków axe bez naruszeń; dostępne HTML odpowiadają PDF. | Pełny odbiór z czytnikiem ekranu/użytkownikami i oznaczone PDF-y; ścieżka dostawcy wymaga sandboxu. |
| E1 | SEO wszystkich adresów | local_ready | 693 trasy, canonical, hreflang, H1 i metadane; audyt bez błędów. | — |
| E2 | Linki i fragmenty | local_ready | 8582 fragmenty bez błędów; 172 linki zewnętrzne sprawdzono, wykryty adres 404 naprawiono we wszystkich 7 językach; 3 odpowiedzi wymagają ręcznej weryfikacji. | — |
| E3 | Search Console | partial | Własność zweryfikowana, sitemapę przesłano, PL i EN zaindeksowane. | Google: pierwszy odczyt sitemapy nieudany; obserwacja 12.10, Marek: logi jeśli powtarzalne. |
| E4 | GSC, GA4 i stare dane | verified | Właściwe GSC połączone z nowym strumieniem GA4. Nie migrowano starych danych ani przekierowań. | Ads wymaga jednoznacznego konta i późniejszej decyzji; nie aktywowano. |
| F1 | Fakty i siedem języków | partial | Datowane źródła, zachowane intencje i odpowiedniki językowe; zewnętrzna rezerwacja ma jawne ograniczenie językowe. | Recepcja: potwierdzenie bieżącej oferty. Właściciel wcześniej zatwierdził własną kontrolę tłumaczeń; nie deklarujemy native review. |
| F2 | Schema i odpowiedzi AI | local_ready | 693 WebPage/LodgingBusiness/Organization, 686 BreadcrumbList, 7 FAQPage i 49 Article; tylko datowane źródła i widoczna treść. | ImageObject i autorstwo wymagają udokumentowanych praw; brak źródła nie zatrzymał pozostałych typów. |
| G1 | Dostęp do istniejącego GBP | verified | Google pokazuje Zarządzasz tym profilem na koncie obiektu; zachowano profil i opinie. | — |
| G2 | NAP, kategorie, godziny | partial | Nazwa, Kopernika 6 i 608662707 zgodne; publiczne oznaczenie 4-gwiazdkowy wymaga wyjaśnienia. | Recepcja: formalna klasyfikacja/kategoria i godziny przed zmianą profilu. |
| G3 | Linki i profile zewnętrzne | partial | WWW i publiczny GuestSage istnieją; GBP Instagram różni się od linku projektu. | Właściciel: wskazać aktywny Instagram; nie nadpisywać niepotwierdzonego profilu. |
| G4 | Autentyczne opinie | local_ready | Przygotowano neutralny proces recepcji bez nagród/selekcji, z ochroną danych. | — |
| G5 | Zdjęcia i lokalne wzmianki | partial | Inwentaryzacja obrazów i wymóg weryfikacji praw. | Właściciel/partnerzy: prawa, faktyczne partnerstwa i publikacje; nie wymyślono wzmianek. |
| H1 | Bezpieczeństwo i odtworzenie | partial | Skan sekretów bez trafień; 3572/3572 plików odtworzono i zbudowano. Aktualizacja zależności: 10 high → 0 high; pozostało 1 moderate w narzędziu developerskim. | Marek: konfiguracja i kopia bazy Cloudflare. Pozostały esbuild developerski: nie udostępniać serwera; czekać na zgodną aktualizację dostawcy. |
| I1 | Monitoring dostępności | partial | Rzeczywisty aktywny heartbeat Codex codziennie 07:30; checker 10/10. | Pierwszy zaplanowany przebieg 12.10; doręczenie alarmu jeszcze niepotwierdzone. |
| I2 | Kontrolowany alarm | partial | Kontrolowana symulacja została wykryta i zakończyła checker kodem 1. | Weryfikacja faktycznego kanału alertu przy pierwszym wykonaniu automatyzacji. |
| I3 | Dashboard | partial | Wewnętrzny panel pokazuje źródła, aktualność i brak danych zamiast zmyślonych liczb. | Dostęp do eksportów GA4/GSC i sprzedaży dla aktualizacji automatycznej. |
| J1 | Rejestr i dowody | local_ready | 34 pozycje, trwałe dowody i rozdzielenie stanów. | — |
| J2 | Utrzymanie i obserwacja | local_ready | Instrukcja publikacji, rollbacku, kopii i przeglądów; właściciele i terminy. | — |
