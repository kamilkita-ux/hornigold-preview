# Hornigold — audyt kodu, bezpieczeństwa i spójności

Data: 11 października 2026. Zakres: aktualny checkout `hornigold-ai-discovery`, commit bazowy c239af6, publiczna domena https://hornigold.pl oraz lokalne artefakty siedmiu języków. Audyt nie wykonuje płatności, rezerwacji, ataków obciążeniowych, obchodzenia WAF ani zmian kont i uprawnień.

## Wynik wykonawczy

W publicznej kontroli wszystkich 693 tras nie wykryto błędów badanych reguł bezpieczeństwa i spójności. Nie oznacza to braku wszystkich możliwych podatności ani certyfikacji zgodności prawnej. Jeden potwierdzony błąd kodu obsługi odpowiedzi awaryjnych naprawiono lokalnie. Jedno umiarkowane ostrzeżenie zależności deweloperskiej pozostaje. Konfiguracja infrastruktury, umowy dostawców oraz transakcje PMS/płatności wymagają osobnego potwierdzenia.

## Ustalenia według priorytetu

### SEC-01 — umiarkowane: zależność deweloperska esbuild

Dowód: `pnpm-lock.yaml`, aktualny raport `output/security-audit-2026-10-11/dependencies.json`. Audyt zależności: 0 krytycznych, 0 wysokich, 1 umiarkowane. Ostrzeżenie dotyczy możliwości odczytu odpowiedzi serwera deweloperskiego przez obcą stronę; zależność jest pośrednia w narzędziach deweloperskich, a nie importowana przez produkcyjny Worker. Nie udostępniać tego serwera; użyty lokalny serwer QA to Python związany wyłącznie z 127.0.0.1. Nie wymuszono niezgodnej aktualizacji pośredniej zależności. Właściciel: utrzymanie kodu; następny krok: zgodna aktualizacja dostawcy drizzle-kit i ponowny audyt.

### SEC-02 — niski, naprawione lokalnie: różne nagłówki odpowiedzi błędów

Dowód: `server/worker.mjs:35` i `server/worker.mjs:42`. Odrzucone żądania licznika 403 i awaria 503 pomijały wspólną funkcję nakładającą politykę bezpieczeństwa. Naprawa kieruje je przez `headersFor`, zachowując status, treść i zakaz cache. Test w `tests/server.test.mjs` sprawdza obie ścieżki i CSP, nosniff, DENY, no-referrer oraz no-store. 46/46 testów Node zaliczonych. Ta zmiana nie została opublikowana w ramach tego audytu.

### SEC-03 — niski / infrastruktura do potwierdzenia: nadużycia licznika

Dowód: `server/worker.mjs:34-38`, `server/counter.mjs:5-8`. Walidacja Origin i własnego nagłówka ogranicza żądania obcych stron w przeglądarce, ale nie uwierzytelnia klientów spoza przeglądarki. Kod nie zawiera limitowania częstotliwości. Nie stwierdzono konfiguracji limitów Cloudflare, ponieważ nie ma dostępu do właściwego projektu. Wskaźnik jest liczbą odsłon, nie unikalnych osób. Następny krok: potwierdzić reguły WAF/rate limiting i budżet D1 z operatorem; nie dodawać zbierania IP ani danych gości bez oceny prywatności. Nie wykonywano prób masowego naliczania na produkcji.

### OPS-01 — różnica źródeł wymagająca zachowania

Produkcja zgłasza wersję 23.11, commit 0ade4c9db17206a1a371864cd2222bbe29c14d4d. Aktualny checkout ma bazę c239af6. Sześć sprawdzonych skryptów produkcyjnych odpowiada źródłom bajt w bajt. CSS produkcji zawiera dodatkowy styl `.booking-panel` od CloudMentor; publiczny `assets/booking.js` obsługuje GuestSage i nie należy do tego checkoutu. Nie nadpisano tych rozszerzeń. Przed kolejnym wdrożeniem trzeba scalić je w rzeczywistym repozytorium produkcyjnym i potwierdzić pipeline. Numer wersji sam w sobie nie dowodzi identyczności wszystkich plików.

## Kontrole wykonane

