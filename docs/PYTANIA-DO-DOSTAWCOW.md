# Hornigold — pytania do KWHotel i Fiserv

Przygotowano 6 października 2026. Nie wysłano do dostawców. Właściciel potwierdził, że nie ma jeszcze dokumentacji API ani dostępu do sandboxa. Odpowiedzi prosimy przesłać jako dokumentację i informacje organizacyjne; klucze i hasła udostępniać wyłącznie bezpiecznym kanałem, poza e-mailem i repozytorium.

## Do KWHotel / dostawcy PMS

Temat: Hornigold — dostęp API do własnego systemu rezerwacji i sandbox

Dzień dobry,

przygotowujemy własny system rezerwacji na stronie Hornigold. Chcemy pobierać cenę i dostępność z PMS, tworzyć rezerwację oczekującą na płatność, a po zweryfikowanej płatności Fiserv potwierdzać ją w PMS. Prosimy o odpowiedź punkt po punkcie:

1. Jaki dokładnie produkt, wersja PMS, booking engine i channel manager są aktywne dla Hornigold? Który system jest źródłem dostępności i cen?
2. Czy nasza umowa obejmuje zewnętrzne API do takiego procesu? Jakie moduły, opłaty i limity są wymagane, a które opcjonalne? Prosimy rozdzielić koszty jednorazowe i stałe.
3. Prosimy o aktualną dokumentację API, sandbox i osobny obiekt testowy, bez wpływu na realną dostępność i portale rezerwacyjne.
4. Czy API pozwala atomowo zablokować dostępność i utworzyć rezerwację oczekującą? Jak zapobiega podwójnej sprzedaży ostatniego pokoju? Czy wspiera warunkowy zapis, hold/TTL i przedłużenie blokady?
5. Jak odczytać pełną cenę, podatki, walutę, dostępność, ograniczenia pobytu, obłożenie, taryfę i warunki anulowania? Jak oznaczona jest ważność oferty?
6. Prosimy o mapowanie identyfikatorów obiektu, kategorii pokoi, taryf, dorosłych/dzieci i wyposażenia oraz reguły dostępności grupowej.
7. Jakie operacje potwierdzają płatność/rezerwację, anulują blokadę i obsługują zwrot? Jakie dane finansowe trzeba przesłać? Czy można podać własny identyfikator płatności Fiserv?
8. Jak działają idempotencja, odczyt wyniku po timeout i wyszukiwanie rezerwacji po naszym identyfikatorze? Jakie są limity i kody błędów?
9. Czy PMS sam wysyła potwierdzenia, czy ma je wysyłać Hornigold? Prosimy o obsługiwane języki treści, błędów i wiadomości: PL, EN, DE, chiński uproszczony, UK, ES, IT. Prosimy wskazać ograniczenia każdego języka.
10. Jakie dane gościa są obowiązkowe, jakie role/uprawnienia API są dostępne oraz jakie są zasady ochrony danych, retencji i umowy powierzenia?
11. Czy powiadomienia PMS są uwierzytelniane i ponawiane? Jak odtworzyć stan po awarii oraz uzgodnić rezerwacje i płatności?
12. Prosimy o osobę techniczną do testów, kryteria odbioru oraz potwierdzenie, że własny interfejs Hornigold + Fiserv może współpracować z obecną konfiguracją i channel managerem.

Prosimy nie aktywować płatnej usługi ani produkcyjnych rezerwacji na podstawie tego zapytania. Najpierw potrzebujemy potwierdzenia możliwości, wyceny i testów.

## Do Fiserv / agenta rozliczeniowego

Temat: Hornigold — Hosted Checkout, API i bezpieczne powiadomienia o płatnościach

Dzień dobry,

chcemy połączyć własny system rezerwacji Hornigold z Hosted Checkout Fiserv. Gość będzie przekierowany do Fiserv; po uwierzytelnionym powiadomieniu i weryfikacji statusu nasz serwer potwierdzi rezerwację w PMS. Prosimy o odpowiedź punkt po punkcie:

1. Jaki dokładnie produkt Fiserv, region i model integracji są objęte naszą umową? Prosimy o nazwę API, wersję i aktualną dokumentację; nie tylko ogólny opis Hosted Checkout.
2. Czy mamy aktywny profil akceptanta i uprawnienia do utworzenia sesji przez backend Hornigold? Jakie koszty jednorazowe, stałe i transakcyjne są wymagane?
3. Prosimy o sandbox, testowe konto/store oraz dane testowe metod płatności. Jak oddzielić testy od rozliczeń produkcyjnych?
4. Jak tworzy się checkout, ustala walutę i kwotę, przekazuje identyfikator zamówienia, callback, webhook oraz język? Jakie domeny przekierowania są dozwolone i jak należy je zweryfikować?
5. Jak dokładnie weryfikować autentyczność webhooka dla **tego produktu**: nazwy nagłówków/pól, algorytm, sposób kanonizacji lub surowe bajty, kodowanie, timestamp, tolerancja czasu, ochrona przed replay, rotacja kluczy? Prosimy o oficjalne wektory testowe. Czy podpis obejmuje kwotę, walutę, status i identyfikatory?
6. Jak serwer odczytuje aktualny status sesji i transakcji po uwierzytelnionym API? Jak powiązać store, checkout, order i transaction ID? Co jest jednoznacznym dowodem zaksięgowania/capture, a co tylko autoryzacją?
7. Jakie są zasady idempotencji, ponawiania webhooków, kolejności zdarzeń, kodów ACK, timeoutów i lookup po przerwaniu żądania tworzącego sesję? Jak nie utworzyć dwóch płatności?
8. Jak długo ważna jest sesja i jak ją anulować? Co dzieje się z płatnością po jej wygaśnięciu i jak zapobiec zapłacie po zwolnieniu pokoju w PMS?
9. Jakie metody są dostępne w naszej umowie: karty, 3DS, BLIK, przelew, portfele? Jak działają SALE, preautoryzacja i capture, zaliczka, pełny/częściowy zwrot, chargeback i uzgadnianie rozliczeń?
10. Czy checkout, błędy i potwierdzenia obsługują PL, EN, DE, chiński uproszczony, UK, ES i IT? Prosimy o dokładne kody locale i ograniczenia. Czy można ustawić język niezależnie od kraju użytkownika?
11. Jakie są wymagania HTTPS, certyfikacji, PCI/SAQ, ochrony danych, logów i retencji dla przekierowania na Hosted Checkout? Jak wygląda bezpieczne przekazanie kluczy i ich rotacja?
12. Prosimy o osobę techniczną, plan testów sandbox i listę warunków uruchomienia live. Testy mają obejmować także fałszywy/duplikowany webhook, brak powrotu gościa, odmowę, awarię PMS po płatności i zwrot.

Prosimy nie aktywować płatnych usług ani obciążeń produkcyjnych na podstawie tego zapytania. Dane dostępowe przekazujmy wyłącznie uzgodnionym bezpiecznym kanałem.
