# PROMPT DLA CODEX — Hornigold w Zielonej Kamienicy: program SEO / AI-search „100%”

**Wersja:** 2.0 · 03.11.2026 · zastępuje `prompt-codex-hornigold-seo-top3.md`
**Strona:** https://hornigold.pl · języki: pl, en, de, cs, zh-hans, uk, es, it
**Właściciel decyzji:** Kamil Kita · **Wykonawca:** Codex
**Źródło audytu:** audyt Claude z 03.11.2026 (ocena 52/100)

---

## 0. JAK PRACUJESZ (przeczytaj przed pierwszym zadaniem)

1. **Zadanie po zadaniu.** Realizuj zadania w kolejności numerów (`T-01`, `T-02`…). Nie zaczynaj kolejnego, dopóki bieżące nie spełnia **wszystkich kryteriów akceptacji**.
2. **Po każdym zadaniu** oddajesz krótki raport: `ID | co zmieniono | pliki | wynik testu | zrzut/URL dowodu | czas`. Następnie zwiększasz numer wersji w stopce.
3. **Źródło prawdy:** `data/hotel-facts.json`. Publikujesz wyłącznie pola ze statusem `confirmed`. Brak faktu → element się nie wyświetla (nie wpisuj „do potwierdzenia”, nie zgaduj).
4. **Nie ruszasz logiki silnika rezerwacji KWHotel.** Wolno: linki, parametry UTM, zdarzenia analityczne, etykiety przycisków.
5. **Wszystkie 8 języków** dostają każdą zmianę. Tłumaczenia naturalne (nie dosłowne), z frazami, których naprawdę szukają ludzie w danym kraju.
6. **Zadania oznaczone `[KAMIL]`** wymagają działania lub decyzji Kamila poza kodem — przygotuj instrukcję krok po kroku i oznacz zadanie jako „czeka na Kamila”, po czym przejdź do następnego zadania.
7. **Zakazy bezwzględne (kara od Google lub utrata zaufania):**
   - ukryty tekst / ukryte słowa kluczowe (biały tekst, `display:none`, `font-size:0`, tekst poza ekranem, tekst tylko dla robotów),
   - cloaking (inna treść dla robota niż dla człowieka),
   - upychanie słów kluczowych (keyword stuffing), ukryte linki,
   - kopiowanie ocen z Google Maps do `aggregateRating` na własnej stronie,
   - fałszywe opinie, wymyślone nagrody, „najlepszy/najtańszy hotel w Katowicach”.

---

## 1. POLITYKA SŁOWA „HOTEL” (decyzja Kamila — obowiązuje w całym projekcie)

**Cel:** Google, Bing i wyszukiwarki AI mają jednoznacznie rozumieć, że Hornigold to **hotel** (fraza „hotel Katowice”, „hotel w centrum Katowic”), ale gość na stronie **nie ma odczuwać krzykliwego „HOTEL”**. Marka komunikuje się jako „Zielona Kamienica” — kameralnie, butikowo.

**To nie jest ukrywanie.** Słowo „hotel” jest widoczne i czytelne, tylko **nie dominuje wizualnie**. Wszystko poniżej jest zgodne z wytycznymi Google.

| Miejsce | Zasada | Przykład PL |
|---|---|---|
| `<title>` | „hotel” obowiązkowo, w środku lub na końcu | `Pokoje i apartamenty w centrum Katowic · butikowy hotel Hornigold` |
| meta description | „hotel” 1× naturalnie | „Butikowy hotel w zielonej kamienicy, 5 min od dworca PKP…” |
| Dane strukturalne | `@type: Hotel` (nie `LodgingBusiness`) | — |
| H1 strony głównej | **Dwa poziomy w jednym H1:** mała, spokojna linia nad tytułem (font 13–14 px, wersaliki z rozstrzeleniem, kolor drugorzędny) + duży tytuł bez słowa „hotel” | `<h1><span class="h1-eyebrow">Butikowy hotel · Katowice centrum</span><span class="h1-main">Pokoje i apartamenty w Zielonej Kamienicy</span></h1>` |
| H1 podstron | „hotel” tylko gdy naturalne (np. „Hotel z jacuzzi i sauną…” na stronie SPA), inaczej w linii `h1-eyebrow` | — |
| Okruszki (breadcrumb) | pierwszy element: „Hotel Hornigold” | `Hotel Hornigold / Pokoje / Classic` |
| Treść | „hotel” 2–4× na 1000 słów, w zdaniach dla ludzi | „W naszym hotelu śniadania podajemy 7:00–10:00.” |
| Alt zdjęć | gdzie pasuje: „…w hotelu Hornigold, Katowice” (max 1 na 3 zdjęcia) | — |
| Stopka | linia z NAP: „Hornigold w Zielonej Kamienicy — butikowy hotel · ul. Mikołaja Kopernika 6, 40-064 Katowice” | — |
| Logo / nagłówek strony | **bez** słowa „hotel” (marka zostaje kameralna) | — |
| Przyciski, banery, hero | **bez** słowa „HOTEL” wersalikami | — |

