# Gotowość wydania 23.11 — 11.10.2026

Ten dokument opisuje bieżące przygotowanie. Wdrożenie produkcyjne wymaga publicznego potwierdzenia; push nie jest takim dowodem. Poprzednie dokumenty są archiwum w docs/implementation, bez zastosowania starych migracji.

| Wymaganie | Status | Dowód | Właściciel | Blocker |
|---|---|---|---|---|
| SEO 693 tras / 7 języków | GOTOWE LOKALNIE | docs/seo/audit-preview.json, audit-production-ready.json | wykonawca | publikacja właściwym pipeline |
| Canonicale, hreflang, sitemap, robots | PRZYGOTOWANE DO PRODUKCJI | scripts/seo.py i pełny audyt | Marek | konto i konfiguracja Workera |
| Preview noindex / brak pomiaru i transakcji | GOTOWE LOKALNIE | audyt preview i testy GA4 | wykonawca | brak |
| Schema na podstawie dossier | GOTOWE LOKALNIE | content/verified-facts-2026-10-11.json | wykonawca | ImageObject/prawa i niepotwierdzone pola wyłączone |
| Search Console | częściowo POTWIERDZONE ZEWNĘTRZNIE | własność potwierdzona, PL/EN zaindeksowane, GSC–GA4 połączone | Google / wykonawca | pierwszy odczyt sitemapy nieudany; obserwacja 12.10 |
| GA4 / zgody | GOTOWE LOKALNIE; konto POTWIERDZONE | testy browser i lifecycle, odczyt Google | wykonawca | odbiór zdarzeń po wdrożeniu |
| Mobile, CLS, obrazy | GOTOWE LOKALNIE w zakresie testów | docs/implementation/evidence | wykonawca | rzeczywiste CWV i prawa do obrazów WYMAGAJĄ POTWIERDZENIA |
| Rezerwacje / płatności | WYMAGA POTWIERDZENIA | istniejący odnośnik GuestSage; uczciwe dokumenty 7 języków | recepcja / dostawcy | aktualna usługa, sandbox, taryfy, PMS, potwierdzenia |
| Uprawnienia i nowe koszty | WYMAGA ZEWNĘTRZNEJ DECYZJI | REGISTER.json | Kamil | osobna decyzja jeśli wystąpi potrzeba |

Szczegółowy rejestr wszystkich 34 punktów: docs/implementation/REGISTER.md i REGISTER.json. Nie migruj historycznej strony, danych ani przekierowań. REDIRECT_MAP_DRAFT.csv jest dawnym archiwum, nie materiałem do wdrożenia.
