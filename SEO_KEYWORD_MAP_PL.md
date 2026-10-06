# Mapa intencji SEO PL — przygotowanie lokalne, 07.10.2026

Adresy poniżej są przyszłymi adresami kanonicznymi, nie dowodem publikacji nowej wersji na `hornigold.pl`. Nie sprawdzano wolumenów fraz, pozycji ani konkurencji. Dopasowanie jest redakcyjne, na podstawie istniejącej treści. Nie dodano osobnych stron pod warianty tej samej frazy.

| Fraza | Intencja | Docelowy URL | Istniejący dowód w treści | Status faktów | Następny krok |
|---|---|---|---|---|---|
| noclegi Katowice | Wybór miejsca pobytu | `https://hornigold.pl/pl/` | Katalog kategorii pokoi, opis pobytu w Katowicach, odnośniki do kontaktu i dojazdu | Metadane zgodne z istniejącą treścią; ceny i parametry oferty nie zostały ponownie potwierdzone | Odbiór faktów operacyjnych przed otwarciem produkcji |
| hotel Katowice | Wybór obiektu określanego przez szukającego jako hotel | `/pl/` wyłącznie jako istniejąca strona noclegowa; fraza nie wdrożona | Są pokoje i apartamenty; brak dossier potwierdzającego uprawnienie do klasyfikacji jako hotel | WYŁĄCZONE z title/H1/meta/nowego tekstu; wcześniejszy zakaz właściciela pozostaje | Nie zmieniać klasyfikacji bez formalnego, datowanego potwierdzenia; nie tworzyć strony „hotel” |
| apartamenty Katowice | Wybór kategorii zakwaterowania | `https://hornigold.pl/pl/pokoje/` | Istniejące kategorie i zdjęcia wnętrz; porównywarka | Nazwa katalogu zgodna z treścią; wyposażenie, ceny i parametry wymagają dossier | Potwierdzić aktualne opisy kategorii; zachować jedną stronę katalogową |
| noclegi Katowice centrum | Wybór noclegu w centrum | `https://hornigold.pl/pl/` | Dotychczasowy H1 „Pokoje i apartamenty w centrum Katowic”; strona lokalizacji, Kopernika 6 | „Centrum” przejęte z istniejącej treści; rejestr potwierdza adres podmiotu, nie czas dojścia ani obszar marketingowy | Utrzymać spójność adresu; bez deklaracji minut/metrów |
| hotel Katowice centrum | Wybór hotelu w centrum | `/pl/` warunkowo, bez użycia klasyfikacji „hotel” | Jak wyżej; brak potwierdzenia statusu hotelowego | WYŁĄCZONE z optymalizacji dokładnej frazy | Formalne potwierdzenie kategorii obiektu; obecnie komunikować noclegi/pokoje/apartamenty |
| nocleg Katowice Spodek | Nocleg związany z wydarzeniem | `https://hornigold.pl/pl/pobyt/wydarzenie/` | Istniejące instrukcje planowania przyjazdu; przewodnik `/pl/katowice/wydarzenie/` z oficjalnymi odnośnikami Spodka, MCK i NOSPR | Nie twierdzimy, że obiekt jest „przy Spodku”, blisko ani w określonej odległości | Aktualność wydarzeń sprawdzać u organizatora; termin noclegu u recepcji |
| nocleg na wydarzenie Katowice | Planowanie pobytu przy okazji koncertu/kongresu | `https://hornigold.pl/pl/pobyt/wydarzenie/` | Sekcje o dojeździe, powrocie i uzgodnieniu późnego przyjazdu; formularz zapytania | Brak obietnicy dostępności, transportu, wejściówki lub pakietu | Potwierdzić indywidualne warunki; przewodnik organizacyjny pozostaje pod osobnym URL |
| nocleg służbowy Katowice | Planowanie podróży służbowej | `https://hornigold.pl/pl/pobyt/sluzbowo/` | Treść: pytania o warunki pracy, fakturę i godziny przyjazdu; przewodnik `/pl/katowice/sluzbowo/` | Pytania do uzgodnienia, nie zapewnienie usług/wyposażenia | Potwierdzić wymagania gościa z recepcją; nie dopisywać gwarantowanego biurka, Wi-Fi ani godzin |
| weekend w Katowicach | Plan miasta i pobytu | `https://hornigold.pl/pl/pobyt/weekend/` | Własny plan miasta, kategorie pokojów; przewodnik `/pl/katowice/weekend/` | Propozycja planowania, nie pakiet lub promocja | Przewodnik zachować jako informacyjny, stronę pobytu jako noclegową |

## Rozdzielenie stron i intencji

- `/pl/` przedstawia obiekt i przejścia do wyboru pokoju; `/pl/pokoje/` jest katalogiem kategorii; `/pl/pobyt/` jest planerem, nie wynikiem dostępności.
- `/pl/pobyt/wydarzenie/` dotyczy zapytania o pobyt, a `/pl/katowice/wydarzenie/` przygotowania do wizyty w Spodku, MCK lub NOSPR. Wzajemne linki łączą te potrzeby bez kopiowania treści i deklarowania odległości.
- `/pl/lokalizacja/` wskazuje istniejące materiały dojazdu i wejścia. `/pl/parking/` kieruje do uzgodnienia miejsca i warunków; nowych parametrów parkingu nie dodano do metadanych.
- Nie wciskamy fraz noclegowych do stron prawnych, ilustracji ani każdego opisu miasta. Ich cel pozostaje informacyjny/redakcyjny.

## Zakres dowodu

Źródło treści: checkout Sites, commit wejściowy `04af54414df7d0764786dbb4d771b95c16644a3e`. `legal/operator-verification.json` zawiera zapis rejestru pobrany 06.10.2026; nie potwierdza cen, usług, wyposażenia, telefonu ani klasyfikacji hotelowej. Pełny wykaz wszystkich 99 kanonicznych stron PL, kandydatów do potwierdzenia i linkowania zapisuje `scripts/audit_pl_intents.py` w `docs/seo/pl-intents-*.json`.
