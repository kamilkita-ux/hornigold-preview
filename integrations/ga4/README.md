# GA4 — prepared locally, not activated

A separate property and WWW stream were created and reread in Google Analytics on 2026-10-10: account 93077899, property 558323228, stream 16101873868, measurement ID G-ZJ9VJNGHGT. See account-status-2026-10-10.json. Collection has not been activated.
The tested runtime is now in `site/assets/analytics.js`; `scripts/build.py` injects it only in production-ready builds. Preview HTML does not include it. The verified measurement configuration is generated separately for each mode. External Cloudflare deployment and GA4 event receipt are still unverified.

Activation requirements:
1. Use the company Google Analytics account; confirm ownership of the property and create/select the Hornigold WWW stream for https://hornigold.pl.
2. Record the public measurement ID (G-…), not API secrets. Disable enhanced measurement and unwanted automatic form/outbound event collection in the stream before activation.
3. Add a separate, unchecked analytics category to the seven-language CMP. Expose `HornigoldPrivacy.allowsAnalytics()` and dispatch `hornigold:privacy` after save, refusal, withdrawal, expiry and cross-tab changes. Existing map/marketing consent never implies analytics consent.
4. Synchronize privacy/cookies HTML and PDFs with actual Google service settings, retention and supplier/transfer information.
5. Set `window.HornigoldGA4={enabled:true,measurementId: VERIFIED_ID}` in a same-origin external configuration file; include analytics.js only after the CMP.
6. Adjust production CSP for the verified Google tag and GA collection endpoints; leave previews disabled. Review tag loading under the site's strict CSP before release.
7. Test no Google traffic before consent/on refusal, a single sanitized page_view after consent, no query/hash/referrer or personal/form data, cookie clearing and cessation after withdrawal, expiry and second-tab changes. Confirm receipt in GA4 DebugView/Realtime using an explicitly consented test session.
8. Deploy through the actual Cloudflare pipeline and reread the public website. GitHub publication alone does not prove Cloudflare deployment or receipt of analytics events.

Basic consent mode: the Google tag is not loaded until analytics consent is granted.
Google Ads storage, user data and personalization stay denied. No purchase, payment or reservation events are implemented.

Official implementation guidance: https://developers.google.com/tag-platform/security/guides/consent?consentmode=basic
