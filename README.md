# Hornigold — ujednolicona wersja 23 (wydanie 23.1)

Samodzielny podgląd WWW: 693 podstrony w siedmiu językach (polski, angielski, niemiecki, chiński uproszczony, ukraiński, hiszpański, włoski).

Pełna strona z tego repozytorium: https://kamilkita-ux.github.io/hornigold-preview/pl/

Osobna opublikowana kopia Sites: https://hornigold-przeglad-beata.ai-bd6d706867.chatgpt.site/pl/

GitHub zawiera komplet źródeł scalonej wersji 23.1. Zgodnie z doprecyzowaniem właściciela z 6 października 2026 GitHub Pages publikuje wszystkie podstrony, grafiki i dokumenty bez przekierowania do Sites. Historia poprzednich wersji pozostaje zachowana. Domena `hornigold.pl` nie została podłączona ani zmieniona.

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

Dla GitHub Pages: `python scripts/build.py --base /hornigold-preview/`. Wynik `_site/` zawiera pełną, przenośną stronę. Workflow publikuje cały `_site/`. Bazową ścieżkę pobiera z konfiguracji Pages, więc obsługuje katalog projektu i wariant głównego katalogu domeny. Stronę można przenieść na inny hosting statyczny, budując ją z `--base /`.

## Ograniczenia uruchomienia docelowego

Publikacja tego podglądu nie jest zgodą na uruchomienie sprzedaży. Przed podmianą hornigold.pl wymagane są zatwierdzone dokumenty i fakty, potwierdzenie praw do materiałów, sprawdzona rezerwacja/płatność/potwierdzenia we wszystkich językach oraz odbiór domeny, analityki i kopii bezpieczeństwa. Nie dodawaj CNAME ani nie zmieniaj DNS na podstawie tego repozytorium.

Materiały wizualne zachowują dotychczasowe oznaczenia i prawa ich właścicieli. Publiczna dostępność repozytorium nie oznacza udzielenia licencji na dowolne wykorzystanie zdjęć i marki.

## Aktualizacja, kontrola i wycofanie

Edytowalnym źródłem tej niezależnej strony jest `site/`: pełny HTML, CSS, JavaScript i zasoby. Nie potrzeba prywatnego generatora ani oryginalnego komputera. Edycję wspólnego elementu trzeba zastosować do wszystkich odpowiednich podstron; CMS dla obsługi nie jest wdrożony.

Aktualizacja: sklonuj repozytorium, utwórz gałąź, zmień źródła i `release.json`, zbuduj oba warianty, uruchom `scripts/audit_static.py` i `scripts/check_repository.py`, wykonaj testy przeglądarkowe. Przegląd zmian poprzedza push do `main`, który publikuje Pages. Sprawdź udany GitHub Actions run, publiczne `release.json`, właściwe podstrony oraz parametry pobytu; sam push nie potwierdza publikacji.

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

Wcześniejszy plan przekierowywania Pages do Sites został wycofany na wyraźne polecenie właściciela. Workflow publikuje pełną stronę. Historyczne raporty `PAGES-HANDOVER-23-1.json` oraz `PUBLICATION-23-1.json` dokumentują poprzedni etap; nie opisują obecnego sposobu publikacji Pages.

Przywrócenie starego projektu Sites jest możliwe przez jego historię wersji. Nie kasuj całego projektu: usunęłoby to właściwy adres i zagroziło danym licznika.


## Domena i pełne funkcje

Techniczna obsługa katalogu głównego nie oznacza gotowości do uruchomienia sprzedaży. GitHub Pages nie wykonuje kodu `server/`, nie zapisuje licznika D1 ani nie łączy się z PMS/Fiserv. Te funkcje wymagają hostingu serwerowego. Zasady GitHub Pages wykluczają używanie go jako darmowego hostingu do prowadzenia biznesu online i witryn nastawionych na transakcje handlowe: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits (sprawdzone 2026-10-06). Dla docelowej strony sprzedażowej kod zostaje na GitHubie, a wdrożenie i domena muszą trafić na odpowiedni hosting. Instrukcja: `docs/DOMENA-I-ODBIOR.md`.


