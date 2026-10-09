# Rezerwacje przez KWHotel / GuestSage — wersja minimalna (przekazanie linkiem)

Data: 2026-10-09. Autor: CloudMentor (Marek + Claude). Status: projekt zaakceptowany przez Marka, do wdrożenia na `deploy/cloudflare`.

## Cel

Gość na hornigold.pl wybiera termin i liczbę osób, a rezerwację i płatność kończy w hostowanym silniku hotelu **GuestSage AI Booking Engine** (KWHotel). Silnik jest skonfigurowany (pokoje, ceny, płatności, regulamin hotelu), zarząd zgodził się na sprzedaż online — potwierdzenie Marka z 9.10.2026.

Kryterium sukcesu: na każdej z 7 podstron `rezerwacja/` działa przycisk prowadzący do GuestSage z wybranymi datami i liczbą osób w języku strony; bez dat — do strony głównej silnika; nic nie osłabia polityki bezpieczeństwa strony.

## Ustalenia

- Wariant C: minimalna wersja teraz (CloudMentor, gałąź `deploy/cloudflare`), pełna integracja u Kamila według tej specyfikacji. Kamil ma nadać kontu GitHub `CloudDev-M` prawo zapisu w `kamilkita-ux/hornigold-preview`.
- Wariant 1: przekazanie linkiem. Odrzucone: widget `booking-bar-widget` z `implementacja.kwhotel.com` (325 KB React, interfejs po polsku, wymaga poluzowania CSP `script-src`/`style-src`/`connect-src`), silnik w iframe (płatność w ramce, blokady ciasteczek zewnętrznych).
- Bez identyfikatorów pokoi na start (`featuredRoomTypeId` dopisywany później).

## Źródła

Materiały od hotelu leżą lokalnie w `kwhotel/` (poza repozytorium — repo jest publiczne, a PDF zawiera dane kontaktowe pracowników dostawcy).

- `kwhotel/AI-Booking-Engine-samodzielna-implementacja.pdf` (KWHotel, 14.04.2025): adres `https://be.guestsage.com/{lang}/{HASH}`, wariant z parametrami `…/{HASH}/offers?arrivalDate=YYYY-MM-DD&departureDate=YYYY-MM-DD&personsCount=N[&featuredRoomTypeId=ID][&featuredRatePlanId=ID][&ageCategoryCounts=[…]]`. Przy parametrach wymagane są co najmniej obie daty i liczba osób.
- `kwhotel/url.txt`: `https://be.guestsage.com/pl/c98ead00-c7fd-4013-bb45-f19539b932d4`.
- Bundle silnika (`be.guestsage.com/assets/index-*.js`, odczyt 9.10.2026): obsługiwane języki `en, pl, de, fr, el, ru, it, es, uk, lv, no, nb, pt, cs, sk, fi, bg`, domyślny `en`. Brak chińskiego.

## Zachowanie

1. Wybór pobytu bez zmian: `HornigoldStay` w `site/assets/app.js` (`sessionStorage['hornigold-stay']`, pola `arrival`, `departure`, `guests` 1–6, `room`; walidacja w `clean()`).
2. Na podstronach `site/{pl,en,de,uk,es,it,zh-hans}/rezerwacja/index.html` blok `.notice` „Rezerwacje online są obecnie niedostępne” zostaje zastąpiony blokiem rezerwacji:
   - nagłówek „Zarezerwuj online” (w języku strony),
   - zdanie: dostępność, cenę i warunki zobaczysz, a rezerwację i płatność zakończysz w systemie rezerwacyjnym hotelu (KWHotel / GuestSage); tam zawierasz umowę na warunkach hotelu,
   - przycisk `<a class="button" data-booking href="https://be.guestsage.com/{lang}/c98ead00-c7fd-4013-bb45-f19539b932d4">` „Sprawdź dostępność i zarezerwuj”, ta sama karta,
   - linki „Zmień pobyt” / „Wróć do pokojów” bez zmian.
   Akapit `.integration-limit` dostosowany: język silnika — w chińskiej wersji silnik otwiera się po angielsku.
