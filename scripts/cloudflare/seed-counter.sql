-- Jednorazowo przy nowej bazie: licznik od zera z datą startu wdrożenia Cloudflare.
INSERT OR IGNORE INTO site_counters (key, total, started_at) VALUES ('pageviews', 0, '2026-10-07');
