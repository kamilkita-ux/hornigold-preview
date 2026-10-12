# Dane zdjęć w SEO — przygotowanie lokalne, 11.10.2026

Źródło definicji: https://schema.org/ImageObject (odczyt 11.10.2026).

Wpisy powstają wyłącznie z istniejących plików /assets/ użytych przez obrazy w głównej treści strony. Opis jest pobierany z już widocznej dla technologii asystujących alternatywy alt. Obrazy ukryte, dekoracyjne z pustym alt, brakujące, zewnętrzne i ścieżki wychodzące poza katalog assets są pomijane. Powtórzenie tego samego pliku na stronie nie tworzy duplikatu encji.

ImageObject zawiera tylko typ, identyfikator, contentUrl i description. Nie deklaruje autorstwa, licencji, własności praw, oceny, ceny, daty wykonania ani pochodzenia zdjęcia. Ilustracje zachowują istniejący opis ilustracji. Nie są oznaczane jako fotografia dokumentalna. Nie deklarujemy prawa do wyniku rozszerzonego Google.

WebPage odsyła do tych encji przez image. Nie wybieramy sztucznie primaryImageOfPage. Canonical host jest produkcyjny, podobnie jak pozostałe encje SEO; podglądy zachowują noindex i robots Disallow.

Testy obejmują ukrycie, puste alternatywy, duplikaty, zewnętrzne pliki, brakujące pliki i próbę wyjścia poza katalog. Audyt obu artefaktów porównuje każdy wpis z rzeczywiście istniejącym plikiem i obrazem w źródle. Prawa do wykorzystania obrazów nadal wymagają odrębnego dossier właściciela (G5).

Stan: przygotowanie publikacji 23.14. Produkcja pozostaje 23.11 do niezależnego potwierdzenia wdrożenia Cloudflare.

Wynik audytu obu artefaktów: 693 trasy, 546 stron z obrazami, 1911 encji ImageObject, zero błędów. Testy Python: 12/12.
