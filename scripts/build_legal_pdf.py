"""Create seven printable policy bundles; HTML remains the accessible alternative."""
from pathlib import Path
import json,shutil
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
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
report=[]
for lang in ['pl','en','de','zh-hans','uk','es','it']:
 d=json.loads((ROOT/'legal'/f'{lang}.json').read_text());font='CJK' if lang=='zh-hans' else 'Body'
 body=ParagraphStyle('body',fontName=font,fontSize=10.0 if lang=='de' else 10.2,leading=14.5 if lang=='de' else 15.2,spaceAfter=9.5 if lang=='de' else 11,wordWrap='CJK' if lang=='zh-hans' else None,allowWidows=0,allowOrphans=0)
 title=ParagraphStyle('title',parent=body,fontName=font if lang=='zh-hans' else 'Bold',fontSize=18,leading=24,spaceAfter=18,keepWithNext=True)
 sub=ParagraphStyle('sub',parent=body,fontSize=8.5,leading=12,textColor=HexColor('#385449'))
 out=OUT/f'hornigold-policies-{lang}.pdf';doc=SimpleDocTemplate(str(out),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=45,bottomMargin=48,title=d['title'],author='Hornigold',subject='2026-10-06 | '+lang)
 story=[]
 for index,sec in enumerate(d['sections']):
  if index:story.append(PageBreak())
  story.extend([Paragraph('HORNIGOLD · 2026-10-06',sub),Paragraph(markup(sec['title'],lang),title)])
  if index==0:story.append(Paragraph(markup(d['intro'],lang),sub));story.append(Spacer(1,8))
  for n,p in enumerate(sec['paragraphs'],1):story.append(Paragraph(markup(str(n)+'. '+p,lang),body))
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
