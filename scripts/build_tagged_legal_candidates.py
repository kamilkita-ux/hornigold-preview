"""Build local tagged candidates from approved JSON; never writes site/ or certifies PDF/UA."""
from pathlib import Path
from html import escape
import argparse, collections, datetime, hashlib, json, re, subprocess, os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
ROOT=Path(__file__).resolve().parents[1]
LANGS=('pl','en','de','zh-hans','uk','es','it')

def source_html(data, identity, lang, edition):
 sections=data['sections'] if edition=='policies' else [s for s in data['sections'] if s['id']==edition]
 if not sections:raise ValueError('Missing approved section: '+edition)
 title=data['title'] if edition=='policies' else sections[0]['title']
 html_lang='zh-Hans' if lang=='zh-hans' else lang
 extra_css=('body{font-size:10.5pt}' if lang=='zh-hans' else '')+('body{font-size:12pt}' if edition=='safeguarding-children' else '')
 parts=['<!doctype html><html lang="'+html_lang+'"><head><meta charset="utf-8"><title>'+escape(title)+'</title><style>@page{size:A4;margin:18mm}body{font-family:DejaVu Sans,Noto Sans SC,sans-serif;font-size:11pt;color:#173b33;line-height:1.35}h1{font-size:21pt;line-height:1.4;margin:0 0 14pt}h2{font-size:17pt;line-height:1.4;margin:0 0 12pt;page-break-before:always}h2.first{page-break-before:auto}li{margin-bottom:8pt}h1,h2{page-break-after:avoid}p.identity{font-size:9pt;margin-top:18pt}p.source{font-size:8.5pt;line-height:1.15;margin:2pt 0}'+extra_css+'</style></head><body><h1>'+escape(title)+'</h1>']
 expected=[title]
 if edition=='policies':parts+=['<p>'+escape(data['intro'])+'</p>'];expected.append(data['intro'])
 for n,sec in enumerate(sections):
  if edition=='policies':parts+=['<h2 class="'+('first' if n==0 else '')+'">'+escape(sec['title'])+'</h2>'];expected.append(sec['title'])
  parts+=['<ol>']+['<li>'+escape(p)+'</li>' for p in sec['paragraphs']]+['</ol>'];expected+=sec['paragraphs']
  for s in sec.get('sources',[]):parts+=['<p class="source"><a href="'+escape(s['url'],quote=True)+'">'+escape(s['title'])+'</a> (2026-10-09)</p>'];expected.append(s['title'])
 note=identity['tagline']+' '+identity['description']
 rating=identity['rating']+' '+identity['ratingNote']
 parts+=['<p class="identity">'+escape(note)+'</p><p>'+escape(rating)+' <a href="'+escape(identity['reviewUrl'],quote=True)+'">'+escape(identity['reviewLinkLabel'])+'</a></p><p>Hornigold · office@hornigold.pl</p></body></html>'];expected+=[note,rating,identity['reviewLinkLabel']]
 return ''.join(parts),expected

def normalize(text):return re.sub(r'\s+','',text).replace('\xad','')

