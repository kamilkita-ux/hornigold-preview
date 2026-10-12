# Lighthouse mobile checks

Pinned Lighthouse 13.5.0 and chrome-launcher 1.2.2, using the existing Playwright Chromium installation. No paid service or public report upload is configured.

Quality workflow: pull requests, manual runs and the existing weekly Monday audit. Tests the local production-ready artifact on `/pl/`, `/pl/pokoje/`, `/en/`; preview noindex is preserved. Publication workflow: read-only audit of the same paths on https://hornigold.pl after successful GitHub Pages publication. This event does not prove or trigger a Cloudflare deployment.

Accessibility, SEO and best-practices scores below 90 or a Lighthouse runtime error fail the check. Performance below 80 is reported as a warning because CI hardware and network noise affect scores. These are minimum score thresholds, not historical regression comparison. Review the HTML/JSON reports for actionable findings. This automated sample is not a full accessibility certification or a booking/payment test.

HTML/JSON reports and a summary are retained in Actions evidence artifacts for seven days. Category scores are also shown in the workflow summary. The existing failure-report workflow deduplicates failed checks into GitHub issues; it does not automatically wake local Codex.

Rollback: revert the Lighthouse change, including dependency/lockfile updates, leaving unrelated site changes intact. Main activation remains subject to the required verified Mac mini backup.