**Kryteria akceptacji polityki:** na każdej stronie „hotel” występuje w `<title>` lub description, w schema i co najmniej raz w widocznej treści; nigdzie nie jest większe niż tekst akapitu poza H1 strony SPA/lokalizacji; nigdzie nie jest ukryte.

---

## 2. KATEGORIE I CEL 100%

| # | Kategoria | Dziś | Cel | Zadania |
|---|---|---|---|---|
| A | Technika i wydajność | 88 | 100 | T-01 – T-06 |
| B | Indeksacja i wersje językowe | 55 | 100 | T-07 – T-13 |
| C | Tytuły, opisy, nagłówki | 50 | 100 | T-14 – T-18 |
| D | Dane strukturalne | 40 | 100 | T-19 – T-24 |
| E | Treść i strony pod intencje | 55 | 100 | T-25 – T-34 |
| F | Linkowanie wewnętrzne i nawigacja | 70 | 100 | T-35 – T-38 |
| G | Wyszukiwarki AI (ChatGPT, Perplexity, Gemini, Copilot) | 60 | 100 | T-39 – T-42 |
| H | Konwersja i rezerwacja bezpośrednia | 70 | 100 | T-43 – T-48 |
| I | Dostępność (WCAG 2.2 AA) i zgodność prawna | 75 | 100 | T-49 – T-53 |
| J | Pomiar i analityka | 30 | 100 | T-54 – T-58 |
| K | Widoczność lokalna i moduł hoteli Google (poza kodem) | 45 | 100 | T-59 – T-66 `[KAMIL]` |
| L | Autorytet i linki zewnętrzne | 20 | 100 | T-67 – T-70 `[KAMIL]` |

„100%” w kategoriach A–J = spełnione wszystkie kryteria akceptacji + zielone testy. K–L zależą od działań Kamila i czasu (Google potrzebuje tygodni na reakcję).

---

## A. TECHNIKA I WYDAJNOŚĆ

**T-01 · Lighthouse mobile ≥ 95 we wszystkich czterech kategoriach**
- Strony testowe: `/pl/`, `/pl/pokoje/`, `/pl/pokoje/classic/`, `/pl/wellness-spa/`, `/en/`, `/de/`.
- ✅ Performance ≥ 95, Accessibility ≥ 98, Best Practices 100, SEO 100 na każdej. Raport z wynikami.

**T-02 · Core Web Vitals w normie z zapasem**
- LCP < 2,0 s (mobile, 4G), INP < 150 ms, CLS < 0,05.
- Obraz główny: `fetchpriority="high"`, `<link rel="preload">`, AVIF + WebP, `width/height`.
- ✅ Wynik PageSpeed Insights (dane laboratoryjne) i, po 28 dniach, dane terenowe CrUX w Search Console.

**T-03 · Obrazy**
- Każde zdjęcie: AVIF/WebP, `srcset` (480/800/1200/1600), `sizes`, `loading="lazy"` poza pierwszym ekranem, `decoding="async"`.
- Obraz Open Graph 1200×630 dla **każdej** strony (pokoje: zdjęcie danej kategorii).
- ✅ Brak obrazu > 200 KB na mobile; brak ostrzeżeń „properly size images”.

**T-04 · Nagłówki HTTP i bezpieczeństwo**
- HTTPS + HSTS (`max-age=31536000; includeSubDomains`), `X-Content-Type-Options`, `Referrer-Policy: strict-origin-when-cross-origin`, CSP zezwalająca tylko na potrzebne domeny (KWHotel, GA4/GTM po zgodzie, Google Maps po kliknięciu).
- Cache: zasoby z hashem `max-age=31536000, immutable`; HTML `no-cache` z ETag.
- Kompresja Brotli.
- ✅ securityheaders.com ≥ A; zero błędów CSP w konsoli na 20 losowych podstronach.

**T-05 · Przekierowania i kanonikalizacja**
- Jedna wersja: `https://hornigold.pl/` → 301 → `/pl/` (lub wykrywanie języka tylko jako baner, bez automatycznego przekierowania robotów).
- `http://`, `www.` → 301 w jednym kroku (bez łańcuchów).
- Stare adresy poprzedniej strony (WordPress) — z logów serwera i z Search Console (Kamil przekaże eksport) — mapa 301 na najbliższy odpowiednik.
- ✅ Crawl całej strony (np. Screaming Frog / własny skrypt): 0 łańcuchów przekierowań, 0 linków wewnętrznych do 3xx/4xx.

**T-06 · Strona 404 i 410**
- 404 w 8 językach z wyszukiwarką/menu i linkami do pokoi; status HTTP 404 (nie 200).
- Strony celowo usunięte: 410.
- ✅ Test statusów.

---

## B. INDEKSACJA I WERSJE JĘZYKOWE

