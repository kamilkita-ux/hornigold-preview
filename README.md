# Hornigold — ujednolicona wersja 23 (wydanie 23.1)

Samodzielny podgląd WWW: 693 podstrony w siedmiu językach (polski, angielski, niemiecki, chiński uproszczony, ukraiński, hiszpański, włoski).

Główny adres po scaleniu: https://hornigold-przeglad-beata.ai-bd6d706867.chatgpt.site/pl/

GitHub jest repozytorium źródeł. Push i przekierowanie Pages do Sites są odłożone decyzją właściciela. Nie opisuj lokalnych zmian jako opublikowanych na GitHubie.

## Zakres

To wersja do przeglądu. Nie zastępuje hornigold.pl. Rezerwacje, płatności i integracja PMS są wyłączone. Formularze przygotowują zapytania do samodzielnego wysłania — nie tworzą rezerwacji. Dokumenty dotyczą aktualnego serwisu informacyjnego i zapytań do recepcji. Nie stanowią regulaminu aktywnej sprzedaży z niepodłączonego PMS/Fiserv; wymagają niezależnego odbioru prawnego. `noindex` ogranicza indeksowanie, ale nie jest kontrolą dostępu: ten podgląd i repozytorium są publiczne.

Sites obsługuje istniejący Worker i bazę D1 z wersji 18: zbiorczy licznik odsłon, przekierowania HTTP 301, ochronne nagłówki i lokalizowane błędy 404. Licznik zapisuje wyłącznie sumę oraz datę rozpoczęcia; nie jest pomiarem unikalnych gości, sprzedaży ani reklam. Stara suma jest zachowywana przez tę samą bazę, bez zerowania. Sam GitHub Pages nie wykonuje tego serwera. Nie uruchomiono GA ani reklam.

## Katalogi

- `site/` — kompletne pliki HTML, CSS, JavaScript i obrazy strony, bez prywatnych dokumentów, korespondencji i historii projektu.
- `scripts/build.py` — dostosowanie wszystkich lokalnych adresów do katalogu GitHub Pages oraz kontrola linków i trybu podglądu.
- `server/` — przeniesiony serwer wersji 18 i pełna mapa dawnych adresów. Niezmieniona historia migracji D1 jest w `drizzle/`.
- `content/club.json` — aktualne teksty sekcji Club Hornigold; warunki korzyści potwierdza recepcja.
- `routes.json` — 693 właściwe adresy podstron; dodatkowe strony przekierowujące zachowują dawne adresy językowe.
- `.github/workflows/pages.yml` — publikacja po zmianie gałęzi `main` lub uruchomieniu ręcznym.

Na Sites dawne adresy otrzymują HTTP 301. W statycznej kopii działają odpowiedniki przekierowujące w przeglądarce. Parametry pobytu i kampanii oraz kotwice są zachowywane. Canonical wskazuje docelową domenę Hornigold; podgląd pozostaje nieindeksowany.

## Uruchomienie

Wymagany Python 3.10 lub nowszy:

```sh
python -m pip install -r requirements.txt
python scripts/build.py --base /
python -m http.server 8080 --bind 127.0.0.1 --directory _site
```

Następnie otwórz http://127.0.0.1:8080/pl/.

Dla GitHub Pages: `python scripts/build.py --base /hornigold-preview/`. Publikowany jest wyłącznie `_site/`, a nie cały katalog repozytorium. Stronę można przenieść na inny hosting statyczny, budując ją z `--base /`.

## Ograniczenia uruchomienia docelowego

Publikacja tego podglądu nie jest zgodą na uruchomienie sprzedaży. Przed podmianą hornigold.pl wymagane są zatwierdzone dokumenty i fakty, potwierdzenie praw do materiałów, sprawdzona rezerwacja/płatność/potwierdzenia we wszystkich językach oraz odbiór domeny, analityki i kopii bezpieczeństwa. Nie dodawaj CNAME ani nie zmieniaj DNS na podstawie tego repozytorium.

Materiały wizualne zachowują dotychczasowe oznaczenia i prawa ich właścicieli. Publiczna dostępność repozytorium nie oznacza udzielenia licencji na dowolne wykorzystanie zdjęć i marki.

## Aktualizacja, kontrola i wycofanie

Edytowalnym źródłem tej niezależnej strony jest `site/`: pełny HTML, CSS, JavaScript i zasoby. Nie potrzeba prywatnego generatora ani oryginalnego komputera. Edycję wspólnego elementu trzeba zastosować do wszystkich odpowiednich podstron; CMS dla obsługi nie jest wdrożony.

Aktualizacja: sklonuj repozytorium, utwórz gałąź, zmień źródła i `release.json`, zbuduj oba warianty, uruchom `scripts/audit_static.py` i `scripts/check_repository.py`, wykonaj testy przeglądarkowe. Przegląd zmian poprzedza push do `main`, który publikuje Pages. Sprawdź udany GitHub Actions run, a następnie publiczne `release.json` i stronę; sam push nie potwierdza publikacji.

Testy przeglądarkowe: `pnpm install --frozen-lockfile`, `pnpm exec playwright install`, lokalny serwer `_site/`, następnie `AUDIT_URL=http://127.0.0.1:4329/ node scripts/browser_audit.cjs`. Skrypt używa odizolowanych przeglądarek Chromium, Firefox i WebKit. WebKit nie zastępuje ręcznego testu wydanej aplikacji Safari.

Kopia kodu: `git clone --mirror` do bezpiecznego katalogu poza publicznym repozytorium, osobno archiwum `_site/` z sumami kontrolnymi. Kopie danych PMS/płatności dopiero po wdrożeniu backendu, szyfrowane i poza GitHubem. Nie commitować `.env`, logów gości, baz ani kopii.

