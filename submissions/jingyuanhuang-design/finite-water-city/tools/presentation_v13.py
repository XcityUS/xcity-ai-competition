# -*- coding: utf-8 -*-
"""Compose source-coordinate plans, public renders and native A0 boards; no new geometry."""
import json,runpy,re,shutil,subprocess,sys
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch,Rectangle
from matplotlib.lines import Line2D
from shapely.geometry import box,Point
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/presentation-v13';O.mkdir(exist_ok=True)
v=runpy.run_path(str(P/'tools/concept_diagrams_v11.py'))
load,fill,line,label,frame=[v[x] for x in ['load','fill','line','label','frame']]
scope,channels,regions,districts,regional,fixed=[v[x] for x in ['scope','channels','regions','districts','regional','fixed']]
land=load(P/'geometry/land_use.geojson');roads=load(P/'geometry/movement.geojson');build=load(P/'geometry/buildings.geojson');phases=load(P/'geometry/phasing.geojson');fields=load(P/'geometry/territorial_fields.geojson')
BG='#FCFBF6';INK='#213C47';BLUE='#397A9B';GOLD='#B49D4F'
rc={'Z1':'#DDA688','Z2':'#B9CD9C','Z3':'#E2CD7A','Z4':'#A9B56C','Z5':'#AD9ABB','Z6':'#D2D4C7'}
roles={'Z1':'Southwest city + services','Z2':'Agricultural research','Z3':'Solar-agriculture opportunity','Z4':'Production + transfer','Z5':'Gateway + logistics','Z6':'Mountain stewardship'}
C=v['C'];bounds=(571800,6551800,576600,6559500)
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'font.size':10,'pdf.fonttype':42})
def whole(a,theme='functions',labels=True):
 fill(a,scope,'#E9E7DB')
 for g,p in regions:
  col=rc[p['id']] if theme in ['functions','structure'] else '#EBE9DE'
  if theme=='ecology':col='#CBCFC1' if p['id']=='Z6' else '#E7E4D5'
  fill(a,g,col,'white',.5)
 if theme in ['functions','landuse','ecology']:
  for g,p in fields:fill(a,g,'#A7B15E',alpha=.75)
 line(a,channels.intersection(scope),'#78A5B2',.55 if theme!='ecology' else 1.1)
 if theme in ['functions','structure','mobility','services']:
  for g,p in regional:
   phase=str(p.get('phase',p.get('phase_id','')))
   line(a,g.intersection(scope),BG,2.8)
   line(a,g.intersection(scope),BLUE,1.35,'--')
 for g,p in fixed:fill(a,g,GOLD,INK,.5)
 for g,p in districts:
  use=p.get('use',p.get('primary_use',''));id=p.get('id','')
  fill(a,g,C.get(use,'#B47C60'),INK,.45)
  if theme in ['structure','mobility','services']:line(a,g,INK,1.3)
 line(a,scope,INK,1.1)
 if labels:
  for g,p in regions:
   if theme in ['functions','structure']:label(a,g,p['id']+'\n'+roles[p['id']],8)
  if theme in ['services','mobility']:
   for g,p in districts:
    label(a,g,p.get('id',''),7)
 frame(a,scope.bounds)
 # Actual enlargement footprint, not an invented node/city boundary.
 line(a,box(*bounds),'#C56243',1.5)
def local(a,theme='functions'):
 w=box(*bounds);fill(a,scope.intersection(w),'#EAE7DB')
 for g,p in land:
  use=p.get('programme_use',p.get('use',''));col=C.get(use,C.get(p.get('use'), '#E6E2D5'))
  if theme=='mobility' and use not in ['school','daily_centre','public_commons','arrival']:col='#DFDCCE'
  if theme=='services' and use not in ['school','daily_centre','public_commons','arrival','civic','culture']:col='#EAE6DA'
  fill(a,g.intersection(w),col,'white',.2)
 for g,p in fixed:fill(a,g.intersection(w),GOLD,INK,.6)
 line(a,channels.intersection(w),'#7AA6AF',.9)
 for g,p in roads:
  q=g.intersection(w)
  if q.is_empty:continue
  net=p.get('network');hier=p.get('road_class',p.get('hierarchy','local'))
  major=hier in ['primary','secondary','arterial','collector']
  line(a,q,BG,2.6 if major else .8)
  line(a,q,BLUE if net!='machine' else '#8B6854',1.25 if major else .45,'--' if net=='people' else '-')
 for g,p in build:fill(a,g.intersection(w),'#5F6D6C',alpha=.8)
 if theme=='phases':
  for g,p in phases:
   k=str(p.get('phase',1));fill(a,g.intersection(w),{'1':'#E3A26E','2':'#85B4B2','3':'#BAA1BD'}.get(k,'#ACA890'),INK,.35,.5)
 labels=[(574800,6558570,'Living precincts'),(574950,6556200,'Town centre / A03'),(573930,6554010,'Solar + crop trials'),(573650,6552540,'Repair + shared plant'),(573480,6552140,'Modular compute / B03')]
 for x,y,t in labels:label(a,Point(x,y),t,8)
 frame(a,bounds)
