import fs from 'node:fs/promises';
import lighthouse from 'lighthouse';
import {launch} from 'chrome-launcher';
import {chromium} from 'playwright';
const origin = process.env.LIGHTHOUSE_URL || 'http://127.0.0.1:4383';
const output = 'docs/implementation/evidence/lighthouse';
await fs.mkdir(output, {recursive: true});
const chrome = await launch({chromePath: chromium.executablePath(), chromeFlags: ['--headless', '--no-sandbox']});
const results = [];
let failed = false;
try {
  for (const path of ['/pl/', '/pl/pokoje/', '/en/']) {
    const id = path.replaceAll('/', '-').replace(/^-|-$/g, '');
    const {lhr, report} = await lighthouse(new URL(path, origin).href, {
      port: chrome.port, output: ['html', 'json'], logLevel: 'error',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    });
    await fs.writeFile(`${output}/${id}.html`, report[0]);
    await fs.writeFile(`${output}/${id}.json`, report[1]);
    const scores = Object.fromEntries(Object.entries(lhr.categories).map(([key, value]) => [key, Math.round((value.score || 0) * 100)]));
    const failures = Object.entries(lhr.audits).filter(([, audit]) => audit.score !== null && audit.score < 1).map(([key, audit]) => ({id: key, title: audit.title, score: audit.score, displayValue: audit.displayValue}));
    const pass = !lhr.runtimeError && scores.accessibility >= 90 && scores.seo >= 90 && scores['best-practices'] >= 90;
    failed ||= !pass;
    results.push({path, scores, pass, performanceWarning: scores.performance < 80, runtimeError: lhr.runtimeError, failures});
    console.log(JSON.stringify({path, scores, pass, performanceWarning: scores.performance < 80}));
  }
} finally { await chrome.kill(); }
await fs.writeFile(`${output}/summary.json`, JSON.stringify({origin, testedAt: new Date().toISOString(), device: 'mobile', thresholds: {accessibility: 90, seo: 90, 'best-practices': 90, performanceWarning: 80}, results}, null, 2));
if (process.env.GITHUB_STEP_SUMMARY) await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, '\n### Lighthouse mobile\n\n| Page | Performance | Accessibility | Best practices | SEO |\n|---|---:|---:|---:|---:|\n' + results.map(r => `| ${r.path} | ${r.scores.performance} | ${r.scores.accessibility} | ${r.scores['best-practices']} | ${r.scores.seo} |`).join('\n') + '\n\nPerformance below 80 is a warning; other categories below 90 fail the check. Full reports are in the evidence artifact.\n');
if (failed) process.exitCode = 1;
