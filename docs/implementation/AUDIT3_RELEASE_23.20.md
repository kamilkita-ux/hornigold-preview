# Wydanie 23.20 — audyt 3

Baza: origin/main 3b50e52 z integracją Marka. Przygotowanie: codex/audit3-release-20261013. GitHub Pages: main. Cloudflare: deploy/cloudflare, Worker hornigold, konto ee23b9132a9692ab6c0e9f22aa86dda8. CLI lokalnie nie uwierzytelnione; nie zmieniono DNS, uprawnień, wiązań ani bramki.

Zmiany: serwerowe 301 root do /pl/ z parametrami; 7 starych adresów PL do odpowiednich podstron; produkcyjny strict-origin-when-cross-origin przy zachowanym no-referrer chronionego przekierowania rezerwacji; usunięcie _ga* także bez ważnej zgody na wejściu; 224 ilustracje i 7 wejść procesu rezerwacji poza indeksem/sitemap/hreflang produkcji, galerie zachowane; 462 indeksowalne URL z lastmod ze źródłowych commitów, nie z zegara buildu; zatwierdzone sameAs; favicon.ico i manifest z ikonami 192/512; dokumenty HTML/PDF w 7 językach, wersja 2026-10-13, opis rzeczywistego zewnętrznego handoffu bez potwierdzania nieprzetestowanej płatności.

Ochrona: booking.js, style.css, wrangler.jsonc i skrypt odtwarzania paneli identyczne z upstream; 21 paneli rezerwacji bez zmian. Pełny pakiet produkcyjny budowany z aktywnym dotychczasowym licznikiem (--counter --production-counter). Nie uruchamiać migracji D1 ani inicjalizacji licznika.

Ograniczenia: brak pełnej listy starych EN/DE/obrazów/PDF — istniejące 539 aliasów zachowane; brak potwierdzonej bieżącej oceny Norton; bez fałszywych cen/ocen/usług i bez zmiany taryf; nie wykonano płatności ani rezerwacji. Czytnik ekranu, PDF/UA, własny backend formularza i rzeczywiste warunki operatora pozostają do osobnego odbioru. Zewnętrznych profili nie zmieniano.

Źródła prawne sprawdzone 13.10.2026: https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/prawo-do-informacji/ oraz https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/wylaczenia-prawa-do-odstapienia/. Informacja w dokumentach nie stanowi certyfikacji całego checkoutu.

Dowody: evidence/audit3-*.json oraz raporty testów. Status publikacji zostaje potwierdzony oddzielnym publicznym odczytem.
