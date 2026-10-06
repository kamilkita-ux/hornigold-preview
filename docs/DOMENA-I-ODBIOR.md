# Hornigold — podłączenie domeny i odbiór wdrożenia

Dla Marka Iwińskiego. Aktualizacja 2026-10-06: właściciel wymaga pełnej strony w repozytorium i na Pages, bez przekierowania do Sites. Workflow publikuje cały `_site/` i odczytuje `base_path` z `actions/configure-pages`; treści działają także po zbudowaniu z `--base /`. **Nie zmieniać teraz DNS ani hornigold.pl.**

- Strona do przeglądu: https://kamilkita-ux.github.io/hornigold-preview/pl/
- Repozytorium publiczne: https://github.com/kamilkita-ux/hornigold-preview
- Wersja bieżąca: `release.json`. Opublikowany commit: `/hornigold-preview/release.json` na stronie. Wdrożenie: GitHub Actions → Publish Hornigold preview; udany run musi wskazywać ten sam commit.
- Obecny hosting: GitHub Pages, projekt `kamilkita-ux/hornigold-preview`. Nie używać go do docelowej sprzedaży online. [Warunki Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), sprawdzone 2026-10-06.
- Przygotowany wariant alternatywny: Render Static Site, proponowana nazwa `hornigold-review`, konfiguracja `render.yaml`. **Usługa nie została utworzona, konto nie zostało połączone, URL/DNS nie są znane.** To hosting frontendu; PMS/Fiserv wymagają osobnej usługi serwerowej, trwałej bazy i workera.

## Stan danych DNS

| Nazwa | Docelowa wartość | Stan |
|---|---|---|
| hornigold.pl | Z panelu wybranego i utworzonego hostingu | BRAK — nie wdrażać |
| www.hornigold.pl | Z panelu tego samego hostingu | BRAK — nie wdrażać |
| Rekord potwierdzenia domeny | Z panelu konkretnego projektu | BRAK — nie wdrażać |
| MX / SPF / DKIM / DMARC | Zachować obecne wartości z eksportu strefy | Eksport jeszcze nie otrzymany |

Nie wpisujemy przykładowych IP jako rekordów produkcyjnych. Dostęp do konta hostingu i strefy DNS jest potrzebny, aby uzupełnić tę tabelę rzeczywistymi wartościami. Nie ma obecnie kompletnego przekazania DNS. Nie zmieniać serwerów nazw bez odtworzenia i weryfikacji całej strefy oraz usług pocztowych.

Główny adres planowany: `https://hornigold.pl`; `https://www.hornigold.pl` ma przekierowywać HTTP 301 do głównego z zachowaniem ścieżki i parametrów. Potwierdzić ten wybór przy odbiorze.

Przekierowanie oznacza zmianę adresu w przeglądarce. Podłączenie domeny do hostingu oznacza, że pliki są obsługiwane pod hornigold.pl bez ujawniania adresu dostawcy. Sam CNAME lub przekierowanie u rejestratora nie gwarantują HTTPS, poprawnych podstron ani działania rezerwacji.

## Kolejność późniejszego przełączenia

1. Odebrać treści, prawa, dokumenty, języki i model uruchomienia (informacja/kontakt albo zweryfikowana sprzedaż). Osobna zgoda właściciela na domenę i zdjęcie noindex.
2. Wybrać i utworzyć projekt hostingu z repozytorium, potwierdzić uprawnienia, koszt i region danych. `render.yaml` nie provisionuje backendu rezerwacji.
3. Wykonać kopię obecnej strony: pliki, bazę i konfigurację; odtworzyć ją w odizolowanym środowisku. Wyeksportować pełną strefę DNS z TTL, także rekordy pocztowe. Zapisać stare A/AAAA/CNAME i plan odtworzenia.
4. Zbudować `python scripts/build.py --base /`; wykonać `python scripts/audit_static.py --base /`. Wariant katalogowy służy tylko Pages. Opublikować `_site/` pod adresem technicznym nowego hostingu i wykonać testy.
5. Uzyskać z panelu rzeczywiste rekordy i uzupełnić tabelę wyżej. Zweryfikować własność obu nazw, status certyfikatu, ewentualne CAA oraz konfliktujące A/AAAA/CNAME. Nie usuwać MX/TXT używanych przez pocztę.
6. Przygotować serwerowe HTTP 301 starych URL na nowe; obecne pliki przekierowań JS nie są zamiennikiem 301. Pełny eksport starych URL i zatwierdzenie mapy pozostają wymagane. Nie stosować przekierowania wszystkich błędów na stronę główną.
7. Po odbiorze i zgodzie zmienić tylko wymagane rekordy. Sprawdzić HTTPS dla obu nazw, 301 www, podstrony, parametry, 404, canonical, hreflang, sitemapę, wysyłanie/odbiór poczty i wymagane funkcje.
8. Usunąć noindex i zmienić robots/sitemapę dopiero po osobnej zgodzie. Obecny build wymusza noindex i nie jest buildem otwartej produkcji.
9. Monitorować dostępność, błędy, rezerwacje/maile w zatwierdzonym zakresie. Zachować stary hosting przez uzgodniony okres powrotu.

## Powrót

Przy błędzie DNS/HTTPS lub kluczowej funkcji przywrócić zapisane stare rekordy z eksportu, nie ruszając poczty. Sprawdzić starą stronę z kilku resolverów; propagacja zależy od TTL. Dla regresji kodu bez zmiany domeny wdrożyć zatwierdzony poprzedni commit. Nie cofać bazy rezerwacji do starej kopii kosztem utraty płatności; dane finansowe uzgodnić osobno.

## Odbiór

- [ ] Potwierdzony projekt hostingu, domeny, rekordy DNS i certyfikaty.
- [ ] Kopia serwisu i strefy oraz przetestowane odtworzenie.
- [ ] MX, SPF, DKIM i DMARC zachowane; test odebranej i wysłanej wiadomości.
- [ ] Siedem języków, daty, goście, kontakt, dokumenty, dostępność i widoki mobilne.
- [ ] Pełna mapa 301 oraz prawdziwe 404, canonical/hreflang/sitemap.
- [ ] Zatwierdzone prawa do materiałów i dokumenty.
- [ ] Funkcje serwerowe odebrane albo jawnie nieaktywne.
- [ ] Osobny odbiór sandbox PMS/Fiserv przed sprzedażą.
- [ ] Monitorowanie, kopie i osoba odpowiedzialna za utrzymanie.
- [ ] Zgoda właściciela na przełączenie i indeksowanie.
