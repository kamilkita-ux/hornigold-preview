# Hornigold.pl: authorized production SEO, 2026-10-09

## Verified current state
- Owner confirmed Cloudflare cutover and authorized production indexing. Booking/payments remain disabled.
- Full read-only public crawl: 693 canonical routes, zero checked metadata/canonical/hreflang/status errors; all 693 still noindex. Source snapshot saved separately in the verified Mac mini evidence backup.
- Both HTML meta and HTTP X-Robots-Tag block indexing. robots.txt disallows all crawling. Canonicals already point to hornigold.pl.
- Production release reports e4b6a3a9f690ad5276a4bb75e12c7d680d396bab; GitHub main was b40f5b5894e6a525252bdab492b2334919eb6fe0 when checked. The actual Cloudflare build source/config is NOT verified. Do not assume GitHub push deploys this domain.
- Email requesting repo/branch/project/build/config/access was sent from lu@farmyfotowoltaiki.pl to the owner-authorized recipient biuro@cloudmentor.pl. API accepted the send; recipient delivery not independently confirmed.

## Reproducible production package (no deploy in these commands)
```
python3 scripts/build.py --mode production-ready --base / --counter --production-counter
python3 scripts/audit_seo.py --mode production-ready
python3 scripts/audit_discovery.py --mode production-ready
python3 scripts/prepare_cloudflare_production.py
node --test tests/production-indexing.test.mjs tests/server.test.mjs
python3 -m unittest discover -s tests -p 'test_seo*.py'
```
The explicit counter flag preserves the existing aggregate counter and requires its current DB binding. It does not create, migrate or clear databases. The old production-ready counter guard remains enforced unless explicitly opted into this production build.

Output `_cloudflare_production/` contains assets, server modules and a SHA256 manifest. Worker entrypoint: `server/production-entry.mjs`; asset directory: `assets`; binding: `ASSETS`; run_worker_first must remain true; not_found_handling must preserve actual HTTP404. This is an application package, NOT a new Cloudflare account/Worker/DB configuration.

## Deployment using the existing project only
1. Obtain Marek's actual Worker configuration, account/project and build pipeline; identify every binding, custom domain and route. Preserve the entire existing configuration and DB history. No guessed IDs or new project.
2. Back up the active deployment/configuration and confirm rollback to that version. Keep secrets exclusively in their approved vault/runtime, never source or mail.
3. Merge the reviewed production entrypoint/assets paths into that existing configuration. Reuse ASSETS and DB. Do not copy the Sites placeholder database ID. Keep workers.dev and all previews excluded via the hostname gate; keep Sites/Pages preview builds unchanged.
4. Build and audit as above from the exact chosen source commit. Record artifact hash, source SHA and existing Cloudflare version before deploying.
5. Deploy only through the confirmed pipeline. No DNS, mail, search-account, analytics, booking or payment changes are part of this release.
6. Remove any independent blanket noindex Transform Rule ONLY for the canonical production host after checking its exact scope. The worker cannot undo a Cloudflare rule that adds a header afterwards. Do not weaken WAF or bot protections globally; verify Googlebot/Bingbot/OAI-SearchBot access narrowly if challenges occur.
7. Canonical successful pages and sitemap become crawlable; PDFs, API, root language-routing shell, aliases and real errors remain noindex. www redirects preserve path/query. All workers.dev/other-host copies remain noindex and Disallow: /.
8. Read back all 693 canonical URLs, robots, sitemap (693 entries), reciprocal hreflang, HTTP/meta robots, images, navigation, PDF exclusions, real404 and legacy301 query preservation. Read back Sites and GitHub Pages to confirm unchanged exclusions. Check both full 200 responses and conditional 304 responses.
9. Only after live verification, submit sitemap to authorized Google Search Console and Bing Webmaster Tools accounts. Account access is not currently confirmed. Do not claim indexing, rankings or AI inclusion from a successful upload.

## Remaining limits
- Full old-WordPress URL export is not available; the existing known 539 redirects are preserved, but this is not proof of covering every historical URL.
- This SEO acceptance is not legal/PAD certification or real payment/PMS acceptance.
- Current production is still blocked until the confirmed deployment runs and public verification succeeds.

Sources: https://developers.google.com/search/docs/crawling-indexing/block-indexing ; https://developers.cloudflare.com/workers/static-assets/headers/
