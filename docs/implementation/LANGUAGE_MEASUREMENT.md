# Pomiar odwiedzin i języków — 14.10.2026

Wersja 23.22 rozdziela wybór języka od otwarcia planowania pobytu. Linki językowe mają `data-stay`, ponieważ zachowują plan; nie oznacza to intencji rezerwacji. `language_switch` zawiera wyłącznie dozwolone kody źródła i celu. Odsłona zawiera `page_language`.

## Istniejące tagi

- GA4: `G-ZJ9VJNGHGT`, usługa `558323228`.
- Google Ads: `AW-18507796156` — istniejący kod pozostaje bez zmian.
- Tylko produkcja `hornigold.pl`, osobne zgody analityczne i marketingowe. Podglądy pozostają bez pomiaru i bez indeksacji.
- Brak nowego piksela, fingerprintingu, personalizacji lub pozorowanych zdarzeń `purchase`/`refund`.
- Daty, liczba gości, tekst formularza, e-mail i numer telefonu nie są przesyłane w zdarzeniu zmiany języka.

## Czeski ruch

Obsługiwany pomiar kodu języka to `cs`, nie `cz`. Dopuszczone etykiety kampanii: źródło `seznam` lub `sklik`, medium `cpc`, `paid_search` lub `organic`, kampania `cs_search` lub `cz_search`. Nie oznacza to uruchomienia reklam. Odnośnik przykładowy po publikacji czeskiego serwisu: `/cs/?utm_source=seznam&utm_medium=cpc&utm_campaign=cs_search`.

Czeskie podstrony nie są jeszcze opublikowane. Nie wolno dodawać canonicali, hreflang ani URL w sitemapie prowadzących do nieistniejących odpowiedników. Przy odbiorze lokalizacji sprawdzić `lang="cs"`, wzajemne `hreflang="cs"`, właściwy canonical, `og:locale="cs_CZ"`, Open Graph, Twitter Card, opisy obrazów oraz trzecią pozycję przełącznika.

Wymiary zdarzeń `page_language`, `source_language`, `target_language` zapisano w usłudze GA4 558323228 dnia 14.10.2026; ponowne wczytanie panelu potwierdziło wszystkie trzy wpisy. Odbiór nowych parametrów wymaga wdrożenia kodu i osobnego sprawdzenia. Rejestracja wymiaru nie dowodzi odbioru zdarzenia.

## Działający monitoring lokalny

Stabilna kopia skryptu: `/Users/kamilkita/Documents/Hornigold-monitoring/monitor_traffic.py`. Prywatna historia: `/Users/kamilkita/Documents/Hornigold-monitoring/traffic`. Skrypt wykonuje tylko GET licznika i release, zapisuje migawkę i przyrost od poprzedniego odczytu. Nie wykonuje JS strony ani konwersji testowych.

Pierwszy odczyt jest bazą, nie wynikiem dziennym. Odsłony nie są liczbą unikalnych osób. Zmiana daty początku lub spadek sumy wymaga sprawdzenia, a nie raportowania ujemnej odwiedzalności. GA4 obejmuje ruch pomierzony po zgodzie; jego sumy nie muszą odpowiadać licznikowi. Źródła sprzedaży i koszty reklam pozostają odrębnymi danymi.

Istniejący heartbeat pozostaje codziennie o 07:30 czasu Warszawy; w poniedziałki odczytuje dostępne GA4/GSC. Dane biznesowe zapisuje się wyłącznie prywatnie. Brak sesji nie przerywa publicznej kontroli i nie wywołuje codziennie tego samego alertu.

## Publikacja

Źródła: `kamilkita-ux/hornigold-preview`; gałąź pracy `codex/language-measurement-20261014`, docelowo sprawdzony `main`. Wdrożenie Cloudflare przez istniejący pipeline musi zachować aktywny licznik i D1: build produkcji z `--counter --production-counter`. Nie używać pakietu bez licznika do nadpisania działającej konfiguracji. Booking, GuestSage, Fiserv, DNS, poczta i bindings pozostają chronione.