**T-07 · Mapa strony z wersjami językowymi**
- `sitemap-index.xml` → `sitemap-pl.xml`, `sitemap-en.xml`… (po jednej na język).
- Każdy `<url>`: `<loc>`, `<lastmod>` (prawdziwa data zmiany treści, nie data builda), komplet `xhtml:link rel="alternate" hreflang` (8 języków + `x-default`), `image:image` dla zdjęć pokoi.
- Wyklucz: strony `noindex`, przekierowania, parametry, stronę rezerwacji.
- ✅ Walidacja XML; liczba URL w mapie = liczba stron indeksowalnych z crawla.

**T-08 · Czeska wersja z czeskimi adresami**
- Dziś `/cs/` używa angielskich slugów (np. `/cs/a-relaxed-visit-starts-before-arrival/`). Wprowadź czeskie slugi, 301 ze starych, aktualizacja hreflang/canonical/sitemap.
- Sprawdź to samo dla `uk`, `es`, `it`, `zh-hans`, `de`, `en`.
- ✅ 0 adresów z obcojęzycznym slugiem w danej wersji językowej.

**T-09 · Zwrotne i kompletne hreflang**
- Każda strona wskazuje wszystkie 8 odpowiedników + `x-default` i każdy odpowiednik wskazuje z powrotem.
- Brak odpowiednika → strona nie ma hreflang do nieistniejącej wersji.
- ✅ Test hreflang (np. narzędzie Merkle/hreflang checker) bez błędów.

**T-10 · Język treści = język strony**
- Problem z audytu: na polskie zapytanie Google pokazał tytuł niemieckiej wersji. Upewnij się, że `<html lang>`, `<title>`, description, H1, treść i `og:locale` są w tym samym języku.
- ✅ Skrypt: dla każdej strony wykryj język tekstu i porównaj z `lang` — 100% zgodności.

**T-11 · Kanoniczne adresy**
- Każda strona: samoreferencyjny `rel=canonical` (absolutny, https, ze slashem końcowym zgodnie z konwencją).
- Strony z parametrami (`?arrival=`, `?room=`, UTM) → canonical do wersji bez parametrów.
- ✅ Crawl: 0 konfliktów canonical/hreflang/sitemap.

**T-12 · Robots i meta robots**
- `robots.txt`: obecny jest poprawny; dodaj blokadę parametrów wyszukiwania terminu (`/*?arrival=`) jeśli generują duplikaty.
- Strony techniczne (podgląd, test, „Club Hornigold” jeśli nieaktywny) → `noindex,follow`.
- ✅ Brak indeksowalnych duplikatów.

**T-13 · Odświeżenie indeksu `[KAMIL + Codex]`**
- Codex: przygotuj listę 30 najważniejszych URL (PL + EN + DE).
- Kamil: Google Search Console → zweryfikuj domenę (rekord DNS TXT), wyślij `sitemap-index.xml`, „Sprawdź URL → Poproś o zindeksowanie” dla listy 30. To samo w Bing Webmaster Tools (+ IndexNow — Codex wdraża klucz i ping przy publikacji).
- ✅ Po 14 dniach: raport „Strony” w GSC — zaindeksowane ≥ 90% adresów z mapy.

---

## C. TYTUŁY, OPISY, NAGŁÓWKI

**T-14 · Usuń szablon opisów**
- Dziś każda podstrona ma opis „X. Poznaj Hornigold przy Kopernika 6 w Katowicach. Zobacz zdjęcia, zaplanuj pobyt…”. Zastąp unikalnymi opisami.
- ✅ 0 zduplikowanych `<title>` i 0 zduplikowanych description w całym serwisie (crawl).

**T-15 · Tytuły i opisy — kluczowe strony PL (wdroż dokładnie lub lepiej, zgodnie z polityką „hotel”)**

