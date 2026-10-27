import json,re,html,base64,hashlib,shutil,textwrap,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A3,landscape
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
P=Path(__file__).resolve().parents[1];O=P/'pages';OUT=P.parents[4]/'outputs/everyday-city';OUT.mkdir(parents=True,exist_ok=True);BG='#f5f1e8';INK='#263b3b';W,H=landscape(A3)
# Raster sheets are authored at 150 dpi A3. The PDFs retain legible English typography.
font='/System/Library/Fonts/Supplemental/Arial.ttf';bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def F(size,b=False):return ImageFont.truetype(bold if b else font,size)
size=(2481,1753)
def image_sheet(key,title,sub,path,cover=False):
 im=Image.new('RGB',size,BG);d=ImageDraw.Draw(im);d.text((112,74),'THE EVERYDAY CITY',font=F(26,True),fill=INK)
 d.text((112,144),title,font=F(56 if cover else 44,True),fill=INK);d.text((112,225),sub,font=F(23),fill=INK)
 src=Image.open(P/path).convert('RGB');src.thumbnail((2257,1290 if cover else 1250));im.paste(src,((size[0]-src.width)//2,310))
 d.text((112,1665),'Jingyuan Huang | XCITY | Concept design review | 27 October 2026',font=F(20),fill=INK)
 d.text((112,1615),'Concept rendering over original massing; details and eye-level interpretation are not surveyed evidence.',font=F(19),fill=INK)
 dest=O/(key+'.png');im.save(dest);return dest
cover=image_sheet('00-cover','THE EVERYDAY CITY','Homes, shared ground and public life before production-led expansion.','media/district-finished.png',True)
finished={k:image_sheet(k+'-finished',k+' / '+n,'Aerial concept view + eye-level experience / same design place',f'media/{k}-finished.png') for k,n in [('A01','Courtyard Homes'),('B03','Useful Compute'),('C02','Working Farm Edge')]}
find=lambda n:next(O.glob(f'{n:02d}-*.png'))
seq=[cover]+[find(n) for n in [1,2,3,4,5,17,6,18,7,19,8,9,10,11]]+[finished['A01'],find(12),finished['B03'],find(13),finished['C02']]+[find(n) for n in [14,15,16]]
main=P/'drawings/everyday-city-design-review.pdf';c=canvas.Canvas(str(main),pagesize=(W,H));c.setTitle('THE EVERYDAY CITY | Design Review');c.setAuthor('Jingyuan Huang')
for i,p in enumerate(seq,1):
 buf=io.BytesIO();Image.open(p).convert('RGB').save(buf,format='JPEG',quality=90);buf.seek(0);c.drawImage(ImageReader(buf),0,0,width=W,height=H,preserveAspectRatio=True,anchor='c');c.setFillColor(INK);c.setFont('Helvetica',7);c.drawRightString(W-20,10,f'{i} / {len(seq)}');c.showPage()
c.save()
# Separate technical appendix: raw controls, QA and numerical assumptions; controls never substitute finished main views.
tech=P/'drawings/everyday-city-technical-appendix.pdf';c=canvas.Canvas(str(tech),pagesize=(W,H));c.setTitle('THE EVERYDAY CITY | Technical Appendix');style=ParagraphStyle('body',fontName='Helvetica',fontSize=11,leading=16,textColor=INK)
count=0
def header(title):
 c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(INK);c.setFont('Helvetica-Bold',22);c.drawString(42,H-54,title);c.setFont('Helvetica',9);c.drawString(42,25,'THE EVERYDAY CITY | Technical evidence, not design approval | Jingyuan Huang | 27 October 2026')
def end():
 global count
 count+=1;c.setFont('Helvetica',8);c.drawRightString(W-30,25,str(count));c.showPage()
header('Geometry and method audit');qa=json.loads((P/'report/geometry-qa.json').read_text());y=H-100
for k in ['source_commit','source_boundary_revision','phase_one_planar_km2','housing_buildings','dwellings','residents_scenario','jobs_scenario','interfaces','buildings','people_path_building_conflict_m','building_fixed_overlap_m2','building_channel_screen_overlap_m2','building_flood_screen_overlap_m2','land_partition_gap_m2']:
 c.setFont('Helvetica',12);c.drawString(45,y,k);c.drawString(420,y,str(qa.get(k)));y-=26
p=Paragraph('Planar areas and geodesic published metrics have different methods. Flood and channel tests use issued preliminary screening. A/B/C IDs follow the current brief. Automatic file, geometry and numerical checks are separate from independent design review; no design approval is claimed.',style);p.wrap(W-100,150);p.drawOn(c,45,85);end()
for key in ['district','A01','B03','C02']:
 header(key+' / original geometry control');p=P/'media/controls'/f'{key}-aerial.png';c.drawImage(str(p),45,85,width=W-90,height=H-190,preserveAspectRatio=True,anchor='c');end()
for title,items in [('Declared assumptions',json.loads((P/'assumptions.json').read_text())['assumptions']),('Source and boundary record',[{'id':x['id'],'topic':x['title'],'value':x['url'],'basis':x['used_for']} for x in json.loads((P/'sources.json').read_text())['sources']])]:
 header(title);y=H-100
 for a in items:
  p=Paragraph('<b>'+html.escape(a['id']+' / '+a['topic'])+'</b><br/>'+html.escape(str(a['value']))+'<br/>'+html.escape(a['basis']),style);w,h=p.wrap(W-100,H-150)
  if y-h<65:end();header(title+' / continued');y=H-100
  p.drawOn(c,45,y-h);y-=h+24
 end()
header('Hourly energy model and resource accounts');e=json.loads((P/'report/energy-results.json').read_text());y=H-100
for k,v in e.items():
 p=Paragraph('<b>'+html.escape(k)+'</b>: '+html.escape(str(v)),style);w,h=p.wrap(W-100,200);p.drawOn(c,45,y-h);y-=h+18
p=Paragraph('Full 8,760-row model: report/hourly-energy.csv. Gross-use water account: 891,748.4 m3/year. Reuse: 180,000. Delivered fresh: 711,748.4. Distribution loss: 40,000. Required abstraction scenario: 751,748.4. All supply rights unverified; the fixed living-quarter demand is additional and unknown.',style);w,h=p.wrap(W-100,200);p.drawOn(c,45,100);end();c.save()
# Self-contained HTML review, embedding the presentation sheets so it can be shared without a broken asset folder.
images=[]
for i,p in enumerate(seq,1):
 b64=base64.b64encode(p.read_bytes()).decode();images.append(f'<section id="p{i}"><p class="page">{i:02d} / {len(seq):02d}</p><img src="data:image/png;base64,{b64}" alt="English design presentation sheet {i}" loading="lazy"></section>')
htmltext='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>THE EVERYDAY CITY | Design Review</title><style>body{margin:0;background:#ebe6da;color:#263b3b;font:16px/1.6 Arial,sans-serif}header{padding:40px 5vw;background:#263b3b;color:#f5f1e8}h1{font-size:clamp(32px,5vw,64px);margin:0}header p{max-width:780px}a{color:inherit}nav{position:sticky;top:0;background:#f5f1e8;padding:14px 5vw;display:flex;gap:22px;flex-wrap:wrap;z-index:2;border-bottom:1px solid #b7b0a1}section{max-width:1500px;margin:32px auto;scroll-margin-top:80px}img{width:100%;height:auto;display:block}.page{padding:0 16px;margin-bottom:6px;font-size:12px}footer{padding:30px 5vw}</style><header><p>XCITY / INDEPENDENT NEW PROPOSAL / 27 OCTOBER 2026</p><h1>THE EVERYDAY CITY</h1><p>Homes, shared ground and public life before production-led expansion.</p><p>Jingyuan Huang / 1,440 homes / 3,600 residents / six neighbourhoods / A01 + B03 + C02</p><p>Concept review. Resource capacities are scenarios; rights and engineering remain unverified. The existing published proposal is unchanged.</p></header><nav><a href="#p2">Whole site</a><a href="#p5">First district</a><a href="#p14">Three nodes</a><a href="#p21">Phasing</a><a href="#p23">Indicators</a></nav>'''+''.join(images)+'''<footer>English final presentation. Original geometry, calculations and imagery registered in the working package. Current organiser node-ID contract still requires migration; no automatic approval or public competition submission is claimed.</footer></html>'''
# Add the complete English design argument after the visual reading sequence.
md=(P/'proposal.md').read_text();blocks=[]
for block in md.split('\n\n'):
 block=block.strip()
 if not block or block.startswith('!['):continue
 if block.startswith('#'):
  n=min(len(block)-len(block.lstrip('#')),4);blocks.append(f'<h{n}>'+html.escape(block.lstrip('#').strip())+f'</h{n}>')
 elif block.startswith('|'):
  rows=[]
  for ln in block.splitlines():
   if set(ln.replace('|','').replace('-','').replace(':','').strip())==set():continue
   rows.append('<tr>'+''.join('<td>'+html.escape(v.strip())+'</td>' for v in ln.strip('|').split('|'))+'</tr>')
  blocks.append('<table>'+''.join(rows)+'</table>')
 else:blocks.append('<p>'+html.escape(block).replace('\n',' ')+'</p>')
article='<article id="statement" style="max-width:950px;margin:60px auto;padding:30px;background:#f5f1e8">'+''.join(blocks)+'</article>'
htmltext=htmltext.replace('</nav>','<a href="#statement">Full design statement</a></nav>').replace('<footer>',article+'<footer>')
(P/'report/index.html').write_text(htmltext);(OUT/'index.html').write_text(htmltext)
for f in [main,tech]:shutil.copy2(f,OUT/f.name)
shutil.copy2(P/'media/district-finished.png',OUT/'district-preview.png')
(P/'drawings/presentation-index.json').write_text(json.dumps({'status':'concept_review_not_formal_pass','main_pages':len(seq),'technical_pages':count,'main_page_sources':[str(p.relative_to(P)) for p in seq]},indent=2))
print('Main',len(seq),'pages; appendix',count,'pages; output',OUT)
