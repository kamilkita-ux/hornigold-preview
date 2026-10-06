# Audyt scalenia Hornigold 18 → 23.1

Data: 6 października 2026. Numer wydania strony: 23, rewizja 23.1. Jedno źródło dalszego rozwoju: to repozytorium. Historia v18 pozostaje kopią odzyskiwania, a nie osobno rozwijaną stroną.

## Zakres i zachowanie pracy

- Zachowano wszystkie 702 ścieżki HTML z v18 (693 właściwe podstrony oraz strony wejściowe/błędy), wszystkie 360 ścieżek grafik oraz wszystkie siedem języków. Dwa pliki identyfikacji graficznej mają nowszą zawartość: favicon i grafika udostępniania; stare bajty są w kopii historii.
- Z v18 przeniesiono serwer, zbiorczy licznik D1, mapę przekierowań, zabezpieczające nagłówki HTTP, lokalizowane błędy 404, llms.txt i mapę witryny. Sitemap odtworzono dla wszystkich 693 aktualnych tras (stara zawierała 616).
- Zachowano nowsze treści, operatora, kontakt office@hornigold.pl, terminologię, dostępność i zgodę na mapy z v23. Nie przywracano dawnych błędów ani banerów testowych.
- Club Hornigold przywrócono na wyraźną prośbę właściciela: cztery obszary korzyści, kontakt i dalsze planowanie pobytu we wszystkich językach. Konkretne warunki wymagają potwierdzenia przez recepcję; strona nie tworzy fikcyjnego członkostwa ani rabatu. Oryginalne robocze sformułowania są w archiwum redakcyjnym.
- Dokumenty HTML i siedem sześciostronicowych PDF-ów opisują teraz oba hostingi i zbiorczy licznik. PDF-y wyrenderowano i obejrzano. Brak certyfikacji PDF/UA i niezależnego odbioru tłumaczy/prawnika pozostaje jawny.

## Wyniki

- Testy serwera: 6 grup bez błędów; m.in. 80 równoległych zapisów, zachowanie istniejącej sumy po ponownym otwarciu bazy, odrzucanie obcego pochodzenia, wszystkie stare przekierowania z datami/gośćmi, 404 w siedmiu językach i nagłówki ochronne.
- Automatyczna dostępność: 1386 kontroli (693 × 375/1366 px), brak wykrytych błędów. Po kosmetycznym przeniesieniu linku Club w stopce przeprowadzono dodatkową próbę wspólnych elementów; 28 dodatkowych kontroli bez błędów; wynik w SHARED-UI-23-1.json.
- Przeglądarki Chromium, Firefox i WebKit: 819 przypadków bez błędów; 7 języków i trzy szerokości.
- Zgody/mapy/PDF: 42 przypadki bez błędów. Ruch do Google w testach był przechwytywany, więc wynik potwierdza bramkę zgody, nie działanie usług Google.
- Formularze, 320 px, 200% tekstu, ograniczenie animacji, JavaScript włączony/wyłączony: 63 przypadki bez błędów.
- Club i licznik: 42 przypadki bez błędów, w tym brak podwójnego naliczania przy zmianie widoczności i brak fikcyjnej liczby przy awarii. Licznik w tych testach był symulowany; trwałość rzeczywistego schematu sprawdzono osobno w testach serwera.
- Mapa zawartości: CONSOLIDATION-23.json; pełna kontrola odnośników i kotwic dla obu baz adresów w raportach statycznych.

## Publikacja i ograniczenia

Opublikowano na istniejącym publicznym Sites; status wdrożenia succeeded. Publiczna przeglądarka potwierdziła wydanie 23.1, brak banera, licznik 124 po pierwszym otwarciu, Club w siedmiu językach oraz pobranie polskiego PDF zgodnego z plikiem źródłowym. Dowód: PUBLICATION-23-1.json. Zachowano projekt i bazę. Przed aktualizacją odczyt bazy wykazał 122 odsłony od 5 października 2026. Odczyty kontrolne strony mogą zwiększać tę sumę; nie są to unikalne osoby. Rzeczywisty wynik wdrożenia i późniejszego odczytu należy sprawdzić w protokole publikacji, a nie w samym lokalnym buildzie.

Push GitHub i przekierowanie GitHub Pages są odłożone przez właściciela. Kod przekierowania jest przygotowany lokalnie; nie usunięto repozytorium ani historii. Nie podmieniono hornigold.pl. Rezerwacje, płatności, Google Analytics i reklamy nie zostały uruchomione.

Automatyczne kontrole nie są certyfikatem całkowitej zgodności UE, WCAG, kompletności redakcyjnej ani testem realnej rezerwacji. Zewnętrzne mapy, niezależny odbiór języków, prawo/operacje recepcji, PMS/Fiserv i testy z rzeczywistymi użytkownikami pozostają odrębnymi zadaniami.

## Kopie

Przed pracą wykonano kopie historii obu repozytoriów na Macu mini w Documents/Hornigold-backups/2026-10-06-before-consolidation. Zgodność SHA-256 potwierdzono ponownym odczytem. Skrypt scripts/backup_release.py zapisuje dodatkowo kompletny bieżący kod (także niezatwierdzone zmiany) wraz z historią Git i sprawdza każdy plik w archiwum. Kopia na tym samym Macu nie stanowi niezależnej kopii poza urządzeniem.
