"""Package an audited production variant without guessing or deploying Cloudflare configuration."""
from pathlib import Path
import json,shutil,hashlib,subprocess
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'_production_ready';release=json.loads((source/'release.json').read_text())
assert release['buildMode']=='production-ready' and release['base']=='/' and release['indexing']
assert not release['bookingEnabled'] and not release['paymentsEnabled']
assert (source/'sitemap.xml').is_file() and 'Allow: /' in (source/'robots.txt').read_text()
out=ROOT/'_cloudflare_production'
if out.exists():shutil.rmtree(out)
(out/'server').mkdir(parents=True);shutil.copytree(source,out/'assets')
for name in ['worker.mjs','counter.mjs','routes.mjs','production-entry.mjs']:shutil.copy2(ROOT/'server'/name,out/'server'/name)
p=out/'server/routes.mjs';text=p.read_text();assert 'export const siteMode="preview";' in text;p.write_text(text.replace('export const siteMode="preview";','export const siteMode="production";',1))
routes=json.loads((ROOT/'routes.json').read_text());(out/'server/canonical-routes.mjs').write_text('export const canonicalRoutes='+json.dumps(routes,ensure_ascii=False)+';\n')
manifest={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
(out/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'artifact':str(out),'canonicalRoutes':len(routes),'files':len(manifest),'deployed':False,'entrypoint':'server/production-entry.mjs','assets':'assets','requiresExistingCloudflareConfiguration':True,'counterEnabled':release['counterEnabled']}))
