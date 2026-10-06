"""Versioned Mac mini recovery copy: Git history + working source + verified hashes."""
from pathlib import Path
import hashlib,tarfile,json,subprocess,datetime,platform
R=Path(__file__).resolve().parent.parent
host=platform.node()
if not host.lower().startswith('mac-mini-kamil'):raise SystemExit('Mac mini not verified: do not claim a Mac mini backup on this host')
D=Path.home()/'Documents/Hornigold-backups'/datetime.datetime.now().astimezone().strftime('%Y-%m-%d_%H%M%S-release23')
D.mkdir(parents=True,exist_ok=False)
subprocess.run(['git','bundle','create',str(D/'history.bundle'),'--all'],cwd=R,check=True,capture_output=True)
excluded={'.git','node_modules','_site','_pages','_production_ready','dist','.wrangler','__pycache__','.venv'}
files=[p for p in R.rglob('*') if p.is_file() and not any(x in excluded for x in p.relative_to(R).parts)]
manifest=[]
with tarfile.open(D/'working-source.tar.gz','w:gz') as tar:
 for p in files:
  rel=str(p.relative_to(R));tar.add(p,arcname=rel,recursive=False);manifest.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with tarfile.open(D/'working-source.tar.gz','r:gz') as tar:
 for f in manifest:
  if hashlib.sha256(tar.extractfile(f['path']).read()).hexdigest()!=f['sha256']:raise SystemExit('Backup readback mismatch: '+f['path'])
subprocess.run(['git','bundle','verify',str(D/'history.bundle')],cwd=R,check=True,capture_output=True)
summary={'host':host,'path':str(D),'sourceFiles':len(manifest),'files':manifest,'archives':[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [D/'history.bundle',D/'working-source.tar.gz']],'readbackVerified':True}
(D/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ('files','archives')}))
