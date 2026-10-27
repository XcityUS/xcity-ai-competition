"""Compose V11 public presentation, A0 and separate camera/control appendix."""
import json,math,io,shutil,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly,PathPatch
from matplotlib.path import Path as MP
from matplotlib.font_manager import findfont
from shapely import make_valid
from shapely.geometry import shape,box,Point
from shapely.geometry.polygon import orient
from shapely.ops import transform
from pyproj import Transformer
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor,Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader,PdfWriter
P=Path(__file__).resolve().parents[1];R=P.parents[2];V=P/'reviews/complete-city-v9';V10=P/'reviews/presentation-v10';O=P/'reviews/presentation-v11';G=V10/'scene/geometry';D=O/'drawings';D.mkdir(exist_ok=True);OUT=R.parents[1]/'outputs/agua-finita-v11';OUT.mkdir(exist_ok=True)
BG='#F8F6F0';INK='#263C43';MUT='#68766F';ACC='#A56F50'
for name,weight in [('Body','normal'),('Bold','bold')]:pdfmetrics.registerFont(TTFont(name,findfont(matplotlib.font_manager.FontProperties(family='DejaVu Sans',weight=weight))))
T=Transformer.from_crs(4326,32719,always_xy=True).transform
load=lambda f:[(make_valid(transform(T,shape(x['geometry']))),x['properties']) for x in json.loads(f.read_text())['features']]
land=load(G/'land_use.geojson');build=load(G/'buildings.geojson');roads=load(G/'movement.geojson');nodes=load(G/'nodes.geojson');regions=load(V/'geometry/planning_regions.geojson');phases=load(G/'phasing.geojson');scope=load(R/'brief/site-package/boundaries/scope_9_13.geojson');channels=load(R/'brief/site-package/water/channels_dem.geojson');fixed=load(R/'brief/site-package/pilot-area/pilot_area.geojson')+load(R/'brief/site-package/pilot-area/pilot_living_area.geojson')
cams=json.loads((O/'camera-registry.json').read_text());metrics=json.loads((V/'metrics.json').read_text());programme=metrics['phases'];resource=metrics['resources'];qas=json.loads((V/'qa.json').read_text())
COL={'residential':'#DECBAA','mixed_use':'#C99172','school':'#A5BCC8','daily_centre':'#C69E74','dry_park':'#B6C19F','terrain_review':'#E8E5DC','streets':'#B5BFC2','dry_open_space':'#EBE5D8','public_commons':'#C39177','civic':'#B78C7C','arrival':'#B2BFC4','culture':'#BD99A2','compute':'#899FAB','industry':'#A8AB99','infrastructure':'#9CADAA','energy':'#D0C08A','agriculture':'#B5C39B','logistics':'#AE99AA','operational_reserve':'#E4E1D7'}
PC={1:'#B98062',2:'#9BAF92',3:'#8EA5B4'}
URBAN=(573350,6555750,576100,6559150);SW=(572100,6551700,576200,6559250);PRODUCT=(573000,6551800,574850,6554800)
def polys(g):
 if g.is_empty:return
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from polys(q)
def fill(a,g,color,lw=.3,edge='none',alpha=1):
 for q in polys(g):
  q=orient(q,1);v=[];codes=[]
  for ring in [q.exterior,*q.interiors]:
   z=np.asarray(ring.coords)/1000;v.extend(z);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(z)-2)+[MP.CLOSEPOLY])
  a.add_patch(PathPatch(MP(v,codes),facecolor=color,edgecolor=edge,lw=lw,alpha=alpha))