| URL | `<title>` (≤ 60 zn.) | description (140–160 zn.) |
|---|---|---|
| /pl/ | Pokoje i apartamenty w centrum Katowic · butikowy hotel Hornigold | Butikowy hotel w zielonej kamienicy, 5 min pieszo od dworca PKP Katowice. Pokoje od 380 zł, apartamenty do 105 m², sauna i jacuzzi. Zarezerwuj bezpośrednio. |
| /pl/pokoje/ | Pokoje i apartamenty w Katowicach – ceny od 380 zł · Hornigold | 9 kategorii: od pokoju Classic 20 m² po apartament 105 m² z dwiema sypialniami. Centrum Katowic, Kopernika 6. Sprawdź ceny i dostępność. |
| /pl/wellness-spa/ | Hotel z jacuzzi i sauną w centrum Katowic · Hornigold | Prywatna strefa wellness na wyłączność: jacuzzi od 150 zł, sauna 90 zł/h, masaże od 200 zł. W butikowym hotelu przy dworcu w Katowicach. |
| /pl/lokalizacja/ | Nocleg 5 minut od dworca PKP Katowice · Hornigold | Hornigold przy ul. Kopernika 6 — 5 minut spacerem od dworca, blisko Mariackiej, Rynku i Spodka. Wirtualny spacer z dworca i parking na dziedzińcu. |
| /pl/sniadania/ | Śniadania 7:00–10:00 w centrum Katowic · Hornigold | Domowe śniadanie w Zielonej Kamienicy codziennie 7:00–10:00, 60 zł/os. Na wczesny wyjazd — śniadanie na wynos po uzgodnieniu z recepcją. |
| /pl/parking/ | Parking na dziedzińcu w centrum Katowic · Hornigold | Prywatny parking na dziedzińcu hotelu przy Kopernika 6. Sprawdź warunki wjazdu i zarezerwuj miejsce razem z pokojem. |
| /pl/konferencje/ | Sale konferencyjne w centrum Katowic · Hornigold | Sale na spotkania i szkolenia w zabytkowej kamienicy przy dworcu PKP. Noclegi dla uczestników, catering, faktura VAT. Zapytaj o ofertę. |
| /pl/pobyt/wydarzenie/ | Nocleg blisko Spodka, MCK i NOSPR · Hornigold Katowice | Jedziesz na koncert lub kongres? Hornigold to spokojny nocleg w centrum, pieszo do Strefy Kultury. Plan dojścia i późne zameldowanie. |
| /pl/pokoje/hornigold/ | Apartament 105 m² z dwiema sypialniami w Katowicach · Hornigold | Największy apartament w Zielonej Kamienicy: dwie sypialnie, dwie łazienki, dwa aneksy kuchenne. Dla rodziny lub grupy znajomych w centrum Katowic. |

- Pozostałe strony (pokoje, przewodniki, FAQ, kontakt, o nas, oferty, opinie, dla firm, lotniska): ten sam standard — **fraza główna na początku, korzyść, liczba, CTA**.
- ✅ Tabela `URL | title | długość | description | długość` dla wszystkich stron PL; 100% w limitach.

**T-16 · Wersje językowe tytułów — frazy natywne**
- EN: „boutique hotel in Katowice city centre”, „hotel near Katowice train station”, „hotel with jacuzzi Katowice”.
- DE: „Boutique-Hotel Kattowitz Zentrum”, „Hotel am Bahnhof Kattowitz”, „Hotel mit Whirlpool Kattowitz”.
- CS: „hotel Katovice centrum”, „ubytování Katovice u nádraží”.
- UK: „готель Катовіце центр”. ES: „hotel boutique Katowice centro”. IT: „hotel boutique Katowice centro”. ZH: „卡托维兹 市中心 酒店”.
- ✅ Tabela tytułów 8 języków; native check przez tłumacza lub LLM z prośbą o naturalność (raport).

**T-17 · Nagłówki H1–H3**
- Jedno H1 na stronę, zgodnie z polityką „hotel” (pkt 1).
- H1 strony głównej: `h1-eyebrow` „Butikowy hotel · Katowice centrum” + `h1-main` „Pokoje i apartamenty w Zielonej Kamienicy”.
- H1 SPA: „Hotel z jacuzzi i sauną w centrum Katowic” (tu słowo hotel jest naturalne i potrzebne — font jak pozostałe H1).
- H1 lokalizacji: „5 minut od dworca — nocleg w centrum Katowic”.
- H1 pokoi: „Pokój Classic 20–22 m² w centrum Katowic” (analogicznie).
- H2 niosą frazy poboczne („Śniadanie w cenie lub na miejscu”, „Parking na dziedzińcu”, „Dojście z dworca PKP”).
- Nagłówki stopki i ustawień prywatności → nie H2 (zwykły tekst lub `aria-label`).
- ✅ Raport drzewa nagłówków dla 10 stron; brak przeskoków poziomów.

**T-18 · Adresy URL**
- Zostaw obecne PL slugi (są dobre, zmiana kosztowałaby pozycje). Nie zmieniaj `/pl/wellness-spa/` — wzmacniasz ją treścią (T-27).
- Nowe strony z T-28 – T-33: krótkie slugi z frazą, np. `/pl/nocleg-przy-dworcu/`, `/pl/pobyt/dla-par/`, `/pl/pobyt/z-psem/`, `/pl/apartamenty-rodzinne/`.
- ✅ Brak polskich znaków w slugach, brak wielkich liter, max 4 słowa.

---

## D. DANE STRUKTURALNE (JSON-LD)

**T-19 · Encja `Hotel` (jedna, wspólna dla całego serwisu)**
- Zamień `LodgingBusiness` na `Hotel`, `@id: https://hornigold.pl/#hotel`.
- Pola: `name`, `alternateName` („Hornigold Katowice”, „Zielona Kamienica Hornigold”), `description`, `url`, `logo`, `image[]` (min. 6 zdjęć 1200 px), `telephone`, `email`, `address` (z `postalCode: 40-064`, `addressRegion: śląskie`), `geo` (50.254591, 19.0163037), `hasMap` (URL Google Maps), `checkinTime: 14:00`, `checkoutTime: 12:00`, `priceRange` („380–1100 PLN” lub zgodnie z faktami), `currenciesAccepted: PLN`, `paymentAccepted`, `petsAllowed: true` (jeśli confirmed), `amenityFeature[]` (`LocationFeatureSpecification`: Sauna, Jacuzzi, Masaż, Wi-Fi, Parking, Śniadanie płatne, Klimatyzacja tylko jeśli confirmed), `numberOfRooms`, `availableLanguage`, `starRating` (tylko jeśli kategoryzacja potwierdzona dokumentem), `sameAs[]` (Google Maps CID, Booking, Tripadvisor, Expedia, Facebook, Instagram, LinkedIn), `parentOrganization` → spółka.
- ✅ Rich Results Test + Schema Markup Validator: 0 błędów, 0 ostrzeżeń krytycznych.