def finish_and_check(path, expected, lang, pdftotext):
 reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
 writer.root_object[NameObject('/Lang')]=TextStringObject('zh-Hans' if lang=='zh-hans' else lang)
 structure=writer.root_object.get('/StructTreeRoot')
 if not structure:raise ValueError('Missing structure tree')
 roles=structure.get_object().get('/RoleMap')
 # Writer/Web imports our sole HTML h1 as this custom style; its original mapping is P.
 # This correction is scoped to HTML generated here, never arbitrary input PDFs.
 if roles and '/Heading 1' in roles:roles[NameObject('/Heading 1')]=NameObject('/H1')
 temp=path.with_suffix('.checked.pdf')
 with temp.open('wb') as f:writer.write(f)
 temp.replace(path);reader=PdfReader(path);catalog=reader.trailer['/Root'];tree=catalog['/StructTreeRoot'];rolemap=tree.get('/RoleMap',{});tags=collections.Counter();seen=set()
 def walk(obj):
  if hasattr(obj,'get_object'):obj=obj.get_object()
  if isinstance(obj,list):
   for i in obj:walk(i)
  elif isinstance(obj,dict):
   if id(obj) in seen:return
   seen.add(id(obj))
   if '/S' in obj:tags[str(rolemap.get(obj['/S'],obj['/S']))]+=1
   if '/K' in obj:walk(obj['/K'])
 walk(tree)
 secondary_text=''.join(p.extract_text() for p in reader.pages)
 extraction=subprocess.run([pdftotext,'-layout',str(path),'-'],capture_output=True,text=True,check=True,timeout=30)
 text=extraction.stdout;missing=[i for i,s in enumerate(expected) if normalize(s) not in normalize(text)]
 secondary_missing=[i for i,s in enumerate(expected) if normalize(s) not in normalize(secondary_text)]
 language=str(catalog.get('/Lang',''));correct_lang=language.lower().startswith(lang.split('-')[0])
 if missing or not correct_lang or tags['/H1']!=1 or not tags['/LI'] or not catalog.get('/MarkInfo',{}).get('/Marked'):raise ValueError(str({'path':str(path),'missingTextItems':missing,'lang':language,'tags':dict(tags)}))
 return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':len(reader.pages),'language':language,'tags':dict(tags),'expectedTextItems':len(expected),'missingTextItems':missing,'textExtractor':'Poppler layout','pypdfExtractionMissingItems':secondary_missing,'tagged':True,'pdfUAValidated':False,'visualReviewCompleted':False}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--soffice',required=True);ap.add_argument('--pdftotext',required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 out=args.output.resolve()
 if out==ROOT/'site' or ROOT/'site' in out.parents:raise SystemExit('Candidate output must remain outside site/')
 out.mkdir(parents=True,exist_ok=False);identity=json.loads((ROOT/'content/property-identity.json').read_text());jobs=[]
 for lang in LANGS:
  data=json.loads((ROOT/'legal'/f'{lang}.json').read_text())
  for edition in ('policies','safeguarding','safeguarding-children'):
   html,expected=source_html(data,identity[lang],lang,edition);source=out/f'hornigold-{edition}-{lang}.html';source.write_text(html);jobs.append((source,expected,lang))
 options=json.dumps({'UseTaggedPDF':{'type':'boolean','value':'true'},'ExportBookmarks':{'type':'boolean','value':'true'}})
 command=[args.soffice,'-env:UserInstallation='+(out/'lo-profile').as_uri(),'--headless','--convert-to','pdf:writer_web_pdf_Export:'+options,'--outdir',str(out)]+[str(s) for s,_,_ in jobs]
 fontconfig=out/'fontconfig.xml'
 fontconfig.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>'+escape(str(ROOT/'legal/fonts'))+'</dir><cachedir>'+escape(str(out/'font-cache'))+'</cachedir></fontconfig>')
 environment={**os.environ,'FONTCONFIG_FILE':str(fontconfig)}
 result=subprocess.run(command,capture_output=True,text=True,timeout=180,env=environment);(out/'conversion.log').write_text(result.stdout+'\n'+result.stderr)
 if result.returncode:raise SystemExit('Conversion failed; inspect local conversion.log')
 report={'createdAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'approved legal/*.json and content/property-identity.json','published':False,'pdfUAValidated':False,'limits':['Structural and text checks do not prove full accessibility or legal validity.','Manual reading-order, link navigation, font and visual review are still required.'],'documents':[finish_and_check(s.with_suffix('.pdf'),expected,lang,args.pdftotext) for s,expected,lang in jobs]}
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'documents':len(report['documents']),'tagged':True,'published':False,'pdfUAValidated':False,'report':str(out/'report.json')}))
if __name__=='__main__':main()
