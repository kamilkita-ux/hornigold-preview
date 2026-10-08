# PAD - zakres, odpowiedzialność i odbiór dostępności

Stan: 2026-10-09, wydanie 23.8. **Przygotowane dokumenty; brak końcowej kwalifikacji spółki i brak odbioru integracji rezerwacji/płatności.** Nie jest to niezależna opinia prawna ani certyfikat.

## Wstępna kwalifikacja usługi

Planowana konsumencka rezerwacja przez stronę zmierzająca do zawarcia umowy jest usługą handlu elektronicznego w rozumieniu PAD (art. 3 ust. 2 pkt 6 i art. 5). Zakres nie ogranicza się do koszyka: obejmuje również identyfikację, bezpieczeństwo i płatności (art. 18). Obecny informacyjny serwis z przygotowaniem zapytania również wymaga kwalifikacji według faktycznej funkcji; samo wyłączenie automatycznej płatności nie dowodzi wyłączenia spod PAD.

Wyłączenie usług mikroprzedsiębiorcy (art. 4 pkt 1) nie zostało ustalone dla spółki Hornigold. Zarząd i księgowość muszą udokumentować właściwy status według aktualnego prawa, z uwzględnieniem wymaganych danych i relacji podmiotowych. Publiczny repozytorium nie jest miejscem na dokumenty finansowe lub kadrowe. Do czasu decyzji prace techniczne stosują wymagania dostępności; nie deklarują zwolnienia.

Treść dostawcy nie jest automatycznie wyłączona jako treść osoby trzeciej: przesłanki art. 4 pkt 2 lit. b muszą być ocenione łącznie (finansowanie, tworzenie, kontrola). Zakupiony/wybrany booking engine i Hosted Checkout nie mogą zostać pominięte tylko dlatego, że mają innego dostawcę. Mapy mogą korzystać z wyłączenia przy spełnieniu warunków; adres i położenie muszą pozostać dostępne tekstowo.

## Obowiązki do oceny i wdrożenia

| Zakres | Podstawa | Stan 23.8 | Właściciel / wymagany dowód |
|---|---|---|---|
| Kwalifikacja spółki i usługi, ewentualne wyłączenia | art. 3–5 | WYMAGA POTWIERDZENIA | Zarząd + księgowość/prawnik; datowana ocena |
| Informacja o usłudze, użyciu i dostępności w równoważnym dokumencie | art. 12 i 32 | WDROŻONA dla obecnego zakresu, nie certyfikat | 7 legal JSON, HTML i PDF; datowane wyniki kontroli |
| Pełna ocena zgodności usługi | art. 32 ust. 1 | CZĘŚCIOWE testy lokalnego frontendu; integracja nieodebrana | Integrator + audytor, manualne technologie wspomagające |
| Informacja o warunkach pomieszczeń i otoczenia w zakresie korzystania z usługi / rzeczywisty certyfikat | art. 33 | WYMAGA POTWIERDZENIA | Zarząd/recepcja: wejście, ciągi komunikacyjne, recepcja, łazienki, sposób pomocy; bez wymyślania cech |
| Zgłoszenia i skargi, odpowiedzi dostępne dla odbiorcy | art. 35–37 | Procedura opisana; organizacyjny odbiór wymagany | Zarząd: osoba i zastępstwo, protokół ustny, terminy, bezpieczna ewidencja |
| Utrzymanie informacji i wyników podczas oferowania usługi, aktualizacje i monitorowanie | art. 32 ust. 2 | WERSJONOWANIE dokumentów i plan odbioru przygotowane | Operator + integrator: ponowne testy po zmianach |
| Usuwanie niezgodności i niezwłoczne powiadomienie właściwego organu | art. 32 ust. 2 pkt 5–6 | PROCEDURA do wykonania po kwalifikacji/stwierdzeniu niezgodności | Zarząd; podpisane zawiadomienie; nic nie wysłano |
| Ewentualna zasadnicza zmiana / nieproporcjonalne obciążenie | art. 21 | NIE POWOŁANO SIĘ na wyjątek | Udokumentowana ocena + wymagane zawiadomienie, nie dowolny zapis stopki |
| Dokumenty i potwierdzenia dostępne, nie tylko widoczne wizualnie | art. 12, 18 | HTML dostępny; PDF-y NIEZNAKOWANE | Naprawa tagowania i walidacja PDF/UA, logiczna kolejność i ręczny odczyt; sam HTML nie stanowi odbioru całej usługi |

Ministerstwo publikuje wykaz norm/specyfikacji. WCAG 2.2 AA jest celem technicznym tego projektu, a nie automatycznym dowodem zgodności PAD. Wersję EN 301 549, zakres stosowania i podstawę ewentualnego domniemania zgodności należy ponownie sprawdzić przy odbiorze; nie zakładać, że zapowiadana aktualizacja normy już nastąpiła.

## Odbiór po podłączeniu usług (obecnie NIE WYKONANO)

Macierz `PAD_BOOKING_ACCEPTANCE.json` zawiera 15 etapów, 7 języków i wymagane metody. Każdy etap wymaga udokumentowanego wyniku, wersji silnika, adresu sandbox, daty i dowodu. Pole `accessibilityJourneyVerified` w release.json pozostaje false. Nie wolno oznaczyć go true na podstawie samego axe, instrukcji dostawcy, działającego iframe lub makiety.