**T-20 · Organizacja (spółka)**
- `Organization` z `legalName`, `taxID`/`vatID`, `address`, `logo`, `sameAs` (LinkedIn). Dane z faktów.
- ✅ Walidacja.

**T-21 · Pokoje: `HotelRoom` + `Offer`**
- Na każdej karcie pokoju: `HotelRoom` (`name`, `description`, `image[]`, `floorSize` {value, unitCode: MTK}, `occupancy` {maxValue}, `bed` (`BedDetails`: typ, liczba), `amenityFeature[]`), `containedInPlace` → `#hotel`.
- `Offer` z ceną „od” (`price`, `priceCurrency: PLN`, `availability`, `url` do rezerwacji, `priceValidUntil` jeśli wymagane).
- Na `/pl/pokoje/`: `ItemList` 9 pokoi.
- ✅ Walidacja dla 9 kart.

**T-22 · `FAQPage`, `BreadcrumbList`, `Article`**
- FAQ: tylko pytania widoczne na stronie, odpowiedzi identyczne z treścią.
- Breadcrumb: pełna ścieżka (Hotel Hornigold › Pokoje › Classic).
- Przewodniki: `Article` (`headline`, `author: Organization Hornigold`, `datePublished`, `dateModified`, `image`).
- ✅ Walidacja.

**T-23 · Usługi i wydarzenia**
- SPA: `Service` / `offers` z cenami (sauna 90 zł/h, jacuzzi 150 zł 1. h + 100 zł kolejna, masaż od 200 zł).
- Sale: `MeetingRoom` (pojemności tylko confirmed).
- Śniadania: `Offer` 60 zł / os., `hoursAvailable` 07:00–10:00.
- ✅ Walidacja.

**T-24 · Spójność schema ↔ treść ↔ Google**
- Każda wartość w JSON-LD musi być widoczna na stronie lub w pliku faktów. Telefon, adres, nazwa identyczne jak w wizytówce Google.
- ✅ Skrypt porównujący pola schema z `hotel-facts.json` — 100% zgodności.

---

## E. TREŚĆ I STRONY POD INTENCJE

Standard każdej strony sprzedażowej: **prawdziwe zdjęcia (min. 4), konkret (liczby, ceny, czasy), sekcja FAQ (3–6 pytań), CTA „Sprawdź dostępność”, telefon, 1 link do przewodnika, 2–3 linki do pokoi**. Ton: ciepły, butikowy, bez przymiotnikowej waty.

**T-25 · Strona główna 900–1200 słów (bez zaśmiecania pierwszego ekranu)**
- Pierwszy ekran: H1 wg pkt 1, formularz, telefon — bez zmian.
- Zaraz pod formularzem: **prawdziwe zdjęcie hotelu** (fasada z bluszczem / dziedziniec). Moduł „32 ilustracje” przenieś niżej (po sekcji pokoi).
- Nowa sekcja „Dlaczego Zielona Kamienica” — 5 kafli: 5 min od dworca · stuletnia kamienica z bluszczem (rok tylko confirmed) · prywatne SPA z jacuzzi i sauną · apartamenty do 105 m² · 4,6/5 w Google (z datą odczytu, link do opinii).
- Sekcja pokoi: wszystkie 9 kategorii (karuzela/siatka z filtrem Pokoje / Apartamenty).
- Sekcja „Najczęstsze pytania” (6) + `FAQPage`.
- ✅ Liczba słów, zrzut ekranu mobile/desktop, Lighthouse bez spadku.

**T-26 · Karty 9 pokoi: 300–450 słów unikalnej treści każda**
- Usuń zdania-szablony („Układ łóżek: Jedno łóżko podwójne…”, „Te parametry pomagają wybrać…”).
- Struktura: „W skrócie” (m², osoby, łóżka, łazienka, cena od) → opis wnętrza (co widać na zdjęciach) → dla kogo → wyposażenie (ikony) → zasady (dostawka, łóżeczko, zwierzęta) → 3 pytania FAQ → porównaj z 2 innymi kategoriami → CTA.
- Alt zdjęć opisowy (co widać + kategoria + „Katowice”).
- ✅ Podobieństwo tekstu między kartami < 30%.

