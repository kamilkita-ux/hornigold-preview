import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
export const siteCounters = sqliteTable('site_counters', {
  key: text('key').primaryKey(),
  total: integer('total').notNull().default(0),
  startedAt: text('started_at').notNull(),
});
