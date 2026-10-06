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
for obj in objects:
 oid,_,name=obj.partition(' ')
 if subprocess.check_output(['git','cat-file','-t',oid],cwd=root,text=True).strip()!='blob':continue
 data=subprocess.check_output(['git','cat-file','blob',oid],cwd=root)
 if b'\x00' not in data and any(r.search(data) for r in compiled):findings.append({'object':oid,'path':name,'reason':'potential historical secret'})
print(json.dumps({'files':count,'gitObjects':len(objects),'findings':findings}));raise SystemExit(bool(findings))