**T-27 · Wellness i SPA: 700–900 słów**
- Dziś ~130 słów. Dodaj: opis strefy (na wyłączność dla gości jednego pokoju), cennik w tabeli, jak zarezerwować, godziny (confirmed), co zabrać, pakiet dla par (tylko confirmed), 6 zdjęć, FAQ (5), link do pokoi z wanną/apartamentów.
- ✅ Strona wchodzi do TOP 10 na „hotel z jacuzzi katowice” w ciągu 8–12 tygodni (pomiar GSC).

**T-28 · Nowa strona: „Nocleg przy dworcu PKP Katowice”** (`/pl/nocleg-przy-dworcu/` + 7 języków)
- Trasa krok po kroku (już jest wirtualny spacer — wykorzystaj), czas dojścia, bagaż, winda (confirmed), parking dla przyjeżdżających autem, przewozy z lotnisk. 600–800 słów.

**T-29 · Nowa strona: „Nocleg blisko Spodka, MCK i NOSPR”** (rozbuduj `/pl/pobyt/wydarzenie/`)
- Odległości i czasy dojścia, plan powrotu po koncercie, późne zameldowanie (confirmed), sekcja „Nadchodzące wydarzenia” (lista ręcznie aktualizowana z linkami do organizatorów, bez kopiowania ich treści). 700–900 słów.

**T-30 · Nowa strona: „Pobyt dla par / romantyczny weekend”**
- Jacuzzi na wyłączność, apartamenty z charakterem, kolacja w okolicy (Śląska Prohibicja tylko po zgodzie Kamila), plan wieczoru. 600–800 słów.

**T-31 · Nowa strona: „Apartamenty rodzinne i dla grup”**
- Apartament Hornigold 105 m², Prestige, Apartament Deluxe — porównanie w tabeli (osoby, sypialnie, łazienki, aneksy), dostawki, łóżeczka (confirmed), parking. 600–800 słów.

**T-32 · Nowa strona: „Pobyt z psem w centrum Katowic”**
- Zasady i opłata (confirmed), parki w pobliżu (Park Kościuszki, Dolina Trzech Stawów — dystanse), co zabrać. 500–700 słów.

**T-33 · „Dla firm” i „Konferencje” — jedna mocna strona B2B lub dwie powiązane**
- Faktura VAT, dłuższe pobyty, sale (nazwy i metraże; pojemność tylko confirmed), catering, formularz zapytania B2B. 700–900 słów.

**T-34 · Przewodniki po mieście (ok. 30 stron) — audyt jakości**
- Każdy przewodnik: data aktualizacji, autor (Zespół Hornigold), źródła oficjalne, unikalne zdjęcia lub zdjęcia z licencją (oznaczone), blok „Nocuj w centrum — Hornigold” z linkiem do pokoi.
- Strony < 300 słów i bez unikalnej wartości → połącz z pokrewnymi (301) lub rozbuduj.
- ✅ Lista przewodników z liczbą słów i decyzją (zostaje / rozbudowa / scalenie).

---

## F. LINKOWANIE WEWNĘTRZNE I NAWIGACJA

**T-35 · Menu główne (wszystkie języki)**
- Pokoje · Wellness & SPA · Lokalizacja · Katowice · Dla firm · Kontakt + przycisk „Sprawdź dostępność”.
- ✅ Każda strona sprzedażowa osiągalna w ≤ 2 kliknięciach od strony głównej.

**T-36 · Linki kontekstowe**
- Z każdego przewodnika min. 2 linki do stron sprzedażowych (anchor opisowy, nie „kliknij tutaj”).
- Z każdej strony pokoju: link do SPA, lokalizacji, śniadań.
- ✅ 0 stron osieroconych (bez linków przychodzących); raport liczby linków wewnętrznych do top 15 stron.

**T-37 · Okruszki widoczne na wszystkich podstronach** (zgodne z `BreadcrumbList`).

**T-38 · Stopka NAP + linki**
- „Hornigold w Zielonej Kamienicy — butikowy hotel · ul. Mikołaja Kopernika 6, 40-064 Katowice · tel. … · office@hornigold.pl” + dane spółki + linki do social media + link „Zobacz opinie w Google”.

---

## G. WYSZUKIWARKI AI

**T-39 · `llms.txt` i `/llms/{lang}.txt` jako karta faktów**
- Dziś to tylko lista języków. Każdy plik językowy: krótki opis, adres, telefon, e-mail, dojazd (5 min od dworca), 9 kategorii (m², osoby, cena od), śniadanie (60 zł, 7:00–10:00), SPA (ceny), parking, zwierzęta, zameldowanie/wymeldowanie, linki do najważniejszych stron, data aktualizacji. Wyłącznie `confirmed`.
- Nagłówek `Content-Type: text/plain; charset=utf-8`.
- ✅ Plik czytelny, ≤ 2 000 słów na język.

**T-40 · Roboty AI**
- `robots.txt`: pozwól GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, ClaudeBot, Google-Extended, Applebot-Extended (decyzja Kamila: widoczność w AI = tak).
- ✅ Wpis w robots i test dostępności stron dla tych user-agentów (status 200).

