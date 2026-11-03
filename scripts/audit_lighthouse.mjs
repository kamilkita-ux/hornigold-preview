import fs from 'node:fs/promises';
import lighthouse from 'lighthouse';
import {launch} from 'chrome-launcher';
import {chromium} from 'playwright';
const origin = process.env.LIGHTHOUSE_URL || 'http://127.0.0.1:4383';
const strict = process.env.LIGHTHOUSE_PROFILE === 'seo100';
const output = process.env.LIGHTHOUSE_OUTPUT || 'docs/implementation/evidence/lighthouse';
if (strict && !['127.0.0.1', 'localhost'].includes(new URL(origin).hostname)) throw new Error('SEO100 runs only against an isolated local production build.');
const paths = strict ? ['/pl/', '/pl/pokoje/', '/pl/pokoje/classic/', '/pl/wellness-spa/', '/en/', '/de/'] : ['/pl/', '/pl/pokoje/', '/en/'];
const thresholds = strict ? {performance: 95, accessibility: 98, 'best-practices': 100, seo: 100} : {accessibility: 90, seo: 90, 'best-practices': 90};
await fs.mkdir(output, {recursive: true});
const chrome = await launch({chromePath: chromium.executablePath(), chromeFlags: ['--headless', '--no-sandbox']});
const results = [];
let failed = false;
try {
  for (const path of paths) {
    const id = path.replaceAll('/', '-').replace(/^-|-$/g, '');
    const {lhr, report} = await lighthouse(new URL(path, origin).href, {
      port: chrome.port, output: ['html', 'json'], logLevel: 'error',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    });
    await fs.writeFile(`${output}/${id}.html`, report[0]);
    await fs.writeFile(`${output}/${id}.json`, report[1]);
    const scores = Object.fromEntries(Object.entries(lhr.categories).map(([key, value]) => [key, Math.round((value.score || 0) * 100)]));
    const failures = Object.entries(lhr.audits).filter(([, audit]) => audit.score !== null && audit.score < 1).map(([key, audit]) => ({id: key, title: audit.title, score: audit.score, displayValue: audit.displayValue}));
    const pass = !lhr.runtimeError && Object.entries(thresholds).every(([key, minimum]) => scores[key] >= minimum);
    failed ||= !pass;
    results.push({path, scores, pass, performanceWarning: scores.performance < 80, runtimeError: lhr.runtimeError, failures});
    console.log(JSON.stringify({path, scores, pass, performanceWarning: scores.performance < 80}));
  }
} finally { await chrome.kill(); }
await fs.writeFile(`${output}/summary.json`, JSON.stringify({origin, testedAt: new Date().toISOString(), device: 'mobile', profile: strict ? 'seo100' : 'existing-ci', thresholds, results}, null, 2));
if (process.env.GITHUB_STEP_SUMMARY) await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, '\n### Lighthouse mobile\n\n| Page | Performance | Accessibility | Best practices | SEO |\n|---|---:|---:|---:|---:|\n' + results.map(r => `| ${r.path} | ${r.scores.performance} | ${r.scores.accessibility} | ${r.scores['best-practices']} | ${r.scores.seo} |`).join('\n') + '\n\nThresholds are recorded in summary.json; SEO100 requires 95/98/100/100, existing CI retains its separate thresholds. Full reports are in the evidence artifact.\n');
if (failed) process.exitCode = 1;
