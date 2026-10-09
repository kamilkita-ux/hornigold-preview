# Sprzedaż internetowa - warunki odbioru przed uruchomieniem

Data: 2026-10-09. Wersja: 23.7. Stan: dokumentacja opublikowana, sprzedaż i płatności NIEAKTYWNE. Sam regulamin w stopce ani poprawna etykieta nie stanowią odbioru integracji.

## Źródła i zakres ustaleń

- UOKiK, Prawo do informacji, sprawdzono 2026-10-09: https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/prawo-do-informacji/ — istotne informacje bezpośrednio przy zamówieniu oraz jednoznaczny obowiązek zapłaty.
- UOKiK, Wyłączenia, sprawdzono 2026-10-09: https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/wylaczenia-prawa-do-odstapienia/ — wyjątek dla usług na określony termin, nie uniwersalna bezzwrotność.
- KWHotel Cloud Booking Engine, instrukcja konfiguracji, aktualizacja dokumentu 2024-03-12, odczyt 2026-10-09: https://www.kwhotel.com/downloads/pl/15_kwhotel_booking_engine/KWHotel-Booking-Engine-Cloud-konfiguracja.pdf — ogólna konfiguracja; nie dowód produktu lub ustawień Hornigold.
- Fiserv Checkout Introduction, odczyt 2026-10-09: https://docs.fiserv.dev/public/docs/introduction-checkout — tworzenie checkout i przekierowanie, nie potwierdzenie przydziału produktu do Hornigold.
- Fiserv Webhooks and status updates, odczyt 2026-10-09: https://docs.fiserv.dev/public/docs/webhooks-and-status-updates-checkout — statusy i dodatkowy odczyt API; brak wystarczającego, przypisanego do konta kontraktu autentyczności webhooka.
- Przekazany przez właściciela NOWY REGULAMIN FIRMY HORNIGOLD[64].docx, odczyt lokalny 2026-10-09: opisuje 100% zapłaty i ofertę bezzwrotną. Zawiera różne nazwy/adresy operatora (First Data/Fiserv) oraz wyłączenia odpowiedzialności. Nie stanowi dowodu aktywnego konta ani mapowania taryf. Nie kopiowano rachunku bankowego ani szerokich wyłączeń odpowiedzialności do nowego dokumentu.

## Decyzje i dowody wymagane

| Wymaganie | Stan | Odpowiedzialny | Dowód odbioru |
|---|---|---|---|
| Konkretny produkt KWHotel, obiekt, mapowanie cen/taryf, API i atomowa blokada | WYMAGA POTWIERDZENIA | KWHotel + integrator | Dokumentacja konta i test ostatniego pokoju |
| Konkretny produkt i podmiot Fiserv, metody, opłaty, sandbox, autentyczność webhooka i status lookup | WYMAGA POTWIERDZENIA | Fiserv + integrator | Potwierdzenie konta i testy podpisu/kwoty/waluty |
| Moment zawarcia umowy; przyjęcie zamówienia a zapłata i gwarancja pobytu | DECYZJA | Zarząd + prawnik + integrator | Zatwierdzona reguła spójna z PMS, UI i mailami |
| Czy 100% bezzwrotna taryfa z dokumentu [64] jest jedyną czy jedną z taryf | DECYZJA | Zarząd/Beata | Zatwierdzone mapowanie konkretnych planów cenowych |
| Dla każdej taryfy kwota/procent, zaliczka/zadatek/pełna zapłata, termin i skutki braku wpłaty | DECYZJA | Zarząd/Beata | Tabela taryf zgodna z PMS |
| Anulowanie: data/godzina/strefa, wyliczenie opłaty; no-show, zmiana i skrócenie | DECYZJA | Zarząd/Beata + prawnik | Warunki taryf w zamówieniu i potwierdzeniu |
| Podstawy i terminy zwrotu, role operatorów, częściowy zwrot i awaria | WYMAGA POTWIERDZENIA | Zarząd + Fiserv + integrator | Procedura i sandbox pełnego/częściowego zwrotu |
| Bezpośrednie podsumowanie przed końcowym przyciskiem, korekta danych i brak zaznaczonych dodatków | PRZYGOTOWANE, NIEZINTEGROWANE | Integrator | Dostępny checkout z realną ofertą sandbox |
| Jednoznaczny przycisk w 7 językach | PRZYGOTOWANE, NIEZINTEGROWANE | Integrator | legal/checkout-contract.json + test rzeczywistego UI |
| Trwała treść kontraktu i wersji regulaminu w mailu/załączniku, odrębne statusy | WYMAGA POTWIERDZENIA | Integrator + recepcja | Odebrane wiadomości sandbox w 7 językach |
| Przegląd prawny ostatecznych taryf i procesu | WYMAGA ODBIORU | Zarząd + prawnik | Akceptacja finalnej konfiguracji, nie samego wzoru |

## Kolejność uruchomienia (nie wykonano)

1. Potwierdzić powyższe decyzje oraz produkt i umowy dostawców. Nie utożsamiać KWHotel DEV, Cloud, iframe i API; nie mieszać Fiserv Checkout API z IPG Connect.
2. Uzupełnić publiczne warunki o konkretne reguły i usunąć opis przygotowania dopiero po odbiorze. Zachować archiwalną wersję warunków dla każdej umowy.
3. Zaimplementować kontrakt legal/checkout-contract.json w rzeczywistym checkout, nie na statycznym GitHub Pages. Publiczna sekcja online-sales jest informacją o przygotowaniu, a nie aktywną ofertą.
4. Wykonać scenariusze sandbox z docs/PMS-FISERV.md: cena, konkurencyjny ostatni pokój, idempotencja, autoryzacja/capture, podpis, timeout, restart, opóźniony webhook, późna zapłata, PMS niedostępny, anulowanie, pełny/częściowy zwrot.
5. Przetestować podsumowanie, przycisk, błędy, regulamin, zapis wersji i trwałe potwierdzenia w 7 językach. Udokumentować ograniczenia zewnętrznych wersji językowych zamiast obiecywać pełną obsługę.
6. Uzyskać osobną zgodę na start sprzedaży, docelowy hosting i domenę. Dzisiejsza publikacja dokumentów NIE włącza płatności ani rezerwacji.