- Wszystkie 693 publiczne trasy: HTTP 200, jeden H1, canonical dokładny, 8 hreflang, 7 odnośników języka, footer i kontakt, poprawny JSON-LD, brak inline handlerów i javascript URL, brak mixed content, alt obrazów, jawne zabezpieczenia nowych okien, CSP/anti-framing/nosniff/referrer. 0 błędów, 0 ostrzeżeń, brak duplikatów title. Każdy język ma 99 tras.
- Lokalne audyty SEO: preview 693 trasy, 1242 HTML, 75106 linków; production-ready 693 trasy, 1242 HTML, 76499 linków; po 2604 obrazy, wszystkie trasy osiągalne, 539 aliasów, 0 błędów i ostrzeżeń.
- Build preview: 693 strony, 0 błędów; blokady indeksacji preview zachowane.
- Testy Node 46/46; Python SEO 10/10; sprawdzenie składni 21 JS/MJS i 30 Python: 0 błędów.
- Heurystyczny skan 1539 śledzonych plików tekstowych: 0 znalezionych wzorców sekretów; nie stanowi pełnego skanu wszystkich historycznych commitów, prywatnych katalogów ani usług zewnętrznych.
- Produkcja, anonimowa pierwsza wizyta: 14 przypadków (7 języków × telefon/komputer), 0 błędów, brak zewnętrznych żądań i cookies przed zgodą. Zewnętrzne żądania blokowane podczas testu; nie zgłaszamy rzeczywistego odbioru GA4.
- Produkcyjne robots/sitemap/API/404: poprawne statusy; nieistniejąca podstrona 404 i noindex, API noindex. Brak CSP na robots.txt nie jest podatnością dokumentu HTML.
- Kopia na Mac mini: `/Users/kamilkita/Documents/Hornigold-backups/2026-10-11_223820-release23`, 1947 plików, ponowny odczyt hashy i Git bundle potwierdzony.

Pełna kontrola 693 tras × 2 widoki: 1386/1386 przypadków działania JavaScript i układu bez błędów; 1386/1386 automatycznych kontroli axe bez naruszeń badanych reguł po powtórzeniu 85 przypadków na stabilnym serwerze QA. Pierwszy przebieg przeciążył kolejkę połączeń lokalnego serwera; pierwotne błędy i wyniki powtórek zachowano, zamiast usuwać dowody. Nie stanowi to ręcznej certyfikacji WCAG. Dowody znajdują się poza publicznym katalogiem strony w `output/security-audit-2026-10-11/`.

## Przegląd kodu

Sprawdzono obsługę wejść URL/storage, dat i liczby gości, DOM, formularzy mailowych, zewnętrznych iframe, zgód, analityki, języków, przekierowań i licznika. Badane skrypty używają textContent/value i kontrolowanych URL zamiast wstawiania nieufnego HTML; zapytania SQL licznika są parametryzowane. Mapy dopuszczają określony host i ścieżkę osadzania. Analityka działa tylko na produkcyjnym origin i po osobnej zgodzie; nie przekazuje dowolnych parametrów URL. Dane swobodne zapytań nie są zapisywane w pamięci przeglądarki przez badany kod. To przegląd zakresu obecnej strony, nie przyszłego systemu płatności.

## Poza zakresem / blokery odbioru

Brak dostępu do właściwego projektu Cloudflare uniemożliwia potwierdzenie WAF, rate limiting, alertów kosztowych, bindingów, uprawnień kont i przywracania produkcyjnej D1. Brak kompletu dowodów PMS/GuestSage/Fiserv uniemożliwia odbiór transakcji, webhooków, idempotencji, anulowań, zwrotów i potwierdzeń. Nie wykonywano testów obciążeniowych, aktywnego pentestu, manualnego odbioru wszystkich języków, czytników ekranu ani PDF/UA. Dokumenty prawne i procedury operacyjne wymagają właściwego odbioru biznesowego/prawnego.

## Źródła metodyki

- MDN CSP: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy
- OWASP DOM XSS: https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html

Przegląd i poprawki w tym zadaniu są lokalne. Nie wykonano push, deploy, zmiany DNS, aktywacji płatności ani rezerwacji.