def line(a,g,color=INK,lw=.5,ls='-'):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  x,y=np.asarray(g.coords).T/1000;a.plot(x,y,color=color,lw=lw,ls=ls)
 elif g.geom_type in ['Polygon','MultiPolygon']:line(a,g.boundary,color,lw,ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(a,q,color,lw,ls)
def lab(a,pt,text,sz=9):
 p=pt if pt.geom_type=='Point' else pt.representative_point();a.text(p.x/1000,p.y/1000,text,ha='center',va='center',fontsize=sz,color=INK,bbox=dict(facecolor=BG,alpha=.9,pad=2,edgecolor='none'))
def mapdraw(name,bounds,mode='land',node=None,figsize=(7,7)):
 f,a=plt.subplots(figsize=figsize,facecolor=BG);a.set_facecolor(BG);w=box(*bounds)
 if mode=='regions':
  for g,p in regions:fill(a,g,p['color'],.8,INK);lab(a,g,p['id'],12)
 else:
  for g,p in scope:fill(a,g.intersection(w),'#EEEADF',.6,INK)
  for g,p in land:
   if not g.intersects(w):continue
   fill(a,g.intersection(w),PC.get(p.get('phase'),BG) if mode=='phase' else COL.get(p['use'],'#DDD8CE'),.2,'#ACA797')
  for g,p in build:
   if g.intersects(w) and mode!='phase':fill(a,g,'#A36D4E' if p.get('form')=='canopy' else '#777C79',.2)
  for g,p in roads:
   if g.intersects(w):line(a,g.intersection(w),'#547C85' if p.get('network')=='people' else '#7F969E',.5)
 for g,p in channels:
  if g.intersects(w):line(a,g.intersection(w),'#8DACA9',1 if node=='C03' else .5)
 for g,p in fixed:
  if g.intersects(w):fill(a,g.intersection(w),'#8A8066',.5,INK)
 for g,p in nodes:
  if g.intersects(w) and (mode=='locator' or node==p['node_id']):line(a,g.intersection(w),'#A4543D',1.3);lab(a,g,p['node_id'],10)
 if mode=='locator':
  for nid in ['A03','B03','C03']:
   c=next(p for p in cams if p['id']==nid+'-aerial');e=np.array(c['position_utm19s'][:2]);t=np.array(c['target_utm19s'][:2]);a.annotate('',xy=t/1000,xytext=e/1000,arrowprops=dict(arrowstyle='->',lw=1.1,color='#324D67'))
 if node:
  for c in cams:
   if c['id'].startswith(node):
    e=np.array(c['position_utm19s'][:2]);t=np.array(c['target_utm19s'][:2]);v=t-e;l=np.linalg.norm(v);u=v/l;n=np.array([-u[1],u[0]]);reach=min(l,500);half=reach*math.tan(math.radians(c['fov_degrees']/2))
    a.add_patch(Poly(np.array([e,e+u*reach+n*half,e+u*reach-n*half])/1000,closed=True,facecolor='#477C9C',alpha=.10,edgecolor='#477C9C',lw=.7));lab(a,Point(*e),'E' if 'eye' in c['id'] else 'A',7)
 x0,y0,x1,y1=np.array(bounds)/1000;a.set(xlim=(x0,x1),ylim=(y0,y1));a.set_aspect('equal');a.axis('off')
 length=10 if x1-x0>20 else (.5 if x1-x0>1 else .1);xx=x0+(x1-x0)*.04;yy=y0+(y1-y0)*.04;a.plot([xx,xx+length],[yy,yy],color=INK,lw=2);a.text(xx,yy+(y1-y0)*.02,f'{length:g} km',fontsize=8,color=INK)
 a.annotate('N',xy=(x1-(x1-x0)*.05,y1-(y1-y0)*.03),xytext=(x1-(x1-x0)*.05,y1-(y1-y0)*.15),arrowprops=dict(arrowstyle='->',color=INK),ha='center',fontsize=9)
 f.subplots_adjust(0,0,1,1);path=D/(name+'.png');f.savefig(path,dpi=200,facecolor=BG);plt.close(f);return path
plots={}
plots['regions']=mapdraw('whole-site-regions',scope[0][0].bounds,'regions',figsize=(8,8))
for k,b,mode in [('urban',URBAN,'land'),('productive',PRODUCT,'land'),('phase',URBAN,'phase'),('productive-phase',PRODUCT,'phase'),('locator',SW,'locator')]:plots[k]=mapdraw(k,b,mode,figsize=(7,9) if k=='locator' else (7,7))
for g,p in nodes:
 nid=p['node_id'];bb=g.buffer(120).bounds
 if nid=='A03':bb=(573880,6556000,574280,6556380)
 if nid=='C03':bb=(572550,6556900,573550,6557500)
 plots[nid]=mapdraw(nid+'-detail-plan',bb,node=nid,figsize=(7,7))
W,H=420*mm,297*mm
style=ParagraphStyle('body',fontName='Body',fontSize=10,leading=14,textColor=HexColor(INK))
def txt(c,x,y,s,size=10,bold=False,color=INK):
 c.setFillColor(HexColor(color));c.setFont('Bold' if bold else 'Body',size);c.drawString(x*mm,y*mm,str(s))
def para(c,x,y,w,s,size=10,leading=None):
 st=ParagraphStyle('p',parent=style,fontSize=size,leading=leading or size*1.4)
 p=Paragraph(s,st);ww,hh=p.wrap(w*mm,1000*mm);p.drawOn(c,x*mm,y*mm-hh);return hh/mm
# Image fitting is presentation layout only; all original images remain unchanged.
def pic(c,path,x,y,w,h,fit='contain'):
 iw,ih=Image.open(path).size
 if fit=='contain':scale=min(w*mm/iw,h*mm/ih)
 else:scale=max(w*mm/iw,h*mm/ih)
 dw,dh=iw*scale,ih*scale;dx=x*mm+(w*mm-dw)/2;dy=y*mm+(h*mm-dh)/2
 src=str(path)
 if Path(path).parent.name in ['media','controls']:
  # PDF export encoding only: retain all original PNG assets unchanged.
  encoded=io.BytesIO();Image.open(path).convert('RGB').save(encoded,format='JPEG',quality=95,subsampling=0);encoded.seek(0);src=ImageReader(encoded)
 c.saveState();p=c.beginPath();p.rect(x*mm,y*mm,w*mm,h*mm);c.clipPath(p,stroke=0,fill=0);c.drawImage(src,dx,dy,dw,dh,mask='auto');c.restoreState()
def bg(c,w=W,h=H):c.setFillColor(HexColor(BG));c.rect(0,0,w,h,fill=1,stroke=0)
def header(c,title,sub=''):
 bg(c);txt(c,17,282,'AGUA FINITA / CITY DESIGN PRESENTATION',9,True,ACC);txt(c,17,265,title,23,True)
 if sub:para(c,17,255,385,sub,9)
def table(c,x,top,width,data,colweights=None,size=9):
 st=ParagraphStyle('cell',parent=style,fontSize=size,leading=size*1.3)
 dd=[[Paragraph(str(v),st) for v in row] for row in data];cw=[width*mm*v/sum(colweights) for v in colweights] if colweights else [width*mm/len(data[0])]*len(data[0]);t=Table(dd,colWidths=cw,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#E1D7C5')),('GRID',(0,0),(-1,-1),.35,HexColor('#C9C3B7')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));ww,hh=t.wrap(width*mm,1000*mm);t.drawOn(c,x*mm,top*mm-hh);return hh/mm
from concept_diagrams_v11 import build_diagrams
concept=build_diagrams()
made=[]
def newpage(name,fn):
 path=D/(name+'.pdf');c=canvas.Canvas(str(path),pagesize=(W,H));fn(c);c.save();made.append(path);return PdfReader(path).pages[0]
original=PdfReader(V/'agua-finita-v9-complete-city-review.pdf');pages=[];index=[]
def add(page,section):pages.append(page);index.append(dict(page=len(pages),section=section))
def sourcepage(i,section):add(original.pages[i],section)
hero=O/'media/A03-aerial.png'
def cover(c):
 bg(c);txt(c,17,266,'AGUA FINITA',31,True);txt(c,17,254,'CONTINUOUS LIVING DISTRICTS / INDEPENDENT PRODUCTION',11,True,ACC)
 pic(c,hero,17,37,386,209,'cover');txt(c,20,43,'CENTRE DISTRICT / LOCAL AERIAL',8,True)
 para(c,17,29,320,'Shade and daily life shape the public centre. The full-site regional framework and the independent productive system are explained in the following plans. AI-finished concept image.',9)
 txt(c,338,19,'JINGYUAN HUANG',9,True);txt(c,338,13,'27 OCT 2026 / V11',8)
add(newpage('cover',cover),'cover')
def whole_composite(c):
 header(c,'Whole-site zoning, road framework and landscape links','The complete issued boundary / six named regions / routes and landscape line widths are diagrammatic, not surveyed setbacks or installed works.')
 pic(c,concept['whole-composite'],17,32,270,211)
 for i,(g,p) in enumerate(regions):
  y=234-i*29;txt(c,303,y,p['id']+' / '+p['name'].split(' region')[0],10,True);txt(c,303,y-8,f"{p['area_km2']:,.1f} km2 gross / proposed role",8,color=MUT)
 para(c,303,52,100,'Blue dashed: regional road studies. Ochre dashed: arrival/freight approaches. Green: seasonal wash landscape. Hollow nodes: conditional transfer/service anchors. Fixed pilots retain their outlines.',8)
 add_legend(c,17,24)
def add_legend(c,x,y):
 for i,(key,name) in enumerate([('residential','Housing'),('mixed_use','Mixed centre'),('school','School'),('dry_park','Dry parks'),('compute','Production'),('energy','Solar')]):
  xx=x+i*58;c.setFillColor(HexColor(COL[key]));c.rect(xx*mm,y*mm,5*mm,3*mm,fill=1,stroke=0);txt(c,xx+7,y,name,8)
def spatial_sheet(c,kind='city-composite'):
 title={'city-composite':'City spatial structure / districts, centres and connections','network-composite':'Street hierarchy, passenger spine and local access','green-composite':'Dry landscape, public parks and proposed shade links'}[kind]
 header(c,title,'Coordinated diagram from current geometry / local urban enlargement with separate productive inset / not the whole competition boundary.')
 pic(c,concept[kind],17,38,271,205);pic(c,plots['productive'],304,100,98,126)
 txt(c,304,231,'P + S / SEPARATE INSET',10,True)
 if kind=='city-composite':body='Warm blocks form continuous living precincts. C is the town-level mixed-use centre; blue S anchors are schools and rust D anchors are daily services. Bold blue streets and the rust passenger spine link them. The productive estate remains separate.'
 elif kind=='network-composite':body='Blue: primary/secondary urban distributors. White: local street mesh. Rust dashed: proposed passenger spine with stops. Freight approaches P through separate study corridors. Rights, junction engineering and yard-spur crossing detail remain to verify.'
 else:body='Green parcels are dry parks; the western seasonal wash forms the landscape study. Bold green links are walking and engineered-shade opportunities along existing streets. Targeted low-water planting remains conditional on a verified reuse allocation; no continuous planted forest, lawn or permanent water is assumed.'
 para(c,304,88,98,body,9)
 add_legend(c,17,24)
add(newpage('whole-site-spatial-composite',whole_composite),'whole_site_regions_and_road_framework')
sourcepage(1,'whole_site_framework')
add(newpage('urban-spatial-composite',lambda c:spatial_sheet(c,'city-composite')),'complete_urban_plan')
def overall(c):
 header(c,'The city and its independent productive system','Southwestern settlement system / hypothetical full build-out / physical camera extent is not the competition boundary.')
 pic(c,O/'media/city-overall.png',17,51,278,188)
 pic(c,plots['locator'],304,68,98,166)
 para(c,17,43,278,'The continuous R/C town lies to the northeast; P is a separate compute/repair estate, with three S photovoltaic parcels between. Undeveloped separation is retained. This aerial does not depict the full 1,658.82 km2 territory or the distant N/E workplaces.',9)
 para(c,304,54,98,'True-distance locator: A03 town commons; B03 productive estate; C03 seasonal wash. The arrows register each aerial camera direction.',8)
add(newpage('system-aerial',overall),'overall_spatial_view')
for i,sect in [(4,'planning_structure'),(5,'functional_programme'),(6,'streets_mobility'),(7,'ecology_landscape'),(8,'land_use'),(9,'public_space_services'),(10,'overall_axonometric')]:
 if sect=='streets_mobility':add(newpage('street-network-diagram',lambda c:spatial_sheet(c,'network-composite')),sect)
 elif sect=='ecology_landscape':add(newpage('landscape-and-shade-diagram',lambda c:spatial_sheet(c,'green-composite')),sect)
 else:sourcepage(i-1,sect)
def locator(c):
 header(c,'Three places, one shared locator','A03 living/public space / B03 production/infrastructure / C03 urban interface/environment. IDs match plans, images and source geometry.')
 pic(c,plots['locator'],17,27,158,215)
 texts=[('A03 / MARKET COMMONS','Public space in heat and Zonda wind','C town centre / Phase 1','An 80 x 80 m civic commons, two market/refuge halls and two 70 x 6 m shade bands. Daily services are reached through the town street network. The view is a node crop, not a whole-city render.'),('B03 / PRODUCTIVE PRECINCT','A compute campus and its waste heat','P independent estate / Phase 1-3','Eight separate staged compute halls and four repair workshops use their own machine/service spine. A 280 m worker shade route parallels the service spine; controlled yard-spur crossings require detailed design. No residential heat pipe is credited.'),('C03 / SEASONAL WASH EDGE','A seasonal river park','Western channel edge / Phase 2','A removable 40 x 6 m shade point and an edge path link back to the residential street. The illustrated visitor edge is a local crop of the larger park study. The dry wash is not an ornamental waterbody.')]
 for k,(name,topic,loc,body) in enumerate(texts):
  y=233-k*69;txt(c,191,y,name,13,True);txt(c,191,y-9,topic,10,False,ACC);txt(c,191,y-18,loc,9,True);para(c,191,y-27,209,body,9)
add(newpage('shared-node-locator',locator),'shared_node_locator')
nodeinfo={
'A03':('Market commons and climate refuge','Public space in heat and Zonda wind','C centre / Phase 1','Morning market setup; daytime visits and refuge; evening social use. Staff open the indoor refuge and manage events. Shade is provided by roofs, not an assumed irrigated canopy.'),
'B03':('Compute and repair precinct','A compute campus and its waste heat','P productive estate / phased 2-4-8 MW scenario','The worker path runs parallel to the service spine; controlled yard-spur crossings still require detailed design. Freight remains on the machine network. Curtailable IT follows the energy account; dry cooling and metering precede expansion. No unverified residential heat benefit is claimed.'),
'C03':('Seasonal wash visitor edge','A seasonal river park','Western seasonal channel / Phase 2','Dry-season walking and observation use the eastern edge. The path and shade point are removable. Access closes on warnings; no occupied building or dam is placed on the source channel. Surveys and hydraulic design must set safe levels.')}
def section(c,nid,x,y,w):
 c.setStrokeColor(HexColor(INK));c.setLineWidth(.8);c.line(x*mm,y*mm,(x+w)*mm,y*mm)
 if nid=='A03':
  for xx in [x+10,x+w-65]:c.rect(xx*mm,y*mm,55*mm,8*mm,stroke=1,fill=0)
  for xx in [x+70,x+w-90]:c.line(xx*mm,(y+7)*mm,(xx+20)*mm,(y+7)*mm)
  txt(c,x,y-8,'Diagrammatic section / low market halls and open shade / not a surveyed level',8)
 elif nid=='B03':
  for xx in [x+w*.06,x+w*.38,x+w*.70]:c.rect(xx*mm,y*mm,w*.24*mm,5*mm,stroke=1,fill=0)
  txt(c,x,y-8,'Diagrammatic hall sequence / footprints and single-storey heights retained',8)
 else:
  pp=c.beginPath();pp.moveTo(x*mm,(y+4)*mm)
  for xx,yy in [(x+30,y+4),(x+65,y),(x+100,y),(x+130,y+4),(x+w,y+4)]:pp.lineTo(xx*mm,yy*mm)
  c.drawPath(pp);txt(c,x,y-8,'Illustrative dry-wash section / no asserted flood levels or permanent water',8)
for nid,(name,topic,loc,use) in nodeinfo.items():
 def aerial(c,nid=nid,name=name,topic=topic,loc=loc):
  header(c,nid+' / '+name,topic+' / '+loc+' / local aerial')
  pic(c,O/'media'/f'{nid}-aerial.png',17,20,386,227)
  txt(c,17,14,'AI-finished concept image from the registered geometry-derived aerial control. Materials and life illustrate design; they are not evidence.',7)
 add(newpage(nid+'-finished-aerial',aerial),'node_'+nid+'_aerial')
 def eye(c,nid=nid,name=name,topic=topic,loc=loc,use=use):
  header(c,nid+' / use, access and spatial detail',topic+' / '+loc+' / eye-level camera E and aerial camera A are marked on the plan.')
  pic(c,O/'media'/f'{nid}-eye.png',17,81,251,157)
  pic(c,plots[nid],281,81,122,157)
  txt(c,17,74,'FINISHED EYE-LEVEL CONCEPT VIEW',8,True);txt(c,281,74,'PLAN / CAMERA DIRECTIONS',8,True)
  para(c,17,64,251,use,9)
  section(c,nid,281,46,122)
  para(c,281,27,122,'Plan is authoritative for position and dimensions. Section is explanatory. People, surface textures and detailed finishes are illustrative.',8)
 add(newpage(nid+'-finished-eye-and-plan',eye),'node_'+nid+'_eye_plan')
sourcepage(13,'phasing_map_and_totals')
works={'R':'Housing + daily care, schools, dry parks and local streets','C':'Arrival, market/refuge, primary care and mixed-use centre','P':'Staged compute halls, repair, covered water/reuse works','S':'Explicit phased PV parcels; essential loads protected','A':'13.4 ha metered irrigation trial, subject to source headroom','N':'Northern maintenance, cooperative and day services','E':'Gateway workshops, trade services and 320 roster beds'}
def programme_page(c):
 header(c,'Every developed zone has a phased account','New / cumulative design capacities; scenario timing and observable triggers govern actual release. Roster beds are not resident households.')
 data=[['Zone / phase','Residents<br/>new / total','Homes<br/>new / total','Jobs<br/>new / total','Works / provision']]
 for ph in programme:
  for z in ph['zones']:data.append([z['zone_id']+' / P'+str(ph['phase']),f"{z['new_residents']:,.0f} / {z['cumulative_residents']:,.0f}",f"{z['new_dwellings']:,} / {z['cumulative_dwellings']:,}",f"{z['new_jobs']:,} / {z['cumulative_jobs']:,}",works[z['zone_id']]])
 h=table(c,17,239,386,data,[.7,1,1,1,2.5],8)
 assert h<210,('programme table',h)
 para(c,17,25,386,'Sequence: access rights and utility supply precede occupancy. School/health/market operators and livelihood demand precede housing release. Gateway rights and worker welfare precede E. Full numeric programme and assumptions remain in the technical records.',8)
add(newpage('zone-phase-programme',programme_page),'zone_phase_programme')
sourcepage(14,'resources_and_independent_operation')
def indicators(c):
 header(c,'Capacities, resource gates and the declared trade-off','All values below are computed geometry or declared scenarios. No water right, installed power, signed employment or approval is implied.')
 data=[['Indicator / basis','Phase 1','Phase 2','Phase 3']]
 for label,key in [('Residents / 2.5 per dwelling','total_residents'),('Dwellings / geometry','total_dwellings'),('Job-space capacity / scenario','total_jobs')]:data.append([label]+[f'{v[key]:,.0f}' for v in programme])
 for label,key in [('Education places / scenario','school_places'),('Fresh requirement / new programme m3/year','fresh_requirement_m3_y'),('Peak IT capacity / MW','it_peak_mw'),('PV scenario / MWp','pv_mwp')]:data.append([label]+[f'{v[key]:,.0f}' for v in resource])
 table(c,17,236,386,data,[2.7,1,1,1],10)
 para(c,17,109,180,'<b>What the scheme gives up</b><br/>Maximum uninterrupted computing throughput and the shortest possible productive route. Housing continuity, independent public life and an honest service boundary take priority. The consequence is a separate worker shuttle and controlled curtailment; operators bear the interruption cost.',10)
 para(c,222,109,181,'<b>What must be verified before construction</b><br/>Combined existing/new water balance; terrain and channel surveys; access and power rights; funded schools, health and utilities; household livelihood/demand; noise, dust, seismic and civil design. Current images cannot establish any of these.',10)
add(newpage('key-indicators',indicators),'key_indicators')
# Consistent headers and page numbers over retained vector planning drawings.
writer=PdfWriter()
for i,p in enumerate(pages):
 buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(W,H));c.setFillColor(HexColor(BG));c.rect(0,H-17*mm,W,17*mm,fill=1,stroke=0);c.rect(0,0,W,11*mm,fill=1,stroke=0)
 txt(c,17,282,'AGUA FINITA / V11 DESIGN PRESENTATION',9,True,ACC)
 txt(c,17,5,'Jingyuan Huang / 27 October 2026 / Planning geometry + declared scenarios / Concept design for review',7,color=MUT);txt(c,385,5,f'{i+1:02} / {len(pages):02}',7,color=MUT);c.save();p.merge_page(PdfReader(buf).pages[0]);writer.add_page(p)
main=D/'agua-finita-v11-booklet.pdf'
with open(main,'wb') as f:writer.write(f)
# A0 spatial presentation: no spreadsheet/grid accounts on the board.
aw,ah=1189*mm,841*mm;c=canvas.Canvas(str(D/'agua-finita-v11-a0.pdf'),pagesize=(aw,ah));bg(c,aw,ah)
txt(c,25,807,'AGUA FINITA',49,True);txt(c,25,786,'CONTINUOUS LIVING DISTRICTS / INDEPENDENT PRODUCTION / CONNECTED PUBLIC LANDSCAPE',20,True,ACC);txt(c,1008,807,'JINGYUAN HUANG',15,True);txt(c,1008,790,'27 OCT 2026 / V11',14)
pic(c,hero,25,485,658,283,'cover');txt(c,30,491,'CENTRE DISTRICT / LOCAL AERIAL / AI-FINISHED CONCEPT',13,True)
pic(c,concept['whole-composite'],707,495,280,270);txt(c,707,772,'WHOLE-SITE ZONING + ROAD FRAMEWORK',17,True)
for i,(g,p) in enumerate(regions):
 txt(c,1000,745-i*37,p['id']+' / '+p['name'].split(' region')[0],13,True)
 txt(c,1000,732-i*37,f"{p['area_km2']:,.1f} km2 gross / proposed role",11,color=MUT)
for x,key,title in [(25,'city-composite','URBAN SPATIAL STRUCTURE'),(325,'network-composite','STREETS + PUBLIC CENTRES'),(620,'green-composite','LANDSCAPE + SHADE LINKS')]:
 txt(c,x,465,title,16,True);pic(c,concept[key],x,263,285,190)
txt(c,925,465,'THREE CONDITIONAL STAGES',16,True);pic(c,plots['phase'],925,350,235,105)
for i,(ph,col) in enumerate(PC.items()):
 yy=332-i*31;c.setStrokeColor(HexColor(col));c.setLineWidth(4);c.line(925*mm,(yy+3)*mm,937*mm,(yy+3)*mm)
 q=programme[i];txt(c,943,yy,f"P{ph} / {q['total_residents']:,.0f} residents / {q['total_dwellings']:,} homes",13,True)
 brief={1:'Years 0-5: access, supply and essential services before occupancy.',2:'Years 5-10: connected expansion; demand and resource headroom verified.',3:'Years 10-20: complete northern precinct; gateway rights and services first.'}[ph]
 para(c,925,yy-8,235,brief,10)
for i,(key,name) in enumerate([('residential','Living precincts'),('mixed_use','Mixed/public centre'),('school','Schools + care'),('dry_park','Dry parks')]):
 xx=25+i*215;c.setFillColor(HexColor(COL[key]));c.rect(xx*mm,248*mm,9*mm,4*mm,fill=1,stroke=0);txt(c,xx+12,248,name,10)
for i,(col,name) in enumerate([('#315C81','Primary/secondary streets'),('#BD6549','Proposed passenger spine'),('#78A14A','Proposed walk/shade links'),('#86A795','Seasonal wash landscape')]):
 xx=25+i*215;c.setStrokeColor(HexColor(col));c.setLineWidth(2.5);c.line(xx*mm,237*mm,(xx+9)*mm,237*mm);txt(c,xx+12,235,name,10)
for i,(nid,(name,topic,loc,use)) in enumerate(nodeinfo.items()):
 x=25+i*382;txt(c,x,219,nid+' / '+name,18,True);txt(c,x,207,topic+' / '+loc,11)
 pic(c,O/'media'/f'{nid}-aerial.png',x,79,179,119);pic(c,O/'media'/f'{nid}-eye.png',x+184,79,179,119)
 txt(c,x,73,'LOCAL AERIAL',10,True);txt(c,x+184,73,'EYE-LEVEL USE',10,True);para(c,x,61,363,use,10)
para(c,25,22,1139,'Whole-site boundary, named regions and road studies remain explicit. Green marks dry landscape, public parks and proposed walking/shade roles; planting remains conditional on the water budget. The hero is a LOCAL aerial. Detailed capacity, resource and zone-phase accounts are retained in the booklet and technical records, not a spreadsheet on this board.',10)
c.save()
# Separate technical attachment: raw controls, comparisons and exact cameras never dominate the public booklet.
a=canvas.Canvas(str(D/'agua-finita-v11-technical-appendix.pdf'),pagesize=(W,H))
header(a,'Technical appendix / image controls and provenance','Original geometry, registered cameras, visual review and current limitations / supporting material, separate from the public design story.')
para(a,17,228,185,'<b>Sources and geometry</b><br/>V9 complete-city geometry and ac96714 requirements snapshot. V10 adds four explicit open shade structures and two pedestrian links; no homes, jobs, school places or compute capacity are added. Zero-area clipping debris is removed from scene inputs. The local scene master polygon defines rendering extent only; it does not replace the design area or whole-site boundary.',11)
para(a,222,228,181,'<b>Scene conventions</b><br/>Source Copernicus terrain is retained. Concept building platforms use maximum sampled corner height to avoid terrain clipping; foundations and grading require civil design. Procedural planting/PV/entourage are disabled. PV rows follow the explicit V9 assets. AI materials and people are illustrative. No long residential heat pipe is credited.',11)
para(a,17,117,185,'<b>Image generation</b><br/>Built-in image_gen.imagegen; exact model version is not exposed. Full prompts and image/control hashes are saved in image_provenance.json and generation-record.json. Rejected trials were excluded: an eight-building simplification of P, oversized aerial people and an additional local-city trial that closed separate bar footprints into courtyards.',10)
para(a,222,117,181,'<b>Review scope</b><br/>The selected images were visually compared for view direction, principal massing, road relationships and prohibited additions. This is a human-readable visual QA record, not a pixel-perfect geometric certification. Plans and underlying geometry govern dimensions and capacity. Rights, hydraulic levels and climate operation remain unverified.',10)
a.showPage()
for rec in cams:
 vid=rec['id']
 if not (O/'media'/f'{vid}.png').exists():continue
 header(a,vid+' / control and finished illustration',rec['scope']+' / '+rec['phase'])
 pic(a,O/'controls'/f'{vid}.png',17,105,189,125);pic(a,O/'media'/f'{vid}.png',214,105,189,125)
 txt(a,17,97,'GEOMETRY-DERIVED CONTROL',9,True);txt(a,214,97,'SELECTED FINISHED CONCEPT IMAGE',9,True)
 txt(a,17,79,'Position / UTM19S: '+str(rec['position_utm19s']),9);txt(a,17,69,'Target / UTM19S: '+str(rec['target_utm19s']),9)
 txt(a,17,59,'Perspective camera / vertical FOV '+str(rec['fov_degrees'])+' degrees / 1920 x 1200 control',9)
 para(a,17,43,386,'The output preserves the intended spatial organisation. Finishes, surface textures, minor equipment and human activity are illustrative. No people, texture or planted ground establishes capacity or surveyed conditions. See the registry and source/control/image fingerprints for traceability.',9)
 a.showPage()
header(a,'Evidence and remaining verification','Internal geometry checks and declared scenarios are not organiser design approval.')
para(a,17,228,185,'<b>Geometry and accounts</b><br/>V9 has '+str(qas['buildings'])+' source building footprints, '+str(qas['residential_blocks'])+' residential blocks and '+str(qas['dwelling_count'])+' dwelling capacity. Building overlap: '+str(qas['building_overlap_m2'])+' m2. Buffered street reserve conflicts: '+str(len(qas['road_building_conflicts']))+'. All district land accounts close. Four V10 open canopies have no household or employment capacity. V9 geometric checks do not certify the V10 yard-spur crossing details; these remain an explicit design hold-point.',11)
para(a,222,228,181,'<b>Capacity assumptions</b><br/>2.5 residents/dwelling; 120 m2 gross housing floor area/dwelling; education need 15% of residents; 360 places per school wing. Job totals are programme capacity, not contracted jobs. Roster beds are counted separately. Phase-one combined existing/new water rights and fixed-pilot demand remain unresolved.',11)
para(a,17,118,386,'<b>Reproduction and disclosure</b><br/>Planning: tools/complete_city_v9.py. Scene and controls: tools/presentation_v10.py; controls rendered with the project renderer plus the disclosed local platform/PV orientation adjustment in renderer-v10.js. Presentation: tools/publish_v10.py. Human directed whole-site scope, regional legibility, housing continuity, finished rendering and close framing; Codex developed the design/geometry and composed the presentation. No public website update or new automatic 12/12 approval is claimed by this presentation review.',10)
a.save()
(D/'presentation-index.json').write_text(json.dumps(dict(status='design_presentation_review_not_final_submission',main_pages=len(pages),sections=index,technical_separate=True),indent=2)+'\n')
for name in ['agua-finita-v11-booklet.pdf','agua-finita-v11-a0.pdf','agua-finita-v11-technical-appendix.pdf','presentation-index.json']:shutil.copy2(D/name,OUT/name)
for path in made:path.unlink(missing_ok=True)
print('DELIVERED',len(pages),'main pages',OUT)
