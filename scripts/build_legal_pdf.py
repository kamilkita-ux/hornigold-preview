"""Create seven printable policy bundles; HTML remains the accessible alternative."""
from pathlib import Path
import json,shutil,sys
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject
ROOT=Path(__file__).resolve().parent.parent;BASE=ROOT.parent
FONT=ROOT/'legal/fonts'
pdfmetrics.registerFont(TTFont('Body',str(FONT/'DejaVuSans.ttf')));pdfmetrics.registerFont(TTFont('Bold',str(FONT/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('CJK',str(FONT/'NotoSansSC-Regular.ttf')))
cmap=pdfmetrics.getFont('CJK').face.charWidths
OUT=BASE/'output/pdf';OUT.mkdir(parents=True,exist_ok=True);DEST=ROOT/'site/documents';DEST.mkdir(exist_ok=True)
def markup(s,lang):
 s=s.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
 if lang!='zh-hans':return escape(s)
 chunks=[];last=None;chunk=''
 for c in s:
  font='CJK' if ord(c) in cmap else 'Body'
  if font!=last and chunk:chunks.append(f'<font name="{last}">{escape(chunk)}</font>');chunk=''
  last=font;chunk+=c
 if chunk:chunks.append(f'<font name="{last}">{escape(chunk)}</font>')
 return ''.join(chunks)
identity=json.loads((ROOT/'content/property-identity.json').read_text())
def identity_note(lang,style):
 info=identity[lang]
 return [Spacer(1,14),Paragraph(markup(info['tagline']+' '+info['description'],lang),style),Paragraph(markup(info['rating']+' '+info['ratingNote'],lang)+' <link href="'+escape(info['reviewUrl'])+'">'+markup(info['reviewLinkLabel'],lang)+'</link>',style)]
report=[]
for lang in ['pl','en','de','zh-hans','uk','es','it']:
 d=json.loads((ROOT/'legal'/f'{lang}.json').read_text());font='CJK' if lang=='zh-hans' else 'Body'
 body=ParagraphStyle('body',fontName=font,fontSize=10.0 if lang=='de' else 10.2,leading=14.5 if lang=='de' else 15.2,spaceAfter=9.5 if lang=='de' else 11,wordWrap='CJK' if lang=='zh-hans' else None,allowWidows=0,allowOrphans=0)
 title=ParagraphStyle('title',parent=body,fontName=font if lang=='zh-hans' else 'Bold',fontSize=18,leading=24,spaceAfter=18,keepWithNext=True)
 sub=ParagraphStyle('sub',parent=body,fontSize=8.5,leading=12,textColor=HexColor('#385449'))
 out=OUT/f'hornigold-policies-{lang}.pdf';doc=SimpleDocTemplate(str(out),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=45,bottomMargin=48,title=d['title'],author='Hornigold',subject='2026-10-09 | '+lang)
 story=[]
 for index,sec in enumerate(d['sections']):
  if index:story.append(PageBreak())
  story.extend([Paragraph('HORNIGOLD · 2026-10-09',sub),Paragraph(markup(sec['title'],lang),title)])
  if index==0:story.append(Paragraph(markup(d['intro'],lang),sub));story.append(Spacer(1,8))
  paragraphs=[Paragraph(markup(str(n)+'. '+p,lang),body) for n,p in enumerate(sec['paragraphs'],1)]
  sources=[Paragraph('<link href="'+escape(source['url'])+'">'+markup(source['title'],lang)+'</link> (2026-10-09)',ParagraphStyle('source',parent=sub,leading=10,spaceAfter=2)) for source in sec.get('sources',[])]
  if sources:
   story.extend(paragraphs[:-1]);story.append(KeepTogether([paragraphs[-1]]+sources))
  else:story.extend(paragraphs)
 story.extend(identity_note(lang,sub))
 def footer(c,doc):
  c.saveState();c.setFont('Body',8);c.setFillColor(HexColor('#385449'));c.drawString(48,25,'Hornigold · office@hornigold.pl');c.drawRightString(547,25,str(doc.page));c.restoreState()
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
 reader=PdfReader(out);writer=PdfWriter();writer.clone_document_from_reader(reader);writer._root_object[NameObject('/Lang')]=TextStringObject('zh-Hans' if lang=='zh-hans' else lang)
 with out.open('wb') as f:writer.write(f)
 reader=PdfReader(out);text=' '.join(p.extract_text() for p in reader.pages)
 assert '\ufffd' not in text and '6343076075' in text and '0001265196' in text,lang
 shutil.copyfile(out,DEST/out.name)
 report.append({'lang':lang,'pages':len(reader.pages),'bytes':out.stat().st_size,'paragraphs':sum(len(s['paragraphs']) for s in d['sections']),'file':str(out),'taggedPDFUA':False})
(BASE/'output/legal-pdf-v23-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))

if '--bundles-only' in sys.argv:raise SystemExit(0)

# Standalone full standards and an easier-to-read child edition in every language.
standalone=[]
for lang in ['pl','en','de','zh-hans','uk','es','it']:
 d=json.loads((ROOT/'legal'/f'{lang}.json').read_text());font='CJK' if lang=='zh-hans' else 'Body'
 for sec in d['sections']:
  if sec['id'] not in ('safeguarding','safeguarding-children'):continue
  child=sec['id']=='safeguarding-children'
  body=ParagraphStyle('standalone-body',fontName=font,fontSize=12 if child else (11.5 if lang=='zh-hans' else 10.2),leading=18 if child or lang=='zh-hans' else 14.5,spaceAfter=13 if child else 10,wordWrap='CJK' if lang=='zh-hans' else None,allowWidows=0,allowOrphans=0)
  title=ParagraphStyle('standalone-title',parent=body,fontName=font if lang=='zh-hans' else 'Bold',fontSize=20,leading=27,spaceAfter=20,keepWithNext=True)
  sub=ParagraphStyle('standalone-sub',parent=body,fontSize=9,leading=13,textColor=HexColor('#385449'))
  out=OUT/f'hornigold-{sec["id"]}-{lang}.pdf'
  doc=SimpleDocTemplate(str(out),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=45,bottomMargin=48,title=sec['title'],author='Hornigold',subject='2026-10-09 | '+lang)
  story=[Paragraph('HORNIGOLD · 2026-10-09',sub),Paragraph(markup(sec['title'],lang),title)]
  for n,p in enumerate(sec['paragraphs'],1):story.append(Paragraph(markup(str(n)+'. '+p,lang),body))
  story.extend(identity_note(lang,sub))
  doc.build(story,onFirstPage=footer,onLaterPages=footer)
  reader=PdfReader(out);writer=PdfWriter();writer.clone_document_from_reader(reader);writer._root_object[NameObject('/Lang')]=TextStringObject('zh-Hans' if lang=='zh-hans' else lang)
  with out.open('wb') as f:writer.write(f)
  reader=PdfReader(out);assert all(p.extract_text().strip() for p in reader.pages),str(out)
  shutil.copyfile(out,DEST/out.name)
  standalone.append({'lang':lang,'edition':sec['id'],'pages':len(reader.pages),'file':str(out),'bytes':out.stat().st_size,'taggedPDFUA':False})
(BASE/'output/safeguarding-pdf-check.json').write_text(json.dumps(standalone,ensure_ascii=False,indent=2)+'\n');print(json.dumps(standalone,ensure_ascii=False))