**T-41 · Treści odpowiadające wprost na pytania**
- W każdym FAQ i na stronach intencyjnych pierwsze zdanie odpowiedzi = pełna odpowiedź (np. „Tak, Hornigold ma prywatne jacuzzi na wyłączność — 150 zł za pierwszą godzinę.”). AI cytuje takie zdania.
- ✅ Lista 30 pytań gości z odpowiedziami jednozdaniowymi.

**T-42 · Spójność faktów w sieci**
- Lista rozbieżności do poprawy przez Kamila (Booking „Hornigold Euroresidence”, agregator „ohotel.com.pl”, Facebook „Hornigold Apartamenty Katowice”, Tripadvisor) — Codex przygotowuje tabelę: serwis | co jest | co powinno być | link do edycji.

---

## H. KONWERSJA I REZERWACJA BEZPOŚREDNIA

**T-43 · Przekaz „rezerwuj bezpośrednio”** — sekcja z korzyściami **tylko confirmed** (np. najlepsza cena, elastyczne warunki, bezpośredni kontakt z recepcją). Bez obietnic, których nie ma w faktach.
**T-44 · Przycisk „Sprawdź dostępność”** przyklejony na dole ekranu na mobile (nie zasłania treści; zamykany).
**T-45 · Formularz zapytania** (kontakt, B2B, grupy) — realna wysyłka (endpoint/serverless), honeypot/Turnstile, zgoda RODO, potwierdzenie na e-mail, kopia do office@hornigold.pl.
**T-46 · Telefon i WhatsApp** klikalne (`tel:`, `https://wa.me/` jeśli Kamil poda numer).
**T-47 · Zaufanie** — moduł opinii: ocena Google z datą i linkiem, 3–6 cytatów **wyłącznie za zgodą autorów lub z oznaczeniem źródła i datą** (bez `aggregateRating` z Google).
**T-48 · Szybkość ścieżki rezerwacji** — z karty pokoju do KWHotel w 1 kliknięciu, przekazanie dat/gości w parametrach (jeśli KWHotel to obsługuje).
- ✅ Dla H: zdarzenia mierzone w J; test ścieżki na iPhone i Android.

---

## I. DOSTĘPNOŚĆ I ZGODNOŚĆ

**T-49 · WCAG 2.2 AA** — kontrast ≥ 4,5:1, focus widoczny, nawigacja klawiaturą (menu, galerie, FAQ `<details>`), cele dotykowe ≥ 44×44 px, `alt` opisowe, etykiety pól.
**T-50 · Deklaracja dostępności** (strona) — opis udogodnień obiektu (winda, wejście od dziedzińca — confirmed) i strony.
**T-51 · Polityka prywatności i cookies** — administrator: spółka z faktów, Consent Mode v2, rejestr zgód; analityka i mapy dopiero po zgodzie.
**T-52 · Regulaminy** — pobyt, rezerwacja i anulacja, zwierzęta, sprzedaż usług — aktualne PDF/HTML od Kamila; dane sprzedawcy w stopce.
**T-53 · AI Act / przejrzystość** — oznaczenie ilustracji generowanych przez AI (już jest) i — jeśli zostanie wdrożony asystent AI — informacja, że rozmowa jest z AI.
- ✅ axe DevTools / WAVE: 0 błędów krytycznych na 10 stronach.

---

## J. POMIAR I ANALITYKA

**T-54 · GA4 przez Google Tag Manager** z Consent Mode v2.
**T-55 · Zdarzenia:** `begin_booking` (klik „Sprawdź dostępność”/przejście do KWHotel), `click_phone`, `click_email`, `click_whatsapp`, `form_submit`, `view_room` (z nazwą kategorii), `spa_interest` (klik w cennik SPA), `language_switch`.
**T-56 · Śledzenie przejścia do KWHotel** — cross-domain lub parametr źródła; jeśli KWHotel pozwala, konwersja `purchase` z wartością.
**T-57 · UTM** dla: Google Business Profile (strona i przycisk rezerwacji), Instagram (bio), Facebook, newsletter, kampanie.
**T-58 · Raport miesięczny** (Looker Studio lub plik): ruch organiczny per język, top frazy z GSC, kliknięcia do rezerwacji, CTR, pozycje 20 fraz (lista w pkt 3).

---

## K. WIDOCZNOŚĆ LOKALNA I MODUŁ HOTELI GOOGLE `[KAMIL]` (Codex przygotowuje instrukcje i teksty)

