CREATE TABLE `site_counters` (
	`key` text PRIMARY KEY NOT NULL,
	`total` integer DEFAULT 0 NOT NULL,
	`started_at` text NOT NULL
);
