# Ochrona rezerwacji i Fiserv

Polecenie właściciela z 11.10.2026: istniejący moduł rezerwacji i bramka Fiserv są nietykalne. Nie zmieniać kodu, konfiguracji, powiązań ani wspólnych zasobów wpływających na te integracje bez nowego wyraźnego polecenia. Nie zastępować produkcji pełnym buildem podglądu.

## Lokalna kontrola plików

`scripts/check_protected_integrations.py` nie wdraża zmian, nie wykonuje transakcji i nie zapisuje zawartości plików. Manifest SHA-256 musi znajdować się poza drzewem źródeł, aby nie trafił do repozytorium. Narzędzie odmawia zastąpienia istniejącego manifestu. Sprawdza zmiany, usunięcia i dodane pliki w wskazanych katalogach; odrzuca symlinki i wyjścia poza katalog źródeł.

Marek musi najpierw wskazać rzeczywisty katalog produkcji oraz kompletną listę chronionych ścieżek, w tym wspólne zasoby i lokalną konfigurację. Nie znamy pełnej listy; brak plików Fiserv w tym checkoutie nie oznacza ich ochrony na produkcji.

Przykładowa składnia (nazwy w nawiasach są miejscami do zastąpienia, nie istniejącymi ścieżkami Hornigold):

```text
python3 scripts/check_protected_integrations.py capture --root <katalog-źródeł-produkcji> --manifest <zewnętrzny-prywatny-manifest.json> --protect <plik-rezerwacji> --protect <katalog-Fiserv> --protect <wspólne-zasoby>
python3 scripts/check_protected_integrations.py check --root <katalog-źródeł-produkcji> --manifest <ten-sam-manifest.json>
```

Zabezpieczyć manifest przed zmianą razem z kopią sprzed wdrożenia. Wynik niezerowy zatrzymuje przygotowanie publikacji; nie wolno po błędzie przechwycić nowego stanu jako rzekomej niezmienionej bazy. Ustalić przyczynę bez modyfikowania integracji.

## Granice dowodu

Zgodność hashy dowodzi jedynie zgodności bajtów wskazanych plików. Nie obejmuje nieujętych ścieżek, zmian konfiguracji Cloudflare, sekretów środowiskowych, DNS, usług dostawcy, aktywnych sesji, transakcji i działania PMS. Te elementy pozostają osobnymi kontrolami właściciela wdrożenia. Narzędzie nie uruchamia się automatycznie w pipeline; pipeline i lista chronionych elementów muszą być potwierdzone przez Marka.

Testy lokalne używają wyłącznie syntetycznych plików. Nie są odbiorem rezerwacji lub płatności.