## Lokalna gotowość SEO — bez publikacji

Prace SEO na gałęzi `codex/seo-readiness-verified-20261006` są wyłącznie lokalne. Nie uruchamiaj push, publikacji, zmian domeny ani indeksowania na podstawie tych testów.

- `python3 scripts/build.py --mode preview --base /hornigold-preview/` tworzy `_site/`: pełne noindex/nofollow/noarchive, Disallow: /, bez sitemapy. Tryb domyślny nadal jest preview.
- `python3 scripts/build.py --mode production-ready --base /` tworzy osobny `_production_ready/`: 693 kanoniczne trasy, robots i sitemapę dla hornigold.pl. Jest to artefakt lokalny, a nie publikacja lub gotowość całej działalności do sprzedaży. Nie zmienia `_site/`, DNS ani rezerwacji.
- `python3 scripts/audit_seo.py --mode preview` oraz `--mode production-ready` zapisują pełne raporty w `docs/seo/`.
- `python3 -m unittest discover -s tests -p 'test_seo.py'` sprawdza m.in. ochronę podglądu i izolację trybów.
- `python3 scripts/build_redirect_draft.py` odtwarza `REDIRECT_MAP_DRAFT.csv` z lokalnych aliasów; wymagana późniejsza weryfikacja starej domeny i zatwierdzenie mapy.
- `seo/metadata-overrides.json` zawiera jawne poprawki tytułów i opisów. `seo/structured-data-policy.json` dokumentuje zachowawczy zakres JSON-LD. Widocznych cen, oferty i danych kontaktowych nie zmieniano.
- CI Pages nadal publikuje wyłącznie `_site/` w trybie preview. `_production_ready/` jest ignorowany przez Git i nie jest czytany przez workflow. Pakowanie Sites wymaga trybu preview.

Kolejność późniejszego wdrożenia i ograniczenia: `SEO_PRODUCTION_HANDOFF.md`. Bieżąca macierz odbioru: `SEO_RELEASE_READINESS.md`. Nie mylić daty/wersji starszego raportu publikacji z obecnymi zmianami lokalnymi.

Worktree `hornigold-seo-readiness-review` jest zweryfikowaną kopią niezapisanych prac SEO z repozytorium głównego. Stan wejściowy zabezpieczono na Mac mini; źródłowego drzewa nie nadpisano. Późniejsze przeniesienie zmian wymaga porównania z aktualnym drzewem, a nie kopiowania w ciemno.

## Dokumentacja przyszłej sprzedaży - 23.7

Siedem wersji dokumentów zawiera sekcję `online-sales`. To wymagania przed uruchomieniem, nie potwierdzenie aktywnej sprzedaży ani zweryfikowanych taryf. [Warunki odbioru](docs/ONLINE_SALES_LAUNCH_GATES.md) rozdzielają źródła, decyzje właściciela i testy dostawców. `legal/checkout-contract.json` przechowuje przyszłe etykiety przycisków i wymagania podsumowania; nie jest aktywnym checkoutem.

## Dostępność - przygotowanie 23.8

[Zakres PAD i odbiór](docs/PAD_SCOPE_AND_ACCEPTANCE.md) opisują wymagane dane spółki, procedurę zgłoszeń i testy po podłączeniu silnika. `docs/PAD_BOOKING_ACCEPTANCE.json` ma 15 etapów w 7 językach, wszystkie przyszłe wyniki NOT_RUN. Nie utożsamiać przygotowania z dostępnością aktywnej sprzedaży. `accessibilityJourneyVerified` i `PADScopeConfirmed` pozostają false; PDF-y pozostają nieznakowane, z pełnym odpowiednikiem HTML.