1. Ustalić rzeczywisty produkt/wersję KWHotel i Fiserv, adres sandbox, zewnętrzne przekierowania, listę języków, osoby odpowiedzialne i kanał zgłoszeń do dostawców. Wystąpić o dostępność i udokumentowane ograniczenia konkretnych wersji, nie ogólną deklarację marki.
2. Przejść realny proces sandbox w PL/EN/DE/zh-Hans/UK/ES/IT. Brak języka lub dostępnej alternatywy zapisać jako ograniczenie integracji; nie uznać za zaliczone.
3. Testować automatycznie oraz manualnie: sama klawiatura, NVDA/Firefox lub Chrome, VoiceOver/Safari na macOS/iOS, TalkBack/Chrome na Androidzie; realne urządzenia i wersje zapisać w dowodzie. Nie deklarować testów czytnika na podstawie AX snapshot lub axe.
4. Sprawdzić reflow przy 320 CSS px i powiększeniu 400%, tekst 200%, spacing, kontrast, focus i brak zasłaniania, orientację oraz dotyk. W weryfikacji kognitywnej uwzględnić zrozumiałość instrukcji, cen, zobowiązania i odzyskiwanie błędów.
5. Formularze: kalendarz i ręczne daty, nazwy pól, required, autouzupełnianie, komunikaty powiązane z błędami, fokus po błędzie, walidacja bez koloru jako jedynego sygnału, brak utraty danych przy cofnięciu. Bez prawdziwych danych gości.
6. Płatność: dostępne podsumowanie, jednoznaczny przycisk, zgody bez przymusu marketingowego, przekierowanie i powrót z zachowaniem kontekstu, 3DS/SCA, odmowa, anulowanie, timeout i alternatywa dla niedostępnej metody. Nie obchodzić uwierzytelniania; rozwiązanie uzgodnić z operatorem.
7. Ograniczenia czasu i blokady dostępności: ostrzeżenie, możliwość wydłużenia tam, gdzie wymagana i możliwa, uzasadnione wyjątki, bezpieczne odzyskiwanie i brak podwójnej płatności. Nie wydłużać fikcyjnie blokady PMS bez potwierdzenia systemu.
8. Statusy oczekujący/opłacony/potwierdzony muszą być rozróżnialne i odczytywane przez technologie wspomagające bez nadmiernych powtórzeń. Test zamknięcia przeglądarki, opóźnienia webhooka i braku PMS; dostępność komunikatu nie zastępuje poprawności płatności.
9. Odebrać rzeczywiste wiadomości sandbox i pliki: temat, język, logiczna kolejność, linki, warunki trwałe, poprawna treść tekstowa, dostępność załączników. Sprawdzić zmianę, anulowanie, pełny i częściowy zwrot wraz z odpowiedzią.
10. Usunąć blokujące bariery, zweryfikować poprawki z dostawcami, udokumentować ograniczenia i wymagane działania prawne. Dopiero po rzeczywistym odbiorze uaktualnić publiczną informację i wydać decyzję o uruchomieniu. Kontakt recepcji/HTML nie jest automatycznym zwolnieniem z naprawy.

## Obsługa skarg - procedura organizacyjna do potwierdzenia

Wdrożony dokument podaje mail, telefon i adres oraz możliwość zgłoszenia osobistego/ustnego do protokołu. Zarząd musi przypisać osobę i zastępstwo, zapewnić dostępny format odpowiedzi i bezpieczną ewidencję poza GitHubem. Minimalne informacje skargi: imię/nazwisko, kontakt/preferowana odpowiedź, usługa, wymaganie/bariera i żądanie. Nie żądać diagnozy lub danych karty.

Termin odpowiedzi: 30 dni; szczególnie skomplikowana sprawa - informacja o przyczynie i nowym terminie w pierwszych 30 dniach, maksymalnie 60 dni od otrzymania. Odpowiedź zgodna z art. 37 ust. 5–6 (wynik, uzasadnienie odmowy albo termin realizacji nie dłuższy niż 6 miesięcy od odpowiedzi, osoba/stanowisko, właściwe pouczenia). Brak terminowej odpowiedzi ma skutek z art. 37 ust. 4: uznanie żądania i realizacja do 6 miesięcy od skargi. Skarga dostępności jest odrębna od zwykłej reklamacji pobytu. Nie ustawiono rzeczywistego systemu ticketowego ani nie potwierdzono dyżurów.

## Źródła sprawdzone 2026-10-09

- https://www.gov.pl/web/dostepnosc-cyfrowa/obowiazki-informacyjne-w-pad
- https://www.gov.pl/web/dostepnosc-cyfrowa/polski-akt-o-dostepnosci--uslugi-handlu-elektronicznego
- https://dziennikustaw.gov.pl/D2024000073101.pdf — art. 3–5, 12, 18, 21, 32–33, 35–38
- https://www.gov.pl/web/dostepnosc-cyfrowa/wykaz-norm-zharmonizowanych-i-specyfikacji-technicznych-dla-wymagan-dostepnosci-uslugi-handlu-elektronicznego
- docs/PMS-FISERV.md i docs/ONLINE_SALES_LAUNCH_GATES.md — dotychczasowe granice i niewykonane scenariusze.
