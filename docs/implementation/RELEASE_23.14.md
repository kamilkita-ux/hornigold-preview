# Hornigold 23.14 — dane zdjęć i aktualny rejestr

Przygotowanie: `codex/cloudflare-production-seo-20261009`; publikacja GitHub: `kamilkita-ux/hornigold-preview`, `main`. Istniejący projekt Sites pozostaje bez zmian tożsamości, odbiorców i D1.

Dodano ImageObject dla istniejących obrazów w głównej treści: tylko URL pliku i opis alt. Bez twierdzeń o autorstwie, licencji, własności praw lub kwalifikacji do wyników rozszerzonych. Audyt porównuje każdą encję ze źródłowym obrazem i istniejącym plikiem; wyklucza ukryte obrazy, puste alty, duplikaty, pliki zewnętrzne i wyjście poza katalog assets. Informacje o prawach nadal wymagają odrębnych źródeł.

Uzupełniono rejestr o publikację 23.13, potwierdzoną kopię/odtworzenie i przegląd publicznego GuestSage. Opisy obiektu widoczne po polsku nie zostały pokazane w sprawdzonych wersjach EN/DE; nie jest to pełny test silnika ani potwierdzenie obsługi siedmiu języków.

Weryfikacja: build preview oraz lokalny production-ready, audyt 693 tras każdego artefaktu, 1911 encji na 546 stronach w każdym artefakcie. Ostateczne wyniki są zapisane w evidence/seo-*-image-schema.json i evidence/image-schema-*.json.

Zachowano noindex, Disallow i brak aktywnego pomiaru podglądów. Nie wdrażano na hornigold.pl, nie uruchamiano rezerwacji, płatności ani nowego trackingu. Produkcja ostatnio potwierdzona jako 23.11. Zmiany Marka i pierwotny brudny checkout pozostają zachowane.
