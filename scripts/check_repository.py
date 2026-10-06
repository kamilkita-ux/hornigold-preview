"""Conservative secret-pattern and private-file scan of working files and Git history.
Reports paths/hashes only, never matching content. This is not proof of absence of all secrets.
"""
from pathlib import Path
import re, subprocess, json
root=Path(__file__).resolve().parent.parent
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'gh[pousr]_[A-Za-z0-9]{30,}',rb'github_pat_[A-Za-z0-9_]{40,}',rb'AKIA[0-9A-Z]{16}',rb'(?i)(?:password|api_secret|access_token)\s*[=:]\s*[\x22\x27][^\x22\x27\s]{8,}[\x22\x27]']
compiled=[re.compile(p) for p in patterns];findings=[];count=0
files=[p for p in root.rglob('*') if p.is_file() and not any(x in p.relative_to(root).parts for x in ('.git','_site','node_modules','.venv','__pycache__'))]
for p in files:
 if p.suffix.lower() in ('.db','.sqlite','.sqlite3','.eml','.msg','.key','.pem') or p.name.startswith('.env'):findings.append({'path':str(p.relative_to(root)),'reason':'private-file type'})
 data=p.read_bytes()
 if b'\x00' not in data and any(r.search(data) for r in compiled):findings.append({'path':str(p.relative_to(root)),'reason':'potential secret'})
 count+=1
objects=subprocess.check_output(['git','rev-list','--objects','--all'],cwd=root,text=True).splitlines()
with subprocess.Popen(['git','cat-file','--batch'],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE) as batch:
 for obj in objects:
  oid,_,name=obj.partition(' ')
  batch.stdin.write((oid+'\n').encode());batch.stdin.flush()
  header=batch.stdout.readline().decode().strip().split()
  if len(header)!=3:raise RuntimeError('Cannot verify Git object: '+oid)
  size=int(header[2]);data=batch.stdout.read(size)
  if len(data)!=size or batch.stdout.read(1)!=b'\n':raise RuntimeError('Incomplete Git object scan: '+oid)
  if header[1]=='blob' and b'\x00' not in data and any(r.search(data) for r in compiled):findings.append({'object':oid,'path':name,'reason':'potential historical secret'})
 batch.stdin.close();batch.wait()
 if batch.returncode:raise RuntimeError('Git history scan failed')
print(json.dumps({'files':count,'gitObjects':len(objects),'findings':findings}));raise SystemExit(bool(findings))
