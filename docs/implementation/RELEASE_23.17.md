# Wersja 23.17 — rzetelny monitoring HTTPS

Naprawiono raportowanie TLS: nie jest już stałą wartością true. Pozytywny wynik wymaga zakończonego powodzeniem żądania HTTPS z domyślną weryfikacją certyfikatu. Monitor odróżnia błędy transportu, błąd certyfikatu, status HTTP i odpowiedź serwera; obsługuje nagłówki CONNECT proxy. Import modułu nie uruchamia sieci.

24 testy Python zaliczone. Monitor odczytowy produkcji: 10/10; kontrolowana awaria: wykryta, kod 1. Nie jest to prognoza wygaśnięcia certyfikatu ani odbiór transakcji.

Zapisano wynik rzeczywistego testu sitemapy w Google: adres dostępny. Raport przetworzenia mapy nadal wymaga obserwacji. Zachowano źródła i ograniczenia dowodu.

Nie zmieniono aplikacji, serwera, rezerwacji, Fiserv, DNS ani konfiguracji Cloudflare. Podglądy pozostają noindex i bez analityki. Pozostałe zależności 34-punktowego zlecenia zachowano w rejestrze.
