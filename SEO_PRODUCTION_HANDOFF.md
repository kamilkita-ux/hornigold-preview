# SEO_PRODUCTION_HANDOFF

Lokalne przygotowanie, 6 października 2026. Nie jest poleceniem publikacji ani zmiany DNS. Każdy etap zewnętrzny wymaga późniejszego zlecenia właściciela.

## 1. Odebrać lokalne źródła

1. Zachować oryginalne niezapisane prace i kopię Mac mini. Przed scaleniem porównać gałąź `codex/seo-readiness-verified-20261006` z aktualnym `hornigold-github-preview`; nie kopiować plików na nieznane zmiany.
2. Przeczytać `SEO_RELEASE_READINESS.md`, raporty `docs/seo/` oraz `seo/structured-data-policy.json`.
3. Zdecydować, czy uruchomienie obejmie tylko serwis informacyjny i kontakt, czy również sprzedaż. Rezerwacje i płatności pozostają wyłączone do osobnego odbioru dostawców.
4. Utrzymać minimalne WebPage. Rozszerzony JSON-LD wolno dodać po otrzymaniu datowanego i zatwierdzonego źródła każdego pola. Nie kopiować starego LodgingBusiness/FAQPage/Article z surowego site/ do publikacji.
5. Potwierdzić treści, prawa do zdjęć, dokumenty i lokalizację językową; test techniczny nie jest takim potwierdzeniem.