**T-59 · Google Hotel Center + darmowe linki do rezerwacji** — połączenie przez KWHotel (partner integracyjny Google). Efekt: w module hoteli pojawia się „Oficjalna strona” z Twoją ceną obok Bookingu (dziś Google pokazuje tylko Booking 867 zł).
**T-60 · Parytet cen** — cena bezpośrednia ≤ cena w OTA dla tych samych warunków; sprawdzenie, skąd w Bookingu 867 zł.
**T-61 · Wizytówka Google:** kategoria główna „Hotel”, dodatkowe trafne; opis 750 znaków z frazami; udogodnienia zgodne z prawdą (usuń „Basen”, śniadanie płatne); logo, okładka, ≥ 30 nowych zdjęć; link strony z UTM; posty co tydzień; Pytania i odpowiedzi.
**T-62 · Odpowiedzi na wszystkie opinie** (paczka `paczka-codex-opinie-hornigold.zip`) — tempo ≤ 20/dzień.
**T-63 · Pozyskiwanie nowych opinii** — e-mail/SMS po wymeldowaniu z linkiem do opinii Google (bez zachęt finansowych, bez filtrowania tylko zadowolonych).
**T-64 · Spójność NAP** w: Booking, Expedia/Hotels.com, Tripadvisor, Kayak, Trivago, Agoda, Facebook, Apple Maps (Business Connect), Bing Places, Panorama Firm, Zumi, Targeo — identyczna nazwa, adres, telefon, link.
**T-65 · Usunięcie/zgłoszenie błędnych wpisów** (agregatory z nazwą „Euroresidence”, „Aparthotel”).
**T-66 · Apple Maps i Bing Places** — założenie/zweryfikowanie profili.

## L. AUTORYTET I LINKI ZEWNĘTRZNE `[KAMIL]`

**T-67 · 15–20 wartościowych linków lokalnych w 90 dni:** portale turystyczne Katowic i Śląska, katalogi hoteli z redakcją, partnerzy (organizatorzy wydarzeń, restauracje, uczelnie — oferty dla gości), blogi podróżnicze (współprace oznaczone).
**T-68 · Historia kamienicy jako materiał PR** — artykuł z archiwalnymi zdjęciami (confirmed) dla mediów lokalnych.
**T-69 · Profile marki** — spójne nazwy kont: Instagram, Facebook (zmiana nazwy „Hornigold Apartamenty Katowice” → „Hornigold w Zielonej Kamienicy”), LinkedIn, TikTok.
**T-70 · Wzmocnienie marki „Hornigold Katowice”** — zawsze w parze z „Katowice” lub „w Zielonej Kamienicy”, by odróżnić od „Benjamin Hornigold” w wynikach wyszukiwania marki.

---

## 3. FRAZY DO MONITOROWANIA (raport co 2 tygodnie)

| Fraza | Dziś (03.11.2026) | Cel 3 mies. | Cel 12 mies. |
|---|---|---|---|
| hornigold katowice | #3 | #1 | #1 |
| hornigold | poza TOP 10 | TOP 5 | TOP 3 |
| zielona kamienica katowice | #6 (tytuł DE) | TOP 3 (tytuł PL) | #1 |
| hotel z jacuzzi katowice | poza TOP 20 | TOP 10 | TOP 3 |
| hotel blisko dworca katowice | poza TOP 20 | TOP 10 | TOP 3 |
| hotel butikowy katowice | poza TOP 10 | TOP 5 | TOP 3 |
| nocleg spodek katowice | brak danych | TOP 10 | TOP 3 |
| apartamenty katowice centrum | poza TOP 20 | TOP 20 | TOP 10 |
| noclegi katowice centrum | poza TOP 20 | TOP 20 | TOP 10 |
| hotel katowice centrum | poza TOP 30 | moduł hoteli TOP 3 | organicznie TOP 10 |
| hotel katowice | poza TOP 30 | moduł hoteli widoczny z ceną oficjalną | organicznie TOP 20 |
| + odpowiedniki EN / DE / CS | — | pomiar | TOP 10 |
Prognozy — zależą od tempa wdrożenia, opinii, cen i działań K–L.

---

## 4. KOLEJNOŚĆ I HARMONOGRAM

| Tydzień | Zadania |
|---|---|
| 1 | T-01 – T-13 (technika + indeksacja), T-59/T-60/T-61 instrukcje dla Kamila |
| 2 | T-14 – T-18 (tytuły, opisy, H1 wg polityki „hotel”) |
| 3 | T-19 – T-24 (schema) |
| 3–5 | T-25 – T-27 (strona główna, pokoje, SPA) |
| 5–7 | T-28 – T-34 (strony intencyjne, przewodniki) |
| 7 | T-35 – T-42 (linkowanie, AI) |
| 8 | T-43 – T-58 (konwersja, dostępność, analityka) |
| stale | T-62 – T-70 (opinie, NAP, linki, marka) |

## 5. DEFINICJA UKOŃCZENIA PROJEKTU
- Kategorie A–J: wszystkie kryteria akceptacji spełnione, raporty oddane.
- Crawl końcowy: 0 błędów 4xx/5xx, 0 duplikatów title/description, 0 błędów hreflang, 0 błędów schema.
- Lighthouse mobile ≥ 95/98/100/100 na 6 stronach testowych.
- GSC: ≥ 90% adresów z mapy zaindeksowanych.
- Tabela fraz z pkt 3 zaktualizowana i przekazana Kamilowi.
