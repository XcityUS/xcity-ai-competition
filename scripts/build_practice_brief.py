#!/usr/bin/env python3
"""Build the public practice PDF from brief/firm-track.en.md; preserve its cover.

Maintainer dependencies: reportlab, markdown, pypdf.
Run from any directory: python scripts/build_practice_brief.py
"""
from pathlib import Path
import io
import re
import xml.etree.ElementTree as ET
from html import escape
import markdown
from pypdf import PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'brief/firm-track.en.md'
OUTPUT = ROOT / 'brief/design-practice-brief.en.pdf'
W, H = 960, 540
INK, GOLD, BODY, BG = '#25221d', '#a2833e', '#49443c', '#f3eee6'
styles = {
 'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=12, leading=17, textColor=HexColor(BODY), spaceAfter=10),
 'h1': ParagraphStyle('H1', fontName='Helvetica', fontSize=31, leading=37, textColor=HexColor(INK), spaceAfter=20, keepWithNext=True),
 'h2': ParagraphStyle('H2', fontName='Helvetica', fontSize=25, leading=31, textColor=HexColor(INK), spaceBefore=18, spaceAfter=18, keepWithNext=True),
 'h3': ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=15, leading=21, textColor=HexColor(GOLD), spaceBefore=12, spaceAfter=10, keepWithNext=True),
 'table': ParagraphStyle('Table', fontName='Helvetica', fontSize=10.5, leading=14, textColor=HexColor(BODY)),
 'small': ParagraphStyle('Small', fontName='Helvetica', fontSize=10, leading=15, textColor=HexColor(BODY), spaceAfter=10),
}

def clean(text):
 return text.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u00a0',' ').replace('①','1.').replace('②','2.').replace('³','3').replace('²','2').replace('≤','<=')

def inline(node):
 text=escape(clean(node.text or ''))
 for c in node:
  inside=inline(c)
  if c.tag in ('strong','b'):text+='<b>'+inside+'</b>'
  elif c.tag in ('em','i'):text+='<i>'+inside+'</i>'
  elif c.tag=='code':text+='<font face="Courier" size="9">'+inside+'</font>'
  elif c.tag=='a':text+='<a color="'+GOLD+'" href="'+escape(c.attrib.get('href',''),quote=True)+'">'+inside+'</a>'
  elif c.tag=='br':text+='<br/>'
  else:text+=inside
  text+=escape(clean(c.tail or ''))
 return text

def page(canvas, doc):
 canvas.saveState();canvas.setFillColor(HexColor(BG));canvas.rect(0,0,W,H,stroke=0,fill=1)
 canvas.setStrokeColor(HexColor('#cfc1a5'));canvas.line(48,H-36,W-48,H-36)
 canvas.setFont('Helvetica',9);canvas.setFillColor(HexColor(GOLD));canvas.drawString(48,H-25,'XCITY / DESIGN PRACTICE CALL / CURRENT BRIEF')
 canvas.setFillColor(HexColor(BODY));canvas.setFont('Helvetica',8);canvas.drawString(48,22,'26 October 2026 | Registration and draft preparation; final submission dates pending')
 canvas.drawRightString(W-48,22,str(doc.page+1));canvas.restoreState()

root=ET.fromstring('<root>'+markdown.markdown(SOURCE.read_text(),extensions=['tables'])+'</root>')
story=[]
for node in root:
 if node.tag=='hr':continue
 if node.tag=='h1':story.append(Paragraph(inline(node),styles['h1']));continue
 if node.tag=='h2':
  story.append(Paragraph(inline(node),styles['h2']));continue
 if node.tag=='h3':story.append(Paragraph(inline(node),styles['h3']));continue
 if node.tag=='p':story.append(Paragraph(inline(node),styles['body']));continue
 if node.tag=='blockquote':
  for child in node:story.append(Paragraph(inline(child),styles['small']))
  continue
 if node.tag in ('ul','ol'):
  for index,child in enumerate(node):
   prefix=str(index+1)+'. ' if node.tag=='ol' else '- '
   story.append(Paragraph(prefix+inline(child),styles['body']))
  continue
 if node.tag=='table':
  rows=[[Paragraph(inline(c),styles['table']) for c in row] for row in node.iter('tr')]
  n=len(rows[0]);widths=[864/n]*n
  if n==3:widths=[190,340,334]
  if n==4:widths=[145,185,280,254]
  if n==2:widths=[210,654]
  table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
  table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),HexColor('#e4dac5')),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#f9f6f0'),HexColor('#f0e9dc')]),('LINEBELOW',(0,0),(-1,0),.7,HexColor(GOLD)),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#d8cfbd')),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
  story.extend([table,Spacer(1,16)])
body=io.BytesIO()
doc=SimpleDocTemplate(body,pagesize=(W,H),leftMargin=48,rightMargin=48,topMargin=58,bottomMargin=50,title='XCITY Design Practice Call - Current Brief',author='XCITY')
doc.build(story,onFirstPage=page,onLaterPages=page)
cover=PdfReader(OUTPUT)
writer=PdfWriter();cover.pages[0].scale_to(W,H);writer.add_page(cover.pages[0])
for p in PdfReader(body).pages:writer.add_page(p)
writer.add_metadata({'/Title':'XCITY Design Practice Call - Brief - 26 October 2026','/Author':'XCITY','/Subject':'Online registration, draft preparation and initial ideas up to 10 pages'})
tmp=OUTPUT.with_suffix('.new.pdf')
with tmp.open('wb')as f:writer.write(f)
tmp.replace(OUTPUT)
print('Built %s (%d pages)' % (OUTPUT,len(writer.pages)))
