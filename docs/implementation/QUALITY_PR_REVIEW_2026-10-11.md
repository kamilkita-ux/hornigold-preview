# Odczyt roboczego PR kontroli jakości

PR: https://github.com/kamilkita-ux/hornigold-preview/pull/2

Odczyt 11.10.2026: OPEN, draft, gałąź `codex/quality-controls-2026-10-11`, commit `1d95a8662b513b972c891bfcd96a9d2c27f64984`. Kontrola quality run `38175917711`: SUCCESS. Nie scalono, nie zmieniono cudzej gałęzi ani ustawień uprawnień. Bieżący main: `a5fdacdfaa6872491911635881f881c576b136ab`.

## Potwierdzone kodem

- Nowe workflow kontrolują PR, poniedziałkowy pełny audyt oraz zakończenie publikacji GitHub Pages; nie wdrażają Cloudflare.
- Odczyt produkcji używa `monitor_public.py`, bez formularzy i transakcji.
- Raporter błędów nie pobiera ani nie wykonuje kodu z błędnej gałęzi. Używa stałego skryptu i deduplikacji otwartego issue według workflow/gałęzi.
- Kontrola błędów nie uruchamia lokalnego Codexa. Wpis issue jest zgłoszeniem, nie rozpoczęciem naprawy.
- Akcje są przypięte do commitów; podstawowe kontrole mają `contents: read`. Raporter deklaruje `issues: write`; nie należy traktować review jako zgody na nowe uprawnienia kont.
- Harmonogram godzinowy pozostaje PAUSED zgodnie z dokumentacją PR. Nie został przeze mnie wznowiony.

## Warunki przed scaleniem

1. Sprawdzić PR względem aktualnego main, nie tylko jego wcześniejszej bazy. Aktualny kod ma nowe testy ImageObject i aktualizację zależności; zielony test dawnego commitu nie dowodzi zgodności nowego zestawu.
2. Uzgodnić wersję pnpm: workflow przypina 10.30.3, lokalny ostatni zweryfikowany build używał 11.25.0. Zweryfikować frozen-lockfile, overrides i brak niezamierzonego wykonywania skryptów instalacyjnych na rzeczywistym merge-commicie. Sama różnica wersji nie dowodzi błędu.
3. Kontrola po publikacji pobiera source z SHA uruchomienia, a `audit_live_release.py` porównuje live revision z lokalnym release.json po pełnym odczycie tras. Nowsza publikacja w trakcie audytu może wywołać fałszywy alarm starszego uruchomienia. Dodać jawny stan „zastąpiona publikacja” po porównaniu oczekiwanego i rzeczywiście wdrożonego artefaktu; nie ukrywać realnych błędów bieżącej wersji. Concurrency redukuje ryzyko, ale nie dowodzi braku okna wyścigu.
4. W quality workflow wykonuje się build production-ready i przygotowanie pakietu lokalnego; nie jest to publikacja. Pakietu nie wolno stosować na produkcji w całości, jeśli narusza chronione integracje. Rezerwacja i Fiserv pozostają nietykalne.
5. Kontrola hashy chronionych elementów wymaga rzeczywistej listy Marka i prywatnego manifestu sprzed pracy. Nie można zastąpić jej sprawdzeniem plików preview.
6. Zachować dowody oraz zweryfikowaną kopię merge-commitu na Mac mini. Przy scaleniu nie cofać zmian main ani nie wykonywać force push.

## Ograniczenia

To lokalny odczyt i przegląd kodu, nie akceptacja PR, aktywacja harmonogramu, potwierdzenie alarmu lub zakończenie punktów I1/I2. Integracja Cloudflare i odbiór rzeczywistego kanału alarmowego pozostają niepotwierdzone. PR nie został przeze mnie skomentowany ani scalony.
