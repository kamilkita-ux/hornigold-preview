#!/usr/bin/env node
// Automatyczne wydanie hornigold.pl na Cloudflare — runbook z docs/CLOUDFLARE.md („Wdrożenie nowej wersji z main")
// zapisany jako kod. Uruchamiać w worktree C:\dev\hornigold-cloudflare na gałęzi deploy/cloudflare.
//
//   node scripts/cloudflare-release.mjs               przegląd: nowe commity z origin/main i wynik kontroli, nic nie zmienia
//   node scripts/cloudflare-release.mjs --deploy      scalenie → build + audyty + testy → deploy → smoke → tag → dziennik
//   node scripts/cloudflare-release.mjs --prepare     scalenie → build + audyty + testy, bez publikacji
//   node scripts/cloudflare-release.mjs --smoke       same testy dymne produkcji
//
// Opcje: --candidate <ref> (zamiast origin/main), --accept CSP,SERVER (świadome przyjęcie po przeglądzie),
// --no-push, --no-rollback.
// Zatrzymuje się na: zmianie wrangler.jsonc, zmianie istniejącej migracji D1, zmianie przełączników właściciela
// w release.json (indexing, bookingEnabled, paymentsEnabled, counterEnabled), zmianie CSP, utracie poprawki
// Windows w scripts/seo.py, konflikcie scalania (poza stronami rezerwacji — te: wersja Kamila + kwhotel_booking_pages.py),
// błędzie buildu/audytu/testu (także audytu przeglądarkowego scripts/audit_ga4.cjs — wymaga Playwright).
// Po publikacji, gdy strona ma GA4: test zgody na żywej stronie (żądania do Google przerywane). Nieudany smoke → rollback.

import { spawnSync } from "node:child_process";
import { appendFileSync, existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const ORIGIN = "https://hornigold.pl";
const ACCOUNT_ID = "ee23b9132a9692ab6c0e9f22aa86dda8";
const WORKER = "hornigold";
const DEPLOY_BRANCH = "deploy/cloudflare";
const TAG_PREFIX = "hornigold-v";
const OWNER_SWITCHES = ["indexing", "bookingEnabled", "paymentsEnabled", "counterEnabled"];
const SAFE_REF = /^[A-Za-z0-9._/-]+$/;
function expectedPageCount() {
  return JSON.parse(readFileSync(new URL("../routes.json", import.meta.url), "utf8")).length;
}

// ---------- funkcje czyste (testy: tests/cloudflare-release.test.mjs) ----------

export function parseArgs(argv) {
  const options = { mode: "review", candidate: "origin/main", accept: new Set(), push: true, rollback: true };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--deploy") options.mode = "deploy";
    else if (arg === "--prepare") options.mode = "prepare";
    else if (arg === "--smoke") options.mode = "smoke";
    else if (arg === "--candidate") { const ref = argv[++i] ?? ""; options.candidate = ref.startsWith("origin/") ? ref : `origin/${ref}`; }
    else if (arg === "--accept") for (const code of (argv[++i] ?? "").split(",")) { if (code) options.accept.add(code.trim().toUpperCase()); }
    else if (arg === "--no-push") options.push = false;
    else if (arg === "--no-rollback") options.rollback = false;
    else throw new Error(`Nieznana opcja: ${arg}`);
  }
  return options;
}

export function nextReleaseTag(existingTags, revision) {
  const base = `${TAG_PREFIX}${revision}-cloudflare`;
  if (!existingTags.includes(base)) return base;
  let number = 1;
  for (const tag of existingTags) {
    const match = new RegExp(`^${base.replace(/\./g, "\\.")}-r(\\d+)$`).exec(tag);
    if (match) number = Math.max(number, Number(match[1]));
  }
  return `${base}-r${number + 1}`;
}

