# Odbiór ręczny — wymagane dowody

Nie jest to potwierdzenie wykonania. Wypełnia tester dla konkretnej wersji, commitu, urządzenia, systemu i czytnika ekranu. Zakres: PL/EN/CS/DE/zh-Hans/UK/ES/IT; strona główna, pokoje i szczegół pokoju, pobyt, lokalizacja, kontakt, dokumenty oraz ustawienia prywatności.

| Scenariusz | Kryterium | Wynik / dowód |
|---|---|---|
| Klawiatura bez myszy | Wszystkie kontrolki osiągalne, logiczny fokus, widoczny fokus, brak pułapki poza modalem | Nie wykonano |
| Czytnik ekranu | Prawidłowe role, etykiety, nagłówki i komunikaty; flagi mają nazwy języków | Nie wykonano |
| Modal zgód | Ogłoszony tytuł, fokus wewnątrz, Escape zamyka i oddaje fokus; osobne wybory nie są domyślnie zaznaczone | Nie wykonano |
| Powiększenie / przełamanie | 200% i 400%, brak utraty treści i poziomego przewijania tekstu | Nie wykonano |
| Osiem języków | Przełącznik zachowuje odpowiednik trasy, chińskie i ukraińskie znaki są czytelne | Nie wykonano |
| Formularze i błędy | Czytelne etykiety, opis wymaganych pól i błędów, brak przekazywania danych bez działania gościa | Nie wykonano |
| PDF | Tytuł, język, kolejność odczytu, nagłówki, listy i linki; porównanie treści z HTML | Nie wykonano |
| Zewnętrzna rezerwacja | Oznaczona granica dostawcy i ograniczenia językowe; dalszy odbiór wyłącznie w uzgodnionym środowisku | Nie wykonano |
| Płatność | Dopiero po uzgodnieniu z operatorem: cena/warunki, obowiązek zapłaty, sukces/odmowa/powrót; bez nieuzgodnionej rzeczywistej transakcji | Nie wykonano |

Każdy błąd: URL i język, kroki odtworzenia, oczekiwane/rzeczywiste zachowanie, zrzut lub nagranie, priorytet i wynik ponownego testu. Automatyczne testy i poprawne znaczniki PDF nie zastępują tego odbioru ani certyfikacji PDF/UA.

## Rozdzielenie dowodów — 15.10.2026

Tabela powyżej dotyczy odbioru ręcznego i pozostaje niewypełniona do faktycznego wykonania. Automatyczne sprawdzenia czeskich tras, ośmiu przełączników języka oraz 24 dokumentów PDF opisano w `evidence/czech-local-acceptance-23.28.json` i `evidence/legal-eight-languages-23.28.json`. Dowody te nie potwierdzają obsługi przez czytnik ekranu ani pełnej ścieżki płatności.