def title(f,k,t,sub=''):
 f.text(.04,.965,k.upper(),fontsize=11,color=GOLD,weight='bold');f.text(.04,.923,t,fontsize=24,weight='bold')
 if sub:f.text(.04,.89,sub,fontsize=10)
def foot(f,n):
 f.text(.04,.025,'AGUA FINITA / V13 presentation revision / 27 October 2026 / Public working preview',fontsize=8)
 f.text(.96,.025,str(n),fontsize=8,ha='right')
def legend(f,x,y,items,size=9):
 for i,(c,t) in enumerate(items):
  f.patches.append(Rectangle((x,y-i*.025),.009,.009,transform=f.transFigure,color=c));f.text(x+.015,y-i*.025,t,fontsize=size)
def photo(a,path):
 a.imshow(plt.imread(P/path));a.axis('off')
def savefig(f,name):
 f.savefig(O/(name+'.png'),dpi=180,facecolor=BG);f.savefig(O/(name+'.pdf'),facecolor=BG);plt.close(f)
# Standalone useful drawings, available in the proposal body.
f=plt.figure(figsize=(16,11),facecolor=BG);title(f,'01 / territory','An energy landscape with connected centres','Full issued boundary. Strategic zones are proposed allocations, not installed works.')
a=f.add_axes([.035,.12,.62,.74]);whole(a)
legend(f,.69,.80,[(rc[k],k+'  '+roles[k]) for k in rc])
f.text(.69,.58,'Source channels remain visible.\nFields stop at screened constraints.\nFixed pilot interiors are retained.\n\nDashed blue: proposed regional corridors.\nRed frame: southwest enlargement below.\n\nZ1 living and public services support\nproduction; they do not replace the\nsolar-agriculture territorial programme.',fontsize=11,linespacing=1.7)
foot(f,1);savefig(f,'full-site-functions')
f=plt.figure(figsize=(16,11),facecolor=BG);title(f,'02 / southwest enlargement','Living, public life and production use different ground','Canonical V12 geometry / street hierarchy, actual footprints and protected pilot context')
a=f.add_axes([.04,.10,.65,.75]);local(a)
legend(f,.72,.79,[('#F0D18F','Living precincts'),('#D8785E','Public commons'),('#7CA7C8','Education / daily services'),('#D9C36D','Solar + crop trial areas'),('#7A9EA8','Compute halls'),('#B1A28B','Repair / productive uses'),(BLUE,'Passenger / shared movement'),('#8B6854','Machine servicing'),('#7AA6AF','Source seasonal channels')])
f.text(.72,.48,'The productive estate remains separate.\nShared plant serves compact modular halls.\nThe shuttle follows the solar edge.\n\nThis is a local enlargement;\nthe red footprint on the full-site plan\nlocates it within the entire territory.',fontsize=10,linespacing=1.6);foot(f,2);savefig(f,'southwest-functions-roads')
f=plt.figure(figsize=(16,11),facecolor=BG);title(f,'03 / coordinated systems','One territory, six planning questions','Each overlay uses the same issued boundary and source channels. Detailed street and service design is enlarged separately.')
for i,(th,t) in enumerate([('structure','Structure / connected centres'),('functions','Functions / strategic districts'),('mobility','Mobility / corridor reservations'),('ecology','Ecology / drainage + retained terrain'),('landuse','Land use / conditional field footprints'),('services','Services / settlement and work anchors')]):
 ax=f.add_axes([.035+(i%3)*.32,.48-(i//3)*.40,.29,.36]);whole(ax,th,False);ax.set_title(t,fontsize=10,loc='left',pad=3)
f.text(.04,.055,'Blue dashed links are studies, not acquired roads. Green fields are conditional opportunities, not installed PV. Retained mountain ground is not vacant development land.',fontsize=8);foot(f,3);savefig(f,'six-system-overlays')
# Native A0 composition: axes draw polygons/roads directly; only concept images are raster.
with PdfPages(P/'drawings/a0-board.pdf') as pdf:
 f=plt.figure(figsize=(46.81,33.11),facecolor=BG);title(f,'A0 / 01','AGUA FINITA | Solar agriculture, productive work and a compact city','A coordinated territorial proposal / source boundary and seasonal channels retained / V13 public working preview')
 a=f.add_axes([.025,.13,.40,.72]);whole(a)
 a=f.add_axes([.44,.32,.25,.53]);local(a)
 f.text(.44,.865,'SOUTHWEST / FUNCTIONS AND STREET NETWORK',fontsize=16,weight='bold')
 a=f.add_axes([.71,.48,.265,.35]);photo(a,'media/v11-A03-aerial.png');f.text(.71,.47,'A03 / local public-centre aerial / AI-finished concept image',fontsize=11)
 a=f.add_axes([.71,.13,.265,.31]);photo(a,'media/v11-A03-eye.png');f.text(.71,.12,'A03 / market commons at eye level / AI-finished concept image',fontsize=11)
 legend(f,.44,.26,[(rc[k],k+'  '+roles[k]) for k in rc],12)
 f.text(.04,.08,'TERRITORY -> SOUTHWEST ENLARGEMENT -> PUBLIC LIFE',fontsize=18,weight='bold')
 f.text(.04,.055,'Photovoltaic fields and under-panel forage / jojoba lead the territorial programme. Compact industrial halls use modular construction and shared infrastructure.\nFuture field opportunities depend on water, grid, demand and detailed engineering; the plan does not claim those resources are secured.',fontsize=12,linespacing=1.5)
 foot(f,1)
 for text in f.findobj(matplotlib.text.Text):text.set_fontsize(text.get_fontsize()*2.15)
 pdf.savefig(f);f.savefig(O/'a0-board-01.png',dpi=55,facecolor=BG);plt.close(f)
 f=plt.figure(figsize=(46.81,33.11),facecolor=BG);title(f,'A0 / 02','The same city, read through its systems','Planning structure, functions, roads, ecology, land use and public-service anchors')
 for i,(th,t) in enumerate([('structure','01 Structure'),('functions','02 Functional regions'),('mobility','03 Regional movement'),('ecology','04 Drainage and retained landscape'),('landuse','05 Conditional production land'),('services','06 Service anchors')]):
  ax=f.add_axes([.035+(i%3)*.32,.49-(i//3)*.40,.29,.36]);whole(ax,th,False);ax.set_title(t,fontsize=18,loc='left')
 f.text(.04,.055,'Strategic diagrams are territorial. Detailed public-service provision and local roads are shown in the southwest enlargement; reservations elsewhere are not operating settlements.',fontsize=13);foot(f,2)
 for text in f.findobj(matplotlib.text.Text):text.set_fontsize(text.get_fontsize()*2.15)
 pdf.savefig(f);f.savefig(O/'a0-board-02.png',dpi=55,facecolor=BG);plt.close(f)
# Booklet with drawings and finished views interleaved in the argument.
with PdfPages(P/'drawings/a3-booklet.pdf') as pdf:
 n=0
 for name in ['full-site-functions','southwest-functions-roads','six-system-overlays']:
  from pypdf import PdfReader
  # Reuse vector standalone pages later through pypdf, below.
 for key,heading in [('v11-A03-aerial','A03 / a public centre within the street network'),('v11-A03-eye','A03 / shade, market frontage and everyday public life'),('v11-C03-aerial','C03 / local seasonal-wash visitor edge'),('v11-C03-eye','C03 / a limited visitor-edge study')]:
  n+=1;f=plt.figure(figsize=(16,11),facecolor=BG);title(f,'Architectural concept / '+key.split('-')[1],heading,'AI-finished view from registered source control. Images illustrate design; they are not survey or engineering evidence.')
  a=f.add_axes([.04,.13,.92,.72]);photo(a,'media/'+key+'.png')
  f.text(.04,.075,'C03 remains a limited local study; these views do not establish the full seasonal river park, hydraulic safety or crossings.' if 'C03' in key else 'The public-space view is local; the whole-site energy programme is shown on the territorial plans.',fontsize=10);foot(f,n);pdf.savefig(f);plt.close(f)
# Assemble overview plans + source operating drawings + renders. Original sheets kept legible at full page.
from pypdf import PdfReader,PdfWriter
renderpages=PdfReader(P/'drawings/a3-booklet.pdf');writer=PdfWriter()
for name in ['full-site-functions','southwest-functions-roads','six-system-overlays']:
 writer.append(O/(name+'.pdf'))
for p in list(renderpages.pages)[:2]:writer.add_page(p)
# V12 operating sheets, imported from their already-authored booklet (page order documented in V12 tool).
old=PdfReader(P/'reviews/production-v12/agua-finita-v12-booklet.pdf')
for i in [0,1,6,7,8,9]:writer.add_page(old.pages[i])
for p in list(renderpages.pages)[2:]:writer.add_page(p)
writer.add_metadata({'/Title':'Agua Finita | V13 spatial plans and architectural concepts'})
with (P/'drawings/a3-booklet.pdf').open('wb') as f:writer.write(f)
# Rebuild the 14-section reading order; no duplicated preliminary section list.
src=subprocess.check_output(['git','show','994bbf5:submissions/jingyuanhuang-design/finite-water-city/proposal.md'],text=True);parts=re.split(r'^## (\d+\. [^\n]+)\n',src,flags=re.M);texts={}
for i in range(1,len(parts),2):texts[int(parts[i].split('.')[0])]=(parts[i],parts[i+1].split('### Retained city diagrams')[0].strip())
images={1:[('Whole-site energy axon','reviews/production-v12/overall-energy-axon.png')],2:[('Whole-site functional regions','reviews/presentation-v13/full-site-functions.png'),('Conditional field layout','reviews/production-v12/territorial-fields-plan.png')],3:[('Six coordinated system overlays','reviews/presentation-v13/six-system-overlays.png')],4:[('Southwest functions and road hierarchy','reviews/presentation-v13/southwest-functions-roads.png')],5:[('City mobility study','reviews/presentation-v11/drawings/diagram-movement.png')],6:[('City landscape study','reviews/presentation-v11/drawings/diagram-green.png')],7:[('Public-centre plan','reviews/presentation-v11/drawings/A03-detail-plan.png')],8:[('A03 aerial - AI-finished concept image','media/v11-A03-aerial.png'),('A03 eye level - AI-finished concept image','media/v11-A03-eye.png')],9:[('Current compact modular compute layout','reviews/production-v12/compute-plan.png')],10:[('C03 edge plan - limited study','reviews/presentation-v11/drawings/C03-detail-plan.png'),('C03 aerial - AI-finished local edge concept','media/v11-C03-aerial.png'),('C03 eye level - AI-finished local edge concept','media/v11-C03-eye.png')],11:[('Compute construction phases','reviews/production-v12/compute-phases.png')],12:[('Panel crop and work plan','reviews/production-v12/agrivoltaic-plan.png'),('Panel crop work section','reviews/production-v12/agrivoltaic-section.png')]}
md='# AGUA FINITA | The Finite Water City\n\nV13 public working preview. Whole-site functions and roads, a southwest enlargement and architectural views are now read together. Source boundary and seasonal channels are retained. Future fields remain conditional proposals.\n\n'
for k in range(1,15):
 h,t=texts[k];md+='## '+h+'\n\n'+t+'\n\n'
 if k==9:md+='The previous B03 finished images are superseded by this compact arrangement and are deliberately excluded. A corrected architectural finish is still pending.\n\n'
 if k==12:md+='Confirmed under-panel crops are forage grass and jojoba. This extension prototype retains that programme; crop allocation, irrigation, panel heights and working clearances remain declared assumptions requiring verification.\n\n'
 for alt,path in images.get(k,[]):md+='!['+alt+']('+path+')\n\n'+alt+'.\n\n'
(P/'proposal.md').write_text(md)
m=json.loads((P/'manifest.json').read_text());m['presentation_revision']='V13';m['summary']=m['summary'].replace('V12','V13');m['autonomy']['human_role']+=' V13 responds to the human request for renders inside the report/booklet/A0 and source-coordinate functional/road diagrams. It does not certify unresolved design or engineering.';(P/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
with (P/'changelog.md').open('a') as f:f.write('\n## 2026-10-27 / V13 presentation correction\n\nReplaced the pasted-sheet A0 with two native vector boards, full-site functional and six-system overlays, and the southwest functions/road enlargement. Inserted the four registered A03/C03 concept images into the actual statement and booklet, and A03 images into A0. Retained current V12 geometry. Superseded B03 finishes remain excluded; full park and engineering review remain open.\n')
subprocess.run([sys.executable,str(R/'scripts/render_proposal_html.py'),str(P)],check=True)
print('V13 authored: two A0 boards, 13-page booklet, 14-section illustrated report')