// nameStatus: `git diff --name-status HEAD...kandydat`; releaseBefore/After: release.json obu stron; cspChanged: diff dotyka CSP.
export function reviewChanges(nameStatus, { releaseBefore = {}, releaseAfter = {}, cspChanged = false } = {}) {
  const blocks = [];
  const warnings = [];
  const newMigrations = [];
  for (const line of nameStatus.split("\n").filter(Boolean)) {
    const [status, ...paths] = line.split("\t");
    const path = paths.at(-1);
    if (paths.some((p) => p.startsWith("drizzle/") && p.endsWith(".sql"))) {
      if (status === "A") newMigrations.push(path);
      else blocks.push({ code: "MIGRATION_CHANGED", detail: `${status} ${paths.join(" → ")} — istniejąca migracja D1 nie może się zmienić` });
    }
    if (path === "wrangler.jsonc") blocks.push({ code: "WRANGLER", detail: "wrangler.jsonc zmieniony przez kandydata — konfiguracja wdrożenia jest nasza" });
    if (path.startsWith("server/")) warnings.push(`server/: ${path} — sprawdzane testami serwera i smoke`);
    if (path === "scripts/seo.py") warnings.push("scripts/seo.py — po scaleniu sprawdzana poprawka Windows (.as_posix())");
    if (path.startsWith("integrations/")) warnings.push(`${path} — integracja przygotowana poza site/, nie trafia na produkcję`);
    if (path === "site/assets/booking.js" || /\/rezerwacja\//.test(path)) warnings.push(`rezerwacje: ${path} — testy booking-pages, ewentualnie scripts/kwhotel_booking_pages.py`);
  }
  for (const key of OWNER_SWITCHES) {
    if (JSON.stringify(releaseBefore[key]) !== JSON.stringify(releaseAfter[key])) {
      blocks.push({ code: "OWNER_SWITCH", detail: `release.json ${key}: ${JSON.stringify(releaseBefore[key])} → ${JSON.stringify(releaseAfter[key])} — decyzja właściciela` });
    }
  }
  if (cspChanged) blocks.push({ code: "CSP", detail: "kandydat zmienia Content-Security-Policy w server/ — sprawdzić nowe źródła (np. Meta) i zgodę na pomiar" });
  return { blocks, warnings, newMigrations };
}

// Strony z naszymi blokami rezerwacji GuestSage (scripts/kwhotel_booking_pages.py). Gdy Kamil je przegeneruje,
// konflikt rozwiązuje się wersją Kamila + ponownym uruchomieniem idempotentnego skryptu.
export function isBookingPage(path) {
  return /^site\/[^/]+\/(?:index\.html|pobyt\/index\.html|rezerwacja\/index\.html)$/.test(path) || path === "site/assets/style.css";
}

// Odnośnik naszego bloku rezerwacji. Sam napis "data-booking" nie wystarcza: sekcja nagrody Kamila ma data-booking-award.
export function hasBookingLink(html) {
  return [...html.matchAll(/<a [^>]*data-booking=""[^>]*>/g)].some((m) => /href="https:\/\/be\.guestsage\.com\//.test(m[0]));
}

// Tekst, który przeglądarka z JavaScriptem namalowałaby z <body> (bez <noscript>, skryptów i znaczników).
export function visibleBodyText(html) {
  const body = /<body[^>]*>([\s\S]*)<\/body>/i.exec(html)?.[1] ?? html;
  return body.replace(/<(noscript|script|style)\b[\s\S]*?<\/\1>/gi, "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

export function robotsMeta(html) {
  const tag = (html.match(/<meta\b[^>]*>/gi) ?? []).find((t) => /\bname=["']robots["']/i.test(t)); // BeautifulSoup zmienia kolejność atrybutów
  return tag ? /\bcontent=["']([^"']*)["']/i.exec(tag)?.[1] ?? null : null;
}

export function firstRedirect(routesSource) {
  const match = /"(\/[^"]+\/)":\s*"(\/[^"]+\/)"/.exec(routesSource);
  return match ? { from: match[1], to: match[2] } : null;
}

export function pickActiveVersion(deployments) {
  const latest = [...deployments].sort((a, b) => String(b.created_on).localeCompare(String(a.created_on)))[0];
  const versions = latest?.versions ?? [];
  return (versions.find((v) => v.percentage === 100) ?? versions[0])?.version_id ?? null;
}

// ---------- wykonanie ----------

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const PYTHON = join(ROOT, ".venv", "Scripts", "python.exe");
const say = (message) => console.log(message);
const fail = (message) => { const error = new Error(message); error.release = true; throw error; };

function run(command, args, { env = {}, shell = false, allowFail = false, quiet = false } = {}) {
  const result = spawnSync(command, args, {
    cwd: ROOT, shell, encoding: "utf8", maxBuffer: 256 * 1024 * 1024,
    env: { ...process.env, CLOUDFLARE_ACCOUNT_ID: ACCOUNT_ID, MSYS_NO_PATHCONV: "1", PYTHONUTF8: "1", ...env },
  });
  const output = `${result.stdout ?? ""}${result.stderr ?? ""}`;
  if (result.status !== 0 && !allowFail) {
    if (!quiet) console.error(output.slice(-4000));
    fail(`Polecenie nie powiodło się (${result.status}): ${command} ${args.join(" ")}`);
  }
  return { status: result.status, output, stdout: result.stdout ?? "" };
}

const git = (args, options) => run("git", args, options).stdout.trim();
// Worktree nie ma node_modules — wrangler w wersji z package.json z cache npx (bez --yes npx czeka na zgodę na instalację).
// npx to na Windows plik .cmd — wyłącznie stałe argumenty, nigdy nazwy gałęzi.
const WRANGLER_VERSION = JSON.parse(readFileSync(join(ROOT, "package.json"), "utf8")).devDependencies?.wrangler ?? "4.92.0";
const wrangler = (args, options) => {
  if (!/^\d+\.\d+\.\d+$/.test(WRANGLER_VERSION)) fail(`Nieoczekiwana wersja wranglera w package.json: ${WRANGLER_VERSION}`);
  return run("npx", ["--yes", `wrangler@${WRANGLER_VERSION}`, ...args], { ...options, shell: true });
};
const python = (args, options) => run(PYTHON, args, options);

function lastJson(output) {
  const line = output.trim().split("\n").reverse().find((l) => l.trim().startsWith("{"));
  try { return line ? JSON.parse(line) : null; } catch { return null; }
}

function preconditions() {
  if (/onedrive/i.test(ROOT)) fail(`Repozytorium w OneDrive (${ROOT}) — wydanie tylko z C:\\dev\\hornigold-cloudflare.`);
  const branch = git(["rev-parse", "--abbrev-ref", "HEAD"]);
  if (branch !== DEPLOY_BRANCH) fail(`Bieżąca gałąź ${branch}, oczekiwana ${DEPLOY_BRANCH}.`);
  const dirty = git(["status", "--porcelain", "--untracked-files=no"]);
  if (dirty) fail(`Niezatwierdzone zmiany w drzewie:\n${dirty}`);
  if (!existsSync(PYTHON)) fail(`Brak ${PYTHON} (venv z bs4).`);
}

function readRelease(ref) {
  return JSON.parse(ref ? git(["show", `${ref}:release.json`]) : readFileSync(join(ROOT, "release.json"), "utf8"));
}

function reviewCandidate(ref) {
  const range = `HEAD...${ref}`;
  const nameStatus = git(["diff", "--name-status", range]);
  const cspChanged = /^[+-].*Content-Security-Policy/m.test(git(["diff", range, "--", "server/"]));
  return reviewChanges(nameStatus, { releaseBefore: readRelease("HEAD"), releaseAfter: readRelease(ref), cspChanged });
}

// Kolejność z runbooka; każdy krok osobno (build na Windows potrafi paść z braku pamięci).
function buildAndTest(changedTests) {
  const sha = git(["rev-parse", "HEAD"]);
  const steps = [
    ["build podglądu", [join("scripts", "build.py"), "--base", "/", "--counter"]],
    ["audit_static", [join("scripts", "audit_static.py"), "--base", "/"]],
    ["build produkcyjny", [join("scripts", "build.py"), "--mode", "production-ready", "--base", "/", "--counter", "--production-counter"]],
    ["audit_seo", [join("scripts", "audit_seo.py"), "--mode", "production-ready"]],
    ["audit_discovery", [join("scripts", "audit_discovery.py"), "--mode", "production-ready"]],
    ["paczka _cloudflare_production", [join("scripts", "prepare_cloudflare_production.py")]],
  ];
  let pages = expectedPageCount();
  for (const [label, args] of steps) {
    const started = Date.now();
    const result = python(args, { env: { GITHUB_SHA: sha } });
    const report = lastJson(result.output);
    const errors = report?.errors;
    if (Array.isArray(errors) ? errors.length : errors) fail(`${label}: błędy ${JSON.stringify(errors).slice(0, 500)}`);
    if (label === "build produkcyjny" && report?.pages) pages = report.pages;
    say(`   ✓ ${label} (${Math.round((Date.now() - started) / 1000)} s)`);
  }
  const nodeTests = ["tests/production-indexing.test.mjs", "tests/server.test.mjs", "tests/booking.test.mjs", "tests/booking-pages.test.mjs", "tests/search-console-verification.test.mjs", ...changedTests];
  run(process.execPath, ["--test", ...new Set(nodeTests.filter((f) => existsSync(join(ROOT, f))))]);
  say("   ✓ testy node");
  python(["-m", "unittest", "discover", "-s", "tests", "-p", "test_seo*.py"]);
  say("   ✓ testy SEO");
  // Audyt przeglądarkowy GA4 Kamila (zgoda, brak ruchu do Google przed zgodą; ruch przechwytywany) na _production_ready.
  // Pozostałe scripts/audit_*.cjs to QA Kamila pisane pod Linux/macOS (/tmp, podgląd _site, pomiary wydajności) — nie bramka wydania.
  const browserAudits = ["audit_ga4.cjs"].filter((f) => existsSync(join(ROOT, "scripts", f)));
  if (browserAudits.length && !existsSync(join(ROOT, "node_modules", "playwright"))) {
    fail("Brak Playwright do audytów przeglądarkowych: npm install --no-package-lock && npx playwright install chromium");
  }
  for (const audit of browserAudits) {
    run(process.execPath, [join("scripts", audit)]);
    say(`   ✓ ${audit}`);
  }
  git(["checkout", "--", "docs/seo/"]); // raporty audytów — nie commitować
  return pages;
}

function mergeCandidate(ref) {
  const merged = run("git", ["merge", "--no-ff", "--no-edit", ref], { allowFail: true, quiet: true });
  if (merged.status === 0) return;
  const conflicted = git(["diff", "--name-only", "--diff-filter=U"]).split("\n").filter(Boolean);
  if (!conflicted.length || !conflicted.every(isBookingPage)) {
    run("git", ["merge", "--abort"], { allowFail: true });
    fail(`Konflikt przy scalaniu ${ref} poza stronami rezerwacji:\n  ${conflicted.filter((f) => !isBookingPage(f)).join("\n  ")}`);
  }
  git(["checkout", "--theirs", "--", ...conflicted]);
  python([join("scripts", "kwhotel_booking_pages.py")]);
  git(["add", "--", ...conflicted]);
  git(["add", "-u", "--", "site/"]);
  git(["commit", "--no-edit"]);
  say(`   konflikt w ${conflicted.length} stronach rezerwacji: wersja Kamila + scripts/kwhotel_booking_pages.py`);
}

// Na żywej stronie: przed zgodą i po odmowie zero żądań do Google; po zgodzie tag próbuje się załadować.
// Żądania do Google są przerywane — test nie wysyła żadnych danych do GA.
async function liveAnalyticsConsent() {
  const { chromium } = createRequire(import.meta.url)("playwright");
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
    let google = 0;
    await context.route("**/*", (route) => {
      const host = new URL(route.request().url()).hostname;
      if (/(^|\.)(googletagmanager|google-analytics)\.com$/.test(host)) { google += 1; return route.abort(); }
      return route.continue();
    });
    const page = await context.newPage();
    page.setDefaultTimeout(20_000);
    // „load”/„networkidle” na żywej stronie potrafi nie nadejść (Windows) — DOMContentLoaded + pauzy.
    await page.goto(`${ORIGIN}/pl/?email=private@example.com&arrival=2030-01-01`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(3000);
    const beforeConsent = google;
    await page.locator("[data-privacy-open]").first().click();
    const prechecked = await page.locator("[name=analytics]").isChecked();
    await page.locator("[data-privacy-necessary]").last().click();
    await page.waitForTimeout(3000);
    const afterRefusal = google;
    await page.locator("[data-privacy-open]").first().click();
    await page.locator("[name=analytics]").check();
    await page.locator("[data-privacy-save]").click();
    await page.waitForTimeout(4000);
    const leaked = await page.evaluate(() => JSON.stringify(window.dataLayer ?? []));
    return { beforeConsent, prechecked, afterRefusal, afterConsent: google - afterRefusal, privateParams: /private@example|2030-01-01/.test(leaked) };
  } catch (error) {
    return { error: error.message.split("\n")[0] };
  } finally {
    await Promise.race([browser.close(), new Promise((r) => setTimeout(r, 10_000))]);
  }
}

async function request(path, init = {}) {
  const url = path.startsWith("http") ? path : `${ORIGIN}${path}`;
  const response = await fetch(url, { redirect: "manual", ...init, signal: AbortSignal.timeout(30_000) });
  if (response.status === 403 && response.headers.get("cf-mitigated") === "challenge") {
    fail(`${url}: 403 Cf-Mitigated: challenge — to ustawienie strefy, nie Worker.`);
  }
  return response;
}

export async function smoke({ pages = expectedPageCount(), expectedCsp = null } = {}) {
  const failures = [];
  const check = (ok, message) => { if (ok) say(`  ✓ ${message}`); else { say(`  ✗ ${message}`); failures.push(message); } };
  const release = readRelease();

  const home = await request("/pl/");
  const homeHtml = await home.text();
  check(home.status === 200, `/pl/ → ${home.status}`);
  check(/index,\s*follow/.test(robotsMeta(homeHtml) ?? "") && !/noindex/i.test(home.headers.get("x-robots-tag") ?? ""), `/pl/ robots: ${robotsMeta(homeHtml)}, X-Robots-Tag: ${home.headers.get("x-robots-tag") ?? "—"}`);
  const csp = home.headers.get("content-security-policy");
  if (expectedCsp) check(csp === expectedCsp, "CSP bez zmian względem poprzedniej wersji");
  else check(Boolean(csp), "nagłówek CSP obecny");
  if (homeHtml.includes("/assets/analytics-config.js")) {
    const metaCsp = /<meta[^>]*http-equiv=["']Content-Security-Policy["'][^>]*>/i.exec(homeHtml)?.[0] ?? "";
    check(csp?.includes("https://www.googletagmanager.com") && (!metaCsp || metaCsp.includes("https://www.googletagmanager.com")), "GA4: CSP nagłówka i meta dopuszcza tag Google");
    if (existsSync(join(ROOT, "node_modules", "playwright"))) {
      const consent = await liveAnalyticsConsent();
      if (consent.error) check(false, `GA4: test zgody w przeglądarce nie wykonany: ${consent.error}`);
      else {
        check(consent.beforeConsent === 0 && consent.afterRefusal === 0, `GA4: przed zgodą ${consent.beforeConsent}, po odmowie ${consent.afterRefusal} żądań do Google (oczekiwane 0)`);
        check(!consent.prechecked, "GA4: zgoda na analitykę nie jest domyślnie zaznaczona");
        check(consent.afterConsent >= 1, `GA4: po zgodzie tag Google ładowany (${consent.afterConsent} żądań, przerwanych w teście)`);
        check(!consent.privateParams, "GA4: parametry z adresu (e-mail, daty) nie trafiają do dataLayer");
      }
    } else say("  ! GA4: test zgody w przeglądarce pominięty — brak Playwright");
  }

  const missing = await request("/pl/nie-ma-takiej/");
  const missingHtml = await missing.text();
  check(missing.status === 404 && (/noindex/i.test(missing.headers.get("x-robots-tag") ?? "") || /noindex/i.test(robotsMeta(missingHtml) ?? "")), `/pl/nie-ma-takiej/ → ${missing.status} z noindex`);

  const robots = await (await request("/robots.txt")).text();
  check(/^Allow:\s*\/\s*$/m.test(robots), "robots.txt: Allow: /");
  const sitemap = await (await request("/sitemap.xml")).text();
  const locs = (sitemap.match(/<loc>/g) ?? []).length;
  const excluded=Object.keys(JSON.parse(readFileSync(join(ROOT,'seo/indexing-policy.json'),'utf8')).excludedRoutes).length;
  check(locs === pages-excluded, `sitemap.xml: ${locs} indeksowalnych adresów (oczekiwane ${pages-excluded})`);

  const live = await (await request("/release.json")).json().catch(() => ({}));
  check(live.indexing === true && live.bookingEnabled === false, `/release.json: indexing ${live.indexing}, bookingEnabled ${live.bookingEnabled}`);
  const stats = await request("/api/site-stats");
  check(stats.status === 200, `/api/site-stats → ${stats.status}`);

  const redirect = firstRedirect(readFileSync(join(ROOT, "server", "routes.mjs"), "utf8"));
  if (redirect) {
    const old = await request(`${redirect.from}?utm_source=release-smoke`);
    check(old.status === 301 && (old.headers.get("location") ?? "").endsWith(`${redirect.to}?utm_source=release-smoke`), `stary adres ${redirect.from} → ${old.status} ${old.headers.get("location")}`);
  }
  const www = await request("https://www.hornigold.pl/pl/?q=1");
  check(www.status === 301 && www.headers.get("location") === `${ORIGIN}/pl/?q=1`, `www → ${www.status} ${www.headers.get("location")}`);

  for (const language of release.languages ?? []) {
    const path = `/${language.toLowerCase()}/rezerwacja/`;
    const page = await request(path);
    check(page.status === 200 && hasBookingLink(await page.text()), `${path} → ${page.status} z a[data-booking] do GuestSage`);
  }
  // Gość nie może zobaczyć strony pośredniej: "/" nic nie maluje przed przejściem do języka, a wybór pokoju
  // z terminem dostaje 302 prosto do silnika (server/production-entry.mjs), nie stronę Rezerwacja.
  const root = await request("/");
  check(root.status===301 && root.headers.get("location")==="https://hornigold.pl/pl/", `/ → ${root.status} ${root.headers.get("location")}`);
  const day = (offset) => new Date(Date.now() + offset * 86_400_000).toISOString().slice(0, 10);
  const stay = `arrival=${day(30)}&departure=${day(32)}&guests=2`;
  const handover = await request(`/pl/rezerwacja/?${stay}&room=classic`);
  const target = handover.headers.get("location") ?? "";
  check(handover.status === 302 && /^https:\/\/be\.guestsage\.com\/pl\/[0-9a-f-]+\/offers\?/.test(target) && target.endsWith(`personsCount=2&featuredRoomTypeId=4830`),
    `wybór pokoju z terminem → ${handover.status} ${target.replace(/\/[0-9a-f-]{36}\//, "/<obiekt>/")}`);
  const stays = await request(`/pl/rezerwacja/?${stay}&room=hornigold`);
  check(stays.status === 200, `pokój bez oferty online → ${stays.status} (strona Rezerwacja)`);
  // Search Console wymaga 200 pod dokładnym adresem — bez obsługi w server/production-entry.mjs assety dałyby 307.
  for (const file of readdirSync(join(ROOT, "site")).filter((f) => /^google[0-9a-f]+\.html$/.test(f))) {
    const response = await request(`/${file}`);
    check(response.status === 200 && (await response.text()).trim() === `google-site-verification: ${file}`, `/${file} → ${response.status} (weryfikacja Search Console)`);
  }
  return failures;
}

function activeWorkerVersion() {
  const { stdout } = wrangler(["deployments", "list", "--json", "--name", WORKER, "--config", "wrangler.jsonc"]);
  return pickActiveVersion(JSON.parse(stdout.slice(stdout.search(/^\[/m))));
}

function appendDeployLog(entry) {
  const file = join(ROOT, "docs", "DEPLOY-LOG.md");
  if (!existsSync(file)) {
    writeFileSync(file, "# Dziennik wydań hornigold.pl (Cloudflare)\n\nZapisuje `scripts/cloudflare-release.mjs --deploy`. Procedura: [`CLOUDFLARE.md`](CLOUDFLARE.md).\n\n| Data (UTC) | Tag | Rewizja | Worker | Poprzedni Worker | Commit Kamila | Migracje |\n|---|---|---|---|---|---|---|\n");
  }
  appendFileSync(file, `| ${entry.date} | \`${entry.tag}\` | ${entry.revision} | \`${entry.worker}\` | \`${entry.previous}\` | \`${entry.upstream}\` | ${entry.migrations} |\n`);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.mode === "smoke") {
    say(`Smoke ${ORIGIN}`);
    const failures = await smoke();
    if (failures.length) fail(`Smoke: ${failures.length} porażek.`);
    return;
  }

  preconditions();
  say("1. Pobieranie z GitHuba");
  git(["fetch", "--prune", "origin"]);
  const ref = options.candidate;
  if (!SAFE_REF.test(ref)) fail(`Niebezpieczna nazwa gałęzi: ${ref}`);
  if (run("git", ["rev-parse", "--verify", "--quiet", ref], { allowFail: true }).status !== 0) fail(`Nie ma gałęzi ${ref}.`);
  const ahead = Number(git(["rev-list", "--count", `HEAD..${ref}`]));
  say(`   HEAD ${git(["rev-parse", "--short", "HEAD"])}, ${ref} ${git(["rev-parse", "--short", ref])} (+${ahead})`);
  if (ahead === 0) { say("   brak nowego kodu — nic do wdrożenia"); return; }

  say("2. Przegląd");
  for (const line of git(["log", "--format=%h %ad %s", "--date=format:%m-%d %H:%M", `HEAD..${ref}`]).split("\n").slice(0, 20)) say(`     ${line}`);
  const review = reviewCandidate(ref);
  for (const warning of review.warnings) say(`   uwaga: ${warning}`);
  for (const block of review.blocks) say(`   ${options.accept.has(block.code) ? "przyjęte" : "STOP"} [${block.code}] ${block.detail}`);
  say(`   nowe migracje D1: ${review.newMigrations.length ? review.newMigrations.join(", ") : "brak"}`);
  const blocks = review.blocks.filter((block) => !options.accept.has(block.code));
  if (blocks.length) fail(`Przegląd zatrzymał wydanie (${[...new Set(blocks.map((b) => b.code))].join(", ")}). Po weryfikacji: --accept <kody> (nie dotyczy MIGRATION_CHANGED, WRANGLER).`);
  if (!["deploy", "prepare"].includes(options.mode)) { say("Przegląd czysty. Wdrożenie: node scripts/cloudflare-release.mjs --deploy"); return; }

  say("3. Scalanie do deploy/cloudflare");
  const changedTests = git(["diff", "--name-only", "--diff-filter=AM", `HEAD...${ref}`, "--", "tests/"]).split("\n").filter((f) => f.endsWith(".test.mjs"));
  mergeCandidate(ref);
  if (!/as_posix\(\)/.test(readFileSync(join(ROOT, "scripts", "seo.py"), "utf8"))) fail("scripts/seo.py bez .as_posix() — build na Windows da 693× noindex. Przywrócić poprawkę (CLOUDFLARE.md).");
  say(`   HEAD ${git(["rev-parse", "--short", "HEAD"])}`);

  say("4. Build, audyty, testy (kilkanaście minut)");
  const pages = buildAndTest(changedTests);
  if (options.mode === "prepare") {
    say(`Przygotowane (${pages} stron, paczka _cloudflare_production). Publikacja: npx wrangler deploy --config C:/dev/hornigold-cloudflare/wrangler.jsonc, potem --smoke.`);
    return;
  }

  say("5. Migracje D1");
  if (review.newMigrations.length) {
    wrangler(["d1", "migrations", "apply", "hornigold-counter-eu", "--remote", "--config", "wrangler.jsonc"]);
    say(`   zastosowane: ${review.newMigrations.length}`);
  } else say("   brak");

  say("6. Publikacja");
  const previous = activeWorkerVersion();
  const csp = options.accept.has("CSP") ? null : (await request("/pl/")).headers.get("content-security-policy");
  const deployed = wrangler(["deploy", "--config", "wrangler.jsonc"]);
  const workerVersion = /Current Version ID:\s*(\S+)/.exec(deployed.output)?.[1];
  if (!workerVersion) fail("Brak „Current Version ID” w wyniku wrangler deploy.");
  say(`   Worker ${workerVersion} (poprzedni ${previous})`);

  say("7. Smoke");
  await new Promise((r) => setTimeout(r, 5_000));
  const failures = await smoke({ pages, expectedCsp: csp });
  if (failures.length) {
    if (options.rollback && previous) {
      wrangler(["rollback", previous, "--name", WORKER, "--config", "wrangler.jsonc", "-m", "cloudflare-release: smoke", "-y"]);
      fail(`Smoke nie przeszedł — przywrócono Worker ${previous}.`);
    }
    fail("Smoke nie przeszedł (rollback wyłączony).");
  }

  say("8. Tag i dziennik");
  const revision = readRelease().revision ?? String(readRelease().version);
  const tag = nextReleaseTag(git(["tag", "-l", `${TAG_PREFIX}*`]).split("\n"), revision);
  git(["tag", "-a", tag, "HEAD", "-m", `hornigold.pl: rewizja ${revision}, Worker ${workerVersion}, ${ref} ${git(["rev-parse", "--short", ref])}`]);
  appendDeployLog({
    date: new Date().toISOString().slice(0, 16).replace("T", " "), tag, revision, worker: workerVersion, previous,
    upstream: git(["rev-parse", "--short", ref]), migrations: review.newMigrations.length ? review.newMigrations.join(", ") : "—",
  });
  git(["add", "docs/DEPLOY-LOG.md"]);
  git(["commit", "-m", `docs(deploy): ${tag} — Worker ${workerVersion}`]);
  if (options.push) {
    const pushed = run("git", ["push", "origin", DEPLOY_BRANCH, tag], { allowFail: true, quiet: true });
    say(pushed.status === 0 ? "   wypchnięte: deploy/cloudflare i tag" : "   push odrzucony (CloudDev-M bez prawa zapisu do repo Kamila) — gałąź i tag zostają lokalnie");
  }
  say(`Gotowe: ${tag}, Worker ${workerVersion}. Rollback: npx wrangler rollback ${previous} --config C:/dev/hornigold-cloudflare/wrangler.jsonc`);
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  main().catch((error) => {
    console.error(`\n✗ ${error.message}`);
    if (!error.release) console.error(error.stack);
    process.exitCode = 1;
  });
}