Wycofanie kodu: utwórz commit odwracający wadliwą zmianę (`git revert`), sprawdź build i wypchnij go do `main`; zweryfikuj udane wdrożenie i ponownie odczytaj publiczną stronę. Nie używaj force push. Odtworzenie danych rezerwacji wymaga osobnej procedury.

Wersja 22 usuwa widoczne oznaczenia testowe na polecenie właściciela; nie usuwa noindex i nie włącza rezerwacji. Brak banera nie jest deklaracją gotowości do produkcji.

## Przekazanie i integracje

- [PMS i Fiserv — projekt integracji](docs/PMS-FISERV.md)
- [Pytania do dostawców](docs/PYTANIA-DO-DOSTAWCOW.md) — przygotowane, niewysłane.
- [Domena i odbiór dla Marka](docs/DOMENA-I-ODBIOR.md) — DNS wymaga danych konkretnego hostingu.
- `render.yaml` — przygotowana alternatywa dla frontendu, jeszcze niewdrożona. GitHub Pages nie jest docelowym hostingiem sprzedaży online.


## Dokumenty i testy wersji 23

Źródłem dokumentów jest `legal/{język}.json`. Pliki HTML generuje `python scripts/build_legal.py`. Nie edytuj wyłącznie jednego przetłumaczonego HTML: wszystkie siedem wersji musi zachować ten sam zakres. Dane rejestrowe i źródło weryfikacji są w `legal/operator-verification.json`.

Aby odtworzyć PDF-y: zainstaluj `requirements-documents.txt`, uruchom `python scripts/build_legal_pdf.py`. Czcionki i licencje znajdują się w `legal/fonts/`; generator nie potrzebuje plików z oryginalnego komputera. Pliki trafiają do `site/documents/` i `../output/pdf/`. Po zmianie treści zawsze wyrenderuj i obejrzyj PDF-y; nie deklaruj zgodności PDF/UA bez walidacji. Ta sama treść jest dostępna w HTML.

`scripts/audit_accessibility.cjs` skanuje wszystkie trasy w szerokościach 375 i 1366 pikseli narzędziem axe. `scripts/audit_privacy.cjs` testuje dialog, klawiaturę, odmowę, zgodę, wycofanie i wygaśnięcie w siedmiu językach oraz trzech silnikach przeglądarek. Żądania map w tym teście są przechwytywane i obsługiwane lokalną odpowiedzią: to test bramki zgody, nie audyt działania Google. Ustaw `AUDIT_URL` na lokalny serwer z odpowiednim prefiksem. Serwer testowy powinien obsłużyć równoległe pobieranie zasobów.

Wersja 23 dodaje dokumenty do obecnych funkcji informacyjnych i zapytań do recepcji. Wydanie 23.1 łączy je z funkcjami serwerowymi wersji 18 i przywraca pełną sekcję Club Hornigold na polecenie właściciela. Nie uruchamia rezerwacji, płatności, analityki ani marketingu. Zewnętrzne mapy wymagają świadomej zgody. Testy automatyczne i przygotowanie treści nie są niezależną opinią prawną ani certyfikatem pełnej zgodności UE/WCAG. Otwarte sprawy operacyjne i prawne są zapisane w `docs/AUDYT-UE-23.json`.

## Scalanie 18 → 23.1 i publikacja Sites

Jedno źródło: to repozytorium. Nie rozwijaj równolegle starego `hornigold-review-site`. `docs/V18-ASSET-MANIFEST.json` oraz `docs/CONSOLIDATION-23.json` dokumentują zachowanie stron i grafik. Kopie pełnej historii sprzed scalenia są poza repozytorium, na Macu mini. Przed publikacją wykonaj kolejną kopię i sprawdź SHA-256 zgodnie z AGENTS.md.

W celu publikacji istniejącego Sites: najpierw odczytaj projekt `appgprj_6ac24ff4d7d08191aef99366bb3d966f` na koncie właściciela, pobierz krótkotrwały dostęp do źródeł i otwórz osobny checkout helperem Sites. Przenieś do niego komplet aktualnych źródeł tego repozytorium, zachowując `.openai/hosting.json` i powiązanie `d1: DB`. Nie dodawaj sekretów, baz ani node_modules. Zbuduj `python3 scripts/build.py --base / --counter` oraz `node scripts/build_sites.mjs`. Pakowanie, commit/push do źródeł Sites i publikację wykonuj helperem i natywnymi narzędziami Sites. Numer wersji hostingu może być inny niż numer wydania strony.

Testy: `node --test tests/server.test.mjs` (Node z node:sqlite), następnie `node scripts/serve_worker.mjs` uruchamia lokalny adapter tego samego Workera i nietrwałą bazę testową. Ustaw AUDIT_URL=http://127.0.0.1:4334 dla audytów przeglądarek. Testy lokalne nie zwiększają licznika produkcyjnego.

`scripts/build_pages_redirect.py` przygotowuje `_pages/` z przekierowaniami wszystkich adresów GitHub Pages do Sites, zachowując daty, gości, kategorię i kotwicę. Nowy workflow opublikuje je dopiero po przyszłym zatwierdzonym pushu na GitHuba. Pełne źródła strony nadal zostają w repozytorium. Nie usuwać repozytorium ani historii, aby je „wyczyścić”.

Przywrócenie starego projektu Sites jest możliwe przez jego historię wersji. Nie kasuj całego projektu: usunęłoby to właściwy adres i zagroziło danym licznika.
