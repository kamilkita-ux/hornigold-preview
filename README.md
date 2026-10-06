# Hornigold — podgląd wersji 21

Samodzielny podgląd WWW: 693 podstrony w siedmiu językach (polski, angielski, niemiecki, chiński uproszczony, ukraiński, hiszpański, włoski).

Publiczny podgląd: https://kamilkita-ux.github.io/hornigold-preview/pl/

## Zakres

To wersja do przeglądu. Nie zastępuje hornigold.pl. Rezerwacje, płatności i integracja PMS są wyłączone. Formularze przygotowują zapytania do samodzielnego wysłania — nie tworzą rezerwacji. Regulamin sprzedaży internetowej, zasady pobytu i polityka prywatności oczekują na uzupełnienie i zatwierdzenie. `noindex` ogranicza indeksowanie, ale nie jest kontrolą dostępu: ten podgląd i repozytorium są publiczne.

GitHub Pages obsługuje statyczne pliki. W tej edycji nie działa serwerowy licznik odwiedzin; stopka informuje o jego wyłączeniu. Hosting GitHub może przetwarzać własne logi techniczne. Nie uruchomiono analityki reklamowej.

## Katalogi

- `site/` — kompletne pliki HTML, CSS, JavaScript i obrazy strony, bez prywatnych dokumentów, korespondencji i historii projektu.
- `scripts/build.py` — dostosowanie wszystkich lokalnych adresów do katalogu GitHub Pages oraz kontrola linków i trybu podglądu.
- `routes.json` — 693 właściwe adresy podstron; dodatkowe strony przekierowujące zachowują dawne adresy językowe.
- `.github/workflows/pages.yml` — publikacja po zmianie gałęzi `main` lub uruchomieniu ręcznym.

Dawne adresy używają przekierowania w przeglądarce, ponieważ ten podgląd nie ma serwera reguł HTTP 301. Parametry pobytu i kampanii oraz kotwice są zachowywane. Canonical wskazuje docelową domenę Hornigold; podgląd pozostaje nieindeksowany.

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
