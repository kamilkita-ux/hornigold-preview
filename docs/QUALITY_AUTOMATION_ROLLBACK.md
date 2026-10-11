# Kontrole Hornigold — punkt powrotu 11.10.2026

Bazowy commit: `ad8224ee0285496ec1114fef30b2c440ba881b1e`. Pełny bundle poza repozytorium: outputs/hornigold-before-controls-2026-10-11.bundle w czacie konfiguracji GitHub; zweryfikowano git bundle verify i SHA-256. Kopia Mac mini NOT VERIFIED.

Nowe pliki: .github/dependabot.yml i workflows quality.yml, post-publication.yml, report-failure.yml. Istniejący pages.yml pozostaje zachowany. Wycofanie: wyłączyć trzy nowe workflow, cofnąć commit dodający te pliki przez git revert, usunąć utworzoną automatyzację Codexa, odtworzyć osobno zapisane ustawienia wymaganych kontroli. Bez force push i bez resetowania bieżącej pracy Marka.

Kontrola publikacji obejmuje GitHub Pages. Nie certyfikuje hornigold.pl ani Sites; podpięcie rzeczywistego wdrożenia Cloudflare wymaga weryfikacji pipeline. Testy nie wykonują rezerwacji ani płatności. Pełny audyt raz w tygodniu, kontrola PR oraz po publikacji. Powtarzające się błędy aktualizują jedno otwarte zgłoszenie. Wymagana osobna weryfikacja skanowania sekretów/CodeQL i ustawienie wymaganej kontroli quality na głównej gałęzi.

Automatyzacja lokalnego Codexa hornigold-raporty-kontroli-do-codexa: PAUSED na polecenie właściciela; bez sprawdzania godzinowego. Kontrole GitHub i raporty mają reagować na PR/aktualizację i zakończenie publikacji. Samo utworzenie issue nie uruchamia automatycznie lokalnego czatu Codexa; połączenie zdarzeniowe do Codexa pozostaje NOT IMPLEMENTED. Nie włączaj ponownie harmonogramu godzinowego. Zakres dostępu integracji przed zmianą: travel-platform, ffp-inwestor, e-wza-platform. Dodano hornigold-preview. Wycofując dostęp usuń tylko to czwarte repo, jeżeli żadne inne prace nie wymagają go już.
