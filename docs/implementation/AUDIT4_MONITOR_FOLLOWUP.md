# Audit 4 — monitoring reconciliation, 15 October 2026

The source audit covered 23.21, while production readback proves 23.24 / 178442e576a910efe6229c7e7c13245ec2ae1de2. All original 34 requirements remain in REGISTER.json; 22 audit observations are mapped separately. The Polish privacy banner is currently corrected. The Czech localization remains incomplete and unpublished.

The previous monitor compared a newer production sitemap with the old checkout inventory and incorrectly reported a sitemap failure (462 versus 463 URLs). The revised monitor resolves routes and indexing exclusions using the full immutable commit from the public production release. The public source host and repository are fixed; branch names, invalid SHA values, missing files and transport failures cannot silently substitute stale local policy. Legacy unversioned releases retain the prior local behavior, explicitly labelled.

The stable private runtime at /Users/kamilkita/Documents/Hornigold-monitoring/monitor_public.py is verified byte-for-byte. The existing daily automation remains active at 07:30 Europe/Warsaw and now uses this runtime. Aggregate traffic history remains private. No website deployment, booking/Fiserv configuration, DNS, permissions or payment changed.

Targeted synthetic tests: 20 passed. Production readback: 12 checks passed using 463 indexable URLs. This is not transaction, legal, translation, ranking or PDF/UA acceptance. Full Python suite requires preview artifacts before invocation, as in CI.
