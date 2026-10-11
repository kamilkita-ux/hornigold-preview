# Hornigold 23.13 — 11.10.2026

Repozytorium: kamilkita-ux/hornigold-preview. Przygotowanie: codex/cloudflare-production-seo-20261009. Cel publikacji: main. Potwierdzony workflow main publikuje GitHub Pages; automatyzacja Cloudflare nadal wymaga wskazania przez Marka.

Zmiany:
- Stopka wszystkich 693 tras pokazuje pełny numer release.json i datę wydania, również w tytule dostępnym dla narzędzi asystujących.
- Kliknięcia rzeczywistych linków Instagram/Facebook/LinkedIn działają z www i bez www; podszywające się domeny nie są zaliczane.
- Referrer pomiarowy ma jawną listę znanych domen; pozostałe, ścieżki i parametry nie są przesyłane przez własny pomiar.
- Celowany override esbuild 0.25.12: audyt pnpm 0 podatności; rzeczywiste generowanie migracji w izolacji zachowuje identyczny SQL.
- Aktualny rejestr i panel odzwierciedlają produkcję 23.11, odbiór kontrolowanego testu GA4 oraz inspekcję siedmiu stron głównych w GSC.

Dowody: evidence/node-tests-23.13.txt (48/48), testy Python (10/10), evidence/dependency-compat-23.13.json, evidence/dependencies-23.13.json, evidence/seo-preview-23.13.json, evidence/seo-production-23.13.json, evidence/static-23.13.json. Wszystkie audyty obejmują 693 trasy; 0 błędów. GA4 i GSC: evidence/ga4-live-receipt-2026-10-11.json i evidence/gsc-seven-languages-2026-10-11.json.

## Pozostałe zależności

- Marek: rzeczywisty Worker/konto/build/pipeline/rollback, kopia konfiguracji i bazy; minimalna poprawka 403/503 z 23.12 oraz zachowanie jego booking.js i rozszerzeń .booking-panel.
- Recepcja/dostawcy: faktycznie zakupiony PMS, GuestSage i operator płatności, sandbox, potwierdzenia językowe, room type IDs, bieżące warunki taryf i odbiór zapytania.
- Właściciel: udokumentowane prawa do zdjęć, rozbieżny aktywny Instagram i formalna klasyfikacja/kategoria profilu; bez tych danych nie dopisujemy niepotwierdzonych twierdzeń.
- Google: indeksacja zgłoszonych zh-Hans/UK i ponowny odczyt sitemapy (obserwacja 12.10). PL/EN/DE/ES/IT: strony główne w indeksie, nie wszystkie podstrony.
- Monitoring: pierwszy zaplanowany przebieg 12.10 07:30; rzeczywiste doręczenie alarmu wymaga potwierdzenia. Dashboard zawiera manualne, jawnie datowane dane — nie udaje automatycznego źródła przychodów.
- Dostępność: dostępny HTML równoważny PDF, automatyczne kontrole zaliczone; manualny odbiór i przyszły checkout dostawcy nadal potrzebne.

Nie wykonano rzeczywistej rezerwacji ani płatności. Kopia źródeł nie jest kopią konfiguracji/bazy Cloudflare. Publikacja podglądów nie oznacza wdrożenia produkcji. Stan podglądów: noindex/nofollow/noarchive, Disallow /, brak aktywnej analityki.