3. `site/assets/booking.js` (nowy, dołączony tylko na podstronach `rezerwacja/`):
   - stałe: `HOTEL = "c98ead00-c7fd-4013-bb45-f19539b932d4"`, `ORIGIN = "https://be.guestsage.com"`, `LANG = {pl:"pl", en:"en", de:"de", uk:"uk", es:"es", it:"it", "zh-hans":"en"}`, `ROOMS = {}` (slug → `featuredRoomTypeId`, puste),
   - `bookingUrl(stay, pageLang)`: gdy `arrival` i `departure` są poprawne (ta sama walidacja co `HornigoldStay`) i `guests` ≥ 1 → `/{lang}/{HOTEL}/offers?arrivalDate=…&departureDate=…&personsCount=…` (+ `featuredRoomTypeId`, jeśli `ROOMS[stay.room]`); w przeciwnym razie `/{lang}/{HOTEL}`; język nieznany → `en`,
   - podstawia `href` wszystkich `a[data-booking]` przy załadowaniu i przy każdej zmianie wyboru pobytu (zdarzenia `input`/`change` pól `arrival`/`departure`/`people` formularza zapytania na tej samej stronie, które już aktualizują `HornigoldStay`),
   - bez nowych napisów w JS (żadnych wpisów w `site/assets/messages/*.js`), bez ciasteczek i bez zapisu poza istniejącym `sessionStorage`.
4. Tekst `.form-help` przy formularzach `form[data-search]` (strony główne i `pobyt/` w 7 językach) — zamiast „Rezerwacje online są obecnie niedostępne…”: rezerwację i płatność zakończysz w systemie rezerwacyjnym hotelu. Element zostaje (wymaga go `scripts/audit_static.py:35`).
5. Formularz zapytania mailowego (`.enquiry-form`) bez zmian — alternatywa dla grup i firm.

## Poza zakresem (etap Kamila)

- Teksty prawne w 7 językach (`legal/*.json`, `build_legal.py`): sekcja sprzedaży online (dziś „w przygotowaniu”), polityka prywatności — GuestSage/KWHotel jako odbiorca danych po przejściu do silnika.
- `seo/discovery-content.json` → `site/llms/*.txt` (dziś: rezerwacje niedostępne).
- `release.json` `bookingEnabled` i audyty, które go wymuszają (`audit_online_sales.py`, `audit_pad_content.py`, `audit_seo.py`, `prepare_cloudflare_production.py`, `tests/production-indexing.test.mjs`) — flaga dotyczy projektu własnego koszyka i płatności na stronie; ustalić nowe znaczenie (np. osobne pole dla zewnętrznego silnika).
- `docs/ONLINE_SALES_LAUNCH_GATES.md`, `PAD_*`, `PMS-FISERV.md` — hostowany silnik zastępuje własny checkout + Fiserv.
- Mapowanie pokoi (`featuredRoomTypeId`) i kategorii wiekowych dzieci (`ageCategoryCounts`) z panelu KWHotel; rozdział dorośli/dzieci w wyborze pobytu.

## Ryzyka

- Do czasu etapu Kamila regulamin i polityka prywatności strony opisują sprzedaż online jako przygotowywaną. Zaakceptowane przez Marka 9.10.2026; zdanie przy przycisku wskazuje, że umowa jest zawierana w systemie hotelu.
- `release.json` nadal ma `bookingEnabled: false` (znaczenie: brak sprzedaży na samej stronie).
- Chińska wersja strony prowadzi do angielskiej wersji silnika.
- Zmiana adresu silnika lub identyfikatora hotelu wymaga edycji jednej stałej w `booking.js` i atrybutów `href` na 7 podstronach.

## Testy i odbiór

- `tests/booking.test.mjs` (node:test): daty poprawne → adres `offers` z trzema parametrami; brak lub błąd dat → adres strony głównej silnika; `zh-hans` → `en`; `ROOMS` z wpisem → `featuredRoomTypeId`; przyjazd w przeszłości → adres bez parametrów.
- Build produkcyjny i audyty Kamila jak w `docs/CLOUDFLARE.md` („Produkcja z indeksowaniem”) oraz `node --test tests/server.test.mjs tests/production-indexing.test.mjs tests/booking.test.mjs` — wszystkie zielone.
- Po wdrożeniu: 7 podstron `rezerwacja/` zwraca 200, zawiera `a[data-booking]` z `be.guestsage.com/{lang}/c98ead00-…`; `booking.js` 200; nagłówek CSP bez zmian; adres z parametrami otwiera się w GuestSage (ręczna próba w przeglądarce).
