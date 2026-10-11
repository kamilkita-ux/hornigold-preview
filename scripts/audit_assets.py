"""Asset integrity and rights inventory; missing provenance is never treated as a license."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent.parent;rows=[]
for p in (R/'site/assets').rglob('*'):
 if not p.is_file() or p.suffix.lower() not in ['.jpg','.jpeg','.png','.webp','.gif','.avif']:continue
 row={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rightsStatus':'Owner supplied project asset; complete rights chain not independently verified','author':None}
 try:
  with Image.open(p) as im:row.update(width=im.width,height=im.height,format=im.format);im.verify();row['decode']='pass'
 except Exception as e:row['decode']='fail';row['error']=type(e).__name__
 rows.append(row)
report={'date':'2026-10-11','images':len(rows),'failures':[r['path'] for r in rows if r['decode']!='pass'],'largeAssets':[r['path'] for r in rows if r['bytes']>500000],'items':rows,'remaining':'Property management must confirm copyright/permission for photographs; generated editorial illustrations must remain explicitly labelled.'}
p=R/'docs/implementation/evidence/image-inventory.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'images':len(rows),'failures':len(report['failures']),'over500KB':len(report['largeAssets'])}))
