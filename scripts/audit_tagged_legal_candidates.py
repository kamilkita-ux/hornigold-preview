"""Read-only structure/content linkage checks; not PDF/UA or screen-reader certification."""
from pathlib import Path
import argparse,collections,json
from pypdf import PdfReader
from pypdf.generic import ContentStream,IndirectObject

def ref(obj):
 if isinstance(obj,IndirectObject):return (obj.idnum,obj.generation)
 obj=getattr(obj,'indirect_reference',None)
 return (obj.idnum,obj.generation) if obj else None

def audit(path):
 reader=PdfReader(path);catalog=reader.trailer['/Root'];page_ids={ref(p):n for n,p in enumerate(reader.pages)};physical=[];annotations={};missing_fonts=[]
 for n,page in enumerate(reader.pages):
  stream=ContentStream(page.get_contents(),reader)
  for operands,operator in stream.operations:
   if operator==b'BDC' and len(operands)>1:
    props=operands[1]
    if isinstance(props,IndirectObject):props=props.get_object()
    if isinstance(props,dict) and '/MCID' in props:physical.append((n,int(props['/MCID'])))
  for annotation in page.get('/Annots',[]):
   obj=annotation.get_object()
   if obj.get('/Subtype')=='/Link':annotations[ref(annotation)]=str(obj.get('/A',{}).get('/URI',''))
  for font_ref in page.get('/Resources',{}).get('/Font',{}).values():
   font=font_ref.get_object();descendants=font.get('/DescendantFonts',[font])
   for child in descendants:
    descriptor=child.get_object().get('/FontDescriptor',{})
    if not any(k in descriptor for k in ['/FontFile','/FontFile2','/FontFile3']):missing_fonts.append({'page':n+1,'font':str(font.get('/BaseFont'))})
 logical=[];linked=[];seen=set();tags=collections.Counter();rolemap=catalog.get('/StructTreeRoot',{}).get('/RoleMap',{})
 def walk(obj,page=None):
  if isinstance(obj,IndirectObject):obj=obj.get_object()
  if isinstance(obj,list):
   for x in obj:walk(x,page)
  elif isinstance(obj,dict):
   if id(obj) in seen:return
   seen.add(id(obj));page=obj.get('/Pg',page)
   if '/S' in obj:tags[str(rolemap.get(obj['/S'],obj['/S']))]+=1
   if obj.get('/Type')=='/OBJR':linked.append(ref(obj.get('/Obj')))
   if '/MCID' in obj:logical.append((page_ids.get(ref(page)),int(obj['/MCID'])))
   if '/K' in obj:walk(obj['/K'],page)
  elif isinstance(obj,int):logical.append((page_ids.get(ref(page)),int(obj)))
 walk(catalog.get('/StructTreeRoot'))
 counts=collections.Counter(logical);physical_counts=collections.Counter(physical);errors=[]
 expected_lang='zh-Hans' if path.stem.endswith('-zh-hans') else path.stem.rsplit('-',1)[-1]
 if not catalog.get('/StructTreeRoot') or not catalog.get('/MarkInfo',{}).get('/Marked'):errors.append('Missing marked structure tree')
 if tags['/H1']!=1 or not tags['/LI'] or not logical:errors.append('Missing heading, list or marked content')
 if str(catalog.get('/Lang','')).lower()!=expected_lang.lower():errors.append('Incorrect document language')
 if counts!=physical_counts:errors.append('Marked content / structure references mismatch')
 if logical!=physical:errors.append('Structure order differs from page content order')
 if any(v>1 for v in counts.values()):errors.append('Duplicate structure content reference')
 if set(linked)!=set(annotations):errors.append('Link annotation / structure references mismatch')
 if missing_fonts:errors.append('Font not embedded')
 if any(not u.startswith('https://') for u in annotations.values()):errors.append('Unexpected link protocol')
 return {'file':path.name,'pages':len(reader.pages),'markedContentReferences':len(logical),'links':len(annotations),'structureLinkReferences':len(linked),'embeddedFonts':not missing_fonts,'missingFonts':missing_fonts,'errors':errors}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--report',type=Path);args=ap.parse_args();rows=[audit(p) for p in sorted(args.directory.glob('*.pdf'))]
 expected={f'hornigold-{edition}-{lang}.pdf' for edition in ('policies','safeguarding','safeguarding-children') for lang in ('pl','en','de','zh-hans','uk','es','it')}
 if {x['file'] for x in rows}!=expected:raise SystemExit('Expected exactly the 21 named legal PDFs')
 report={'documents':rows,'errors':sum(len(r['errors']) for r in rows),'limits':['Technical structure linkage and ordering only; manual semantic reading-order and assistive-technology acceptance remain unverified.']};(args.report or args.directory/'structure-linkage-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));raise SystemExit(bool(report['errors']))
if __name__=='__main__':main()
