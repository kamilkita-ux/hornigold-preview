export async function readCount(db) {
  const row = await db.prepare('SELECT total, started_at FROM site_counters WHERE key = ?').bind('pageviews').first();
  return {total: row?.total ?? 0, startedAt: row?.started_at ?? '2026-10-05'};
}
export async function countView(db) {
  const row = await db.prepare("INSERT INTO site_counters (key,total,started_at) VALUES (?,1,?) ON CONFLICT(key) DO UPDATE SET total = total + 1 RETURNING total, started_at").bind('pageviews','2026-10-05').first();
  if (!row || !Number.isSafeInteger(row.total)) throw new Error('Invalid counter result');
  return {total:row.total,startedAt:row.started_at};
}
