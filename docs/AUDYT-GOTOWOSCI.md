# Hornigold — audyt gotowości

Stan 2026-10-06, wersja 22. Nie jest to certyfikat zgodności prawnej, WCAG ani kompletnego przekładu profesjonalnego. Usunięcie banera zostało osobno zlecone przez właściciela. Noindex, nieaktywne rezerwacje i płatności pozostają.

| Obszar | Status i dowód | Ryzyko / czynność | Odpowiedzialny | Odbiór |
|---|---|---|---|---|
| Źródła i build | Komplet statycznych źródeł w site; build / i /hornigold-preview/ przechodzi | Wspólne zmiany wymagają aktualizacji wszystkich HTML | Programista | Czysty CI i artefakt |
| Nawigacja i zasoby | 693 trasy, 1241 HTML z aliasami; 59149 odwołań, 0 błędów/ostrzeżeń w obu wariantach | Publiczna kopia wymaga osobnego odczytu | Programista | publiczne sumy/HTTP zgodne z commitem |
| Przeglądarki | 819 przypadków Chromium/Firefox/WebKit, 375/768/1366 px, 7 języków, 0 błędów | Emulacja, nie urządzenia; WebKit nie jest wydanym Safari | QA | osobny ręczny test Safari i urządzeń |
| Zakres próbek | Home, pokoje, Classic, lokalizacja, kontakt, dokumenty, miasto, ilustracje, gastronomia, pobyt, rezerwacja, FAQ | Nie każdy artykuł poddano ręcznej ocenie wzrokowej | QA | odbiór edytorski wszystkich treści |
| Daty i języki | 63 testy interakcji na kontekstach 7 × 3 × 3; zachowanie dat/gości po języku i odświeżeniu, menu Escape | Zewnętrzny PMS niepodłączony | Programista/dostawca | sandbox w 7 językach |
| Dostępność | Alt, h1, etykiety i elementy nawigacji kontrolowane; brak poziomego overflow w próbkach | Pełna klawiatura, czytniki, kontrast wszystkich stanów i zoom niewykonane; nie deklarować WCAG PASS | QA | ręczny protokół i usunięcie usterek |
| Oferta i operator | Dane operatora i kontakt na stronie; dane ceny opisowe, nie aktualny PMS | Weryfikacja wszystkich faktów z właścicielem | Beata/właściciel | podpisany wykaz oferty |
| Materiały | Dotychczasowe zasoby gościnne; źródła i część atrybucji w stronie | Pełne potwierdzenie praw każdego zdjęcia nadal nieudokumentowane w repo; publiczność nie jest licencją | Właściciel | rejestr źródło/licencja/zgoda/pliki |
| Języki | Siedem wersji i wzajemny hreflang; kontrola strukturalna | Brak udokumentowanego niezależnego odbioru przez tłumaczy wszystkich artykułów | Redakcja/tłumacze | podpisany odbiór 7 języków |
| Dokumenty | Dotychczasowe sekcje oznaczały braki; nowy plik regulaminu otrzymany w tym zadaniu | Oddzielny przekład i odbiór; brak polityki prywatności i cennika-załącznika | Właściciel/prawnik | zgodne aktualne dokumenty |
| Formularze | Lokalne przygotowanie wiadomości / mailto; brak serwerowej wysyłki | Otwarcie poczty nie jest wysłaniem; test odbioru recepcji niewykonany | Recepcja | wysłany i odebrany kontrolowany test |
| Kontakt do Marka | Pierwsza wiadomość do wskazanego adresu wróciła jako niedostarczona | Wymagany poprawny kanał, nie oznaczać doręczenia | Właściciel | potwierdzony odbiór |
| PMS / channel manager | Niepotwierdzony kontrakt API i sandbox; ślady KWHotel/UpperBooking nie dowodzą aktywnego API | Bloker sprzedaży | Dostawca PMS | odpowiedzi i testy z PMS-FISERV.md |
| Fiserv | Schemat i pytania gotowe; brak potwierdzonego produktu, podpisu webhooka i konta sandbox | Bloker sprzedaży; zero realnych rezerwacji/opłat | Fiserv/operator | sandbox, 3DS, webhook, odtwarzanie |
| Analityka / Ads / licznik | Nieaktywne; serwerowy licznik nie jest uruchomiony w Pages | Nie ma pomiaru wszystkich wizyt ani konwersji | Marketing/programista | zatwierdzony pomiar i zgody |
| Cookies i prywatność | Język w localStorage, pobyt w sessionStorage/URL, linki zewnętrzne; brak automatycznych reklam | Hosting przetwarza logi; noindex nie chroni danych | Właściciel/prawnik | polityka odzwierciedla realne usługi |
| Bezpieczeństwo repo | Skan wzorców sekretów i typów prywatnych plików, także historia: 0 trafień | Skan nie dowodzi braku wszystkich sekretów | Programista | kontrola każdego commitu, GitHub secret scanning |
| Nagłówki | Przygotowane w render.yaml; Pages nie wykonuje backendu ani konfiguracji dowolnych nagłówków | Pełna CSP, nagłówki API i testy bezpieczeństwa przed produkcją | Hosting/programista | nagłówki odczytane po wdrożeniu |
| SEO | Lang, meta, canonical i wzajemne hreflang zweryfikowane; robots blokuje indeksowanie | Sitemap produkcyjna i 301 dopiero po potwierdzeniu domeny/mapy; nie włączać indeksowania | SEO/programista | mapa stare/nowe, brak łańcuchów, test 301 |
| Hosting / DNS | Pages działa; Render blueprint przygotowany, konto/projekt nieutworzone | Pages nie jest docelowym hostingiem biznesowej sprzedaży; nie znamy rekordów DNS nowego dostawcy | Marek/właściciel | rzeczywisty projekt i tabela DNS |
| CMS | Statyczne źródła, brak panelu recepcji | Zmiany wymagają programisty | Właściciel | ustalony proces aktualizacji |
| Kopie / rollback | Instrukcja w README i dokumencie domeny | Test odtworzenia starego WordPressa, bazy i DNS niewykonany | Marek/administrator | udany test restore i uzgodnione RTO/RPO |
| Monitoring | GitHub CI stan wdrożenia; brak alertów dostępności/awarii płatności | Potrzebna osoba i kanał reagowania | Administrator | kontrolowany alarm i reakcja |
| Wydajność | Brak pomiaru danych rzeczywistych użytkowników; próby przeglądarkowe nie są Core Web Vitals | Osobny pomiar laboratoryjny z profilem mobilnym i potem RUM | QA | raport LCP/CLS/INP ze źródłem pomiaru |

**Blokuje sprzedaż:** PMS/Fiserv, dokumenty i regulaminowe reguły płatności, hosting z backendem, potwierdzenia, uzgodnienie danych i awarii. **Blokuje przełączenie domeny:** odbiór treści/praw, projekt hostingu i DNS, kopia/restore, mapa 301 i zgoda właściciela. **Możliwe później po decyzji:** CMS, dodatkowa analityka i nowe funkcje redakcyjne.

Pełny audyt wymagany w briefie nie jest zakończony. Tabela celowo wyróżnia niewykonane kontrole; testy wersji 22 nie zastępują testów kolejnego commitu.
