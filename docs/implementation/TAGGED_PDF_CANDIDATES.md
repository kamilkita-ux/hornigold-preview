# Lokalne kandydaty PDF ze strukturą

Stan: przygotowanie, nie publikacja. Generator `scripts/build_tagged_legal_candidates.py` zapisuje wyłącznie osobny katalog kandydatów; nie zmienia `site/`, rezerwacji ani Fiserv. Źródła: zatwierdzone `legal/*.json` i `content/property-identity.json`.

21 dokumentów / 7 języków: pakiet dokumentów oraz pełne i dziecięce standardy. Kontrola dokładnej treści Poppler: zero brakujących elementów; nagłówek H1, listy LI i język dokumentu sprawdzone. Poprawiono mapowanie stylu nagłówka Writer/Web do H1 oraz język katalogu PDF. Czcionki pochodzą z `legal/fonts` przez lokalny FONTCONFIG_FILE, bez instalacji systemowej. pypdf przestawia część chińskiej interpunkcji przy ekstrakcji; nie pominięto tych różnic — zastosowano niezależną ekstrakcję Poppler layout.

Wyrenderowano 127 stron i przejrzano arkusze wszystkich języków. Do poprawy: pakiet chiński ma stronę z samymi źródłami. Wymagane jeszcze: ostateczny świeży build generatora, ponowna kontrola układu, struktury linków i kolejności czytania, zgodna informacja HTML/PDF o dostępności przed ewentualną podmianą. Nie potwierdzono PDF/UA, PAD ani całej ścieżki rezerwacji.

Uruchomienie: Python z pypdf 6.20.0, `--soffice` (lokalny LibreOffice), `--pdftotext` (Poppler), `--output` (nowy katalog poza site/). Nie ma automatycznego kopiowania do opublikowanych dokumentów.

## Aktualizacja kontroli
Świeży build generatora: 21/21, tekst źródłowy kompletny, wszystkie czcionki osadzone. Audyt struktury potwierdził zgodność MCID z treścią stron i kolejnością odwołań oraz powiązania wszystkich linków; zero błędów. Cztery kontrolowane uszkodzenia zostały wykryte. Poprawiono odstępy pod nagłówkami i układ chińskich źródeł; sprawdzono stronę chińską z nagłówkiem prywatności w pełnym rozmiarze. Dowód: evidence/tagged-pdf-candidates-23.18.json.

Do adopcji: zaktualizować informację o znacznikach w akapicie accessibility we wszystkich 7 JSON-ach, jednocześnie wygenerować końcowe HTML/PDF, ponownie przejrzeć finalne arkusze stron, wykonać build i regresję, dopiero potem podmienić istniejące nazwy PDF. PDF/UA i pełny odbiór czytnikiem pozostają niepotwierdzone.

## Adopcja lokalna 23.18 (12 października 2026)
21 oznaczonych dokumentów zastąpiło lokalne pliki w `site/documents/`; opisy accessibility w 7 JSON-ach i HTML zostały zsynchronizowane. Kontrola struktury i tekstu: zero błędów. Przejrzano 124 strony finalnego układu, w tym oba pełne obrazy poprawionego dokumentu chińskiego. W starszym generatorze dodano odmowę nadpisania oznaczonych PDF-ów. Dowód: `evidence/tagged-pdf-adoption-23.18.json`. 23.18 opublikowano na obu podglądach; 693 trasy na każdym bez błędów, 42 publiczne kopie PDF zgodne z zatwierdzonymi hashami. Produkcja nadal 23.11. Odbiór czytnikiem ekranu i PDF/UA pozostają niepotwierdzone.

Kontrola przed publikacją: Pages i quality uruchamiają audyt 21 nazwanych PDF z kontrolą struktury, języka, nagłówka, list, kolejności, odwołań i czcionek. 6 testów pozytywnych/negatywnych korzysta wyłącznie z jednorazowych kopii; łącznie 36 testów przeszło.
