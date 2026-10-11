import assert from "node:assert/strict";
import test from "node:test";
import { firstRedirect, isBookingPage, nextReleaseTag, parseArgs, pickActiveVersion, reviewChanges, robotsMeta } from "../scripts/cloudflare-release.mjs";

test("strony z blokami rezerwacji — tylko te konflikty rozwiązywane automatycznie", () => {
  for (const path of ["site/pl/index.html", "site/zh-hans/pobyt/index.html", "site/de/rezerwacja/index.html"]) assert.ok(isBookingPage(path), path);
  for (const path of ["site/pl/pokoje/index.html", "server/worker.mjs", "site/assets/booking.js", "site/pl/rezerwacja/regulamin/index.html"]) assert.ok(!isBookingPage(path), path);
});

test("domyślnie przegląd origin/main; --candidate dopisuje origin/", () => {
  assert.equal(parseArgs([]).mode, "review");
  assert.equal(parseArgs([]).candidate, "origin/main");
  const options = parseArgs(["--deploy", "--candidate", "codex/x", "--accept", "csp"]);
  assert.equal(options.mode, "deploy");
  assert.equal(options.candidate, "origin/codex/x");
  assert.deepEqual([...options.accept], ["CSP"]);
  assert.throws(() => parseArgs(["--force"]), /Nieznana opcja/);
});

test("tag z rewizji release.json; kolejne -rN", () => {
  assert.equal(nextReleaseTag(["hornigold-v23.9-cloudflare"], "24.0"), "hornigold-v24.0-cloudflare");
  assert.equal(nextReleaseTag(["hornigold-v23.9-cloudflare", "hornigold-v23.9-cloudflare-seo"], "23.9"), "hornigold-v23.9-cloudflare-r2");
  assert.equal(nextReleaseTag(["hornigold-v23.9-cloudflare", "hornigold-v23.9-cloudflare-r3", "hornigold-v2309-cloudflare-r9"], "23.9"), "hornigold-v23.9-cloudflare-r4");
});

test("przegląd: przełączniki właściciela, wrangler.jsonc, migracje i CSP zatrzymują", () => {
  const review = reviewChanges("M\twrangler.jsonc\nM\tdrizzle/0000_quiet_overlord.sql\nA\tdrizzle/0001_new.sql", {
    releaseBefore: { indexing: false, bookingEnabled: false }, releaseAfter: { indexing: false, bookingEnabled: true }, cspChanged: true,
  });
  assert.deepEqual(review.blocks.map((b) => b.code), ["WRANGLER", "MIGRATION_CHANGED", "OWNER_SWITCH", "CSP"]);
  assert.deepEqual(review.newMigrations, ["drizzle/0001_new.sql"]);
});

test("przegląd: dzisiejsza paczka Kamila (social, Search Console, Meta poza site/) przechodzi", () => {
  const review = reviewChanges("A\tcontent/social-channels.json\nA\tintegrations/meta/pixel.js\nM\tscripts/build.py\nA\tsite/google6078b276ecb15bd4.html", {
    releaseBefore: { indexing: false }, releaseAfter: { indexing: false },
  });
  assert.equal(review.blocks.length, 0);
  assert.equal(review.warnings.length, 1);
});

test("meta robots i pierwsze przekierowanie z server/routes.mjs", () => {
  assert.equal(robotsMeta('<meta name="robots" content="index,follow">'), "index,follow");
  assert.equal(robotsMeta('<meta content="noindex" name="robots"/>'), "noindex");
  assert.equal(robotsMeta("<p></p>"), null);
  assert.deepEqual(firstRedirect('export const redirects={\n  "/de/catering/": "/de/catering-und-veranstaltungen/",'), { from: "/de/catering/", to: "/de/catering-und-veranstaltungen/" });
});

test("aktywna wersja Workera", () => {
  assert.equal(pickActiveVersion([{ created_on: "2026-10-09", versions: [{ version_id: "a", percentage: 100 }] }, { created_on: "2026-10-10", versions: [{ version_id: "b", percentage: 100 }] }]), "b");
});