## 2. Odtworzyć i sprawdzić buildy

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build.py --mode preview --base /hornigold-preview/
python3 scripts/audit_seo.py --mode preview
python3 scripts/audit_static.py --base /hornigold-preview/
python3 scripts/build.py --mode production-ready --base /
python3 scripts/audit_seo.py --mode production-ready
python3 -m unittest discover -s tests -p 'test_seo.py'
python3 scripts/build_redirect_draft.py
python3 scripts/check_repository.py
```

`_site/` jest wyłącznie preview. Musi pozostać noindex/nofollow/noarchive, Disallow: /, bez sitemapy. Domyślny tryb i GitHub Actions wskazują preview. `release.json` źródłowy nadal ma indexing=false. `_production_ready/` jest osobnym, lokalnym artefaktem; `published=false` oznacza wynik buildu, nie monitorowanie faktycznego wdrożenia. Nie wykonywać publish/push w ramach tego odbioru lokalnego.

Do powtórzenia testów przeglądarek użyć serwerów loopback z `scripts/serve_seo.py`. Audyty blokują zewnętrzne żądania. Wymagane Node/Playwright/axe wg package.json. Nie korzystać z profilu osobistej przeglądarki ani wykonywać rzeczywistej rezerwacji.

## 3. Wybrać hosting i uzyskać zgodę na uruchomienie

1. Kod może pozostać na GitHubie. GitHub Pages jest aktualnym podglądem i nie jest zatwierdzonym hostingiem produkcyjnej sprzedaży; jego warunki sprawdzono wcześniej i opisano w `docs/DOMENA-I-ODBIOR.md`.
2. Wybrać hosting dla https://hornigold.pl. Potwierdzić obsługę TLS, prawdziwych 404, serwerowych 301, nagłówków i ewentualnego backendu. Zatwierdzić koszt, konto i uprawnienia.
3. Uzgodnić główną nazwę hornigold.pl oraz 301 z www z zachowaniem ścieżki i parametrów. Potwierdzić własność domeny i model DNS. Nie używać DNS do przekierowywania wszystkich podstron na homepage.
4. Wyeksportować pełną strefę DNS, zabezpieczyć istniejące pliki/bazę, wykonać próbę odtworzenia i zapisać plan powrotu. Zachować MX/SPF/DKIM/DMARC oraz usługi pocztowe.
5. Uzyskać osobną zgodę na przełączenie domeny oraz otwarcie indeksowania. Testy lokalne nie stanowią takiej zgody.

## 4. Odebrać pełną mapę 301

1. Uzyskać eksport URL starego serwisu z CMS i dostępnych źródeł właściciela. Obecne 1078 wierszy pochodzi wyłącznie z lokalnych aliasów, nie z aktualnego crawlu hornigold.pl.
2. Dopasować każdy stary URL do właściwego nowego odpowiednika w tym samym języku. Nie kierować masowo błędów na homepage. Zachować parametry pobytu zgodnie z integracją.
3. Zatwierdzić mapę, usunąć konflikty i spłaszczyć łańcuchy. Stare URL bez odpowiednika wymagają decyzji 404/410; nie tworzyć fikcyjnych treści.
4. Wdrożyć mapę jako HTTP 301 na wybranym hostingu dopiero po zgodzie. Obecne statyczne aliasy JS nie zastępują serwerowego 301.

## 5. Zastosować właściwy artefakt i nagłówki

1. Zbudować production-ready z --base / i wdrożyć jego zawartość wyłącznie na zatwierdzonym hostingu. Nie publikować bezpośrednio site/, _site/ ani _production_ready/ na podglądzie Pages.
2. Utrzymać robota `Allow: /`, `Disallow: /api/` i sitemapę https://hornigold.pl/sitemap.xml. Sitemap zawiera tylko 693 kanoniczne trasy, bez aliasów, 404, PDF, parametrów i dat lastmod wymyślonych z daty buildu.
3. Usunąć blanket noindex tylko z docelowego wariantu, także w HTTP, CDN, platformie i szablonach. Sprawdzić `_headers`; hosting musi jawnie wspierać ten format lub otrzymać równoważną konfigurację. Zachować blokady preview.
4. Aktualne `server/routes.mjs` ma siteMode=preview, Worker dodaje globalny X-Robots-Tag, a render.yaml deklaruje noindex. Nie wdrażać ich bezpośrednio jako otwartej produkcji. Wdrażający musi przygotować odpowiadającą wybranemu hostingowi konfigurację i przetestować jej nagłówki. Production-ready w tym zadaniu obejmuje zasoby statyczne, nie aktywację Workera/D1.
5. API, błędy 404 i pobierane PDF pozostają nieindeksowane. Zwracać prawdziwe statusy; nie włączać catch-all 200 dla brakujących URL.
6. Zachować canonical, OG URL i hreflang wyłącznie w domenie hornigold.pl, x-default na polski odpowiednik. Nie kierować produkcyjnych canonicali do github.io lub chatgpt.site.

## 6. Sprawdzić po późniejszym wdrożeniu

1. Odpytać HTTP/HTTPS, hornigold.pl/www oraz kilka niezależnych resolverów; potwierdzić TLS, jedną kanoniczną nazwę i statusy 200/301/404/410.
2. Sprawdzić wszystkie 693 trasy i pełną zatwierdzoną mapę przekierowań: zachowanie języka, parametrów, brak pętli/łańcuchów, brak przekierowań do technicznego adresu hostingu.
3. Odczytać robots, sitemapę, meta robots i HTTP X-Robots-Tag. Każdy URL sitemap/canonical/hreflang ma zwracać docelowy 200, prawidłowy język i być dozwolony dla crawlera. Podglądy muszą nadal blokować indeksowanie.
4. Powtórzyć audyt metadanych, obrazów, linków, schema, mobilności i dostępności na rzeczywistym hostingu. Ręcznie sprawdzić klawiaturę, czytnik ekranu, prawdziwe urządzenia i jakość tłumaczeń.
5. Sprawdzić zewnętrzne odsyłacze i karty społecznościowe. Nie deklarować ich poprawności z audytu offline.
6. Dopiero po uprawnionej weryfikacji Search Console przesłać produkcyjną sitemapę i sprawdzić reprezentatywne adresy. Monitorować indeksację, błędy, duplikaty i wykluczenia; samo przesłanie nie gwarantuje indeksacji ani rankingu.
7. Zmierzyć wydajność na docelowym hostingu i, gdy będą dostępne, dane od rzeczywistych użytkowników. Lokalny pomiar nie jest field CWV i nie zawiera rzeczywistego INP.
8. Analitykę i reklamy uruchamiać tylko po oddzielnym odbiorze zgód, ustawień i zakresu pomiaru. Nie są włączane przez SEO.
9. Rezerwacje/płatności testować osobno w odebranym sandboxie PMS/Fiserv, z potwierdzeniami w siedmiu językach. Nie wykonywać realnych płatności na podstawie tego dokumentu.
10. Zachować stare wdrożenie i kopie. W razie kluczowej regresji wrócić do zatwierdzonego poprzedniego kodu lub zapisanych rekordów DNS bez utraty danych rezerwacyjnych i poczty.

## Stan adresów

- Sites: https://hornigold-przeglad-beata.ai-bd6d706867.chatgpt.site/pl/
- GitHub Pages: https://kamilkita-ux.github.io/hornigold-preview/pl/

To istniejące publikacje sprzed tej pracy lokalnej. Zmiany SEO z worktree nie zostały na nie wysłane; nie potwierdzano teraz ich aktualnego stanu przez sieć.
