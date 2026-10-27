"""Coordinated geometry-derived diagrams; no generative map geometry."""
import json,math
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch,Patch
from matplotlib.path import Path as MP
from shapely.geometry import shape,box,Point,LineString
from shapely.geometry.polygon import orient
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/redesign-v2';D=O/'diagrams';D.mkdir(exist_ok=True);T=Transformer.from_crs(4326,32719,always_xy=True).transform
load=lambda f:[(transform(T,shape(x['geometry'])),x['properties']) for x in json.loads(f.read_text())['features']]
land=load(P/'geometry/land_use.geojson');land=[(g,dict(p,use=p.get('programme_use',p['use']))) for g,p in land];bld=load(P/'geometry/buildings.geojson');roads=load(P/'geometry/movement.geojson');regions=load(P/'geometry/structure.geojson');nodes=load(P/'geometry/nodes.geojson');dist=load(O/'districts.geojson');scope=load(R/'brief/site-package/boundaries/scope_9_13.geojson');ch=load(R/'brief/site-package/water/channels_dem.geojson');fixed=load(R/'brief/site-package/pilot-area/pilot_area.geojson')+load(R/'brief/site-package/pilot-area/pilot_living_area.geojson');assets=load(P/'geometry/assets.geojson')
BG='#F7F4EC';INK='#263F46';BLUE='#356C86';RUST='#BC7652';GREEN='#9BB77A';GREY='#DEDCD3';COL={'residential':'#E8CA86','civic':'#C37A68','school':'#8CB2C0','daily_centre':'#C897B5','dry_park':'#A8BF87','terrain_review':'#D9D9CF','infrastructure':'#BDC5C7','open_space':'#DAD9C7','compute':'#889DB0','industry':'#B29A88','agriculture':'#B9C992','energy':'#C4AD74'}
RC={'D00-F':'#A69779','D00-L':'#B59B84','D01':'#DEB397','D02':'#B6C693','D03':'#DFCC89','D04':'#A4BDC1','D05':'#B7A4BF','D06':'#E3E0D2','D07':'#C5CBBE'}
PC={1:'#C18361',2:'#9FB48C',3:'#88A8BD'};TOWN=(573250,6554150,575950,6556850);SYSTEM=(572700,6550800,576150,6557000)
def poly(g):
 if g.is_empty:return
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from poly(q)
def fill(a,g,c,edge='none',lw=.25,alpha=1):
 for q in poly(g):
  q=orient(q,1);v=[];co=[]
  for ring in [q.exterior,*q.interiors]:
   z=np.asarray(ring.coords)/1000;v.extend(z);co.extend([MP.MOVETO]+[MP.LINETO]*(len(z)-2)+[MP.CLOSEPOLY])
  a.add_patch(PathPatch(MP(v,co),facecolor=c,edgecolor=edge,lw=lw,alpha=alpha))
def line(a,g,c=BLUE,lw=.7,ls='-'):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  x,y=np.asarray(g.coords).T/1000;a.plot(x,y,color=c,lw=lw,ls=ls)
 elif g.geom_type in ['Polygon','MultiPolygon']:line(a,g.boundary,c,lw,ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(a,q,c,lw,ls)
def label(a,g,text,size=8,c=INK):
 p=g if g.geom_type=='Point' else g.representative_point();a.text(p.x/1000,p.y/1000,text,ha='center',va='center',fontsize=size,color=c,bbox=dict(facecolor=BG,alpha=.88,pad=2,edgecolor='none'))
def canvas(bounds,size=(9,9)):
 f,a=plt.subplots(figsize=size,facecolor=BG);a.set_facecolor(BG);a.set_aspect('equal');a.axis('off');x,y,X,Y=np.array(bounds)/1000;a.set(xlim=(x,X),ylim=(y,Y));l=10 if X-x>20 else .5 if X-x>2 else .1;xx=x+.04*(X-x);yy=y+.03*(Y-y);a.plot([xx,xx+l],[yy,yy],color=INK,lw=2);a.text(xx,yy+.02*(Y-y),f'{l:g} km',fontsize=8,color=INK);a.annotate('N',xy=(X-.045*(X-x),Y-.02*(Y-y)),xytext=(X-.045*(X-x),Y-.12*(Y-y)),arrowprops=dict(arrowstyle='->',color=INK),ha='center',fontsize=9);f.subplots_adjust(.02,.05,.98,.98);return f,a
def save(f,name):p=D/(name+'.png');f.savefig(p,dpi=190,facecolor=BG);plt.close(f);return p
def legend(a,items):a.legend(handles=[Patch(facecolor=c,label=t) for t,c in items],loc='upper center',bbox_to_anchor=(.5,-.025),ncol=3,frameon=False,fontsize=8)
def base(a,bounds,mode='land'):
 w=box(*bounds)
 for g,p in land:
  if g.intersects(w):fill(a,g.intersection(w),PC[p['phase']] if mode=='phase' else (COL.get(p['use'],GREY) if mode=='land' else (COL[p['use']] if p['use'] in ['civic','school','daily_centre','dry_park'] else '#E1DFD5')),edge=BG,lw=.7)
 if mode not in ['phase','mobility']:
  for g,p in bld:
   if g.intersects(w):fill(a,g.intersection(w),'#8C6B54' if p['use']=='residential' else '#626F70',lw=0)
 for g,p in roads:
  if not g.intersects(w) or p.get('study_only'):continue
  if p['network']=='people':
   if mode in ['green','mobility']:line(a,g.intersection(w),GREEN if mode=='green' else RUST,2.4 if mode=='green' else 1.8,'--')
   continue
  if mode!='phase':line(a,g.intersection(w),BLUE if p['network']!='machine' else '#806365',2.5 if p['road_class']=='primary' else 1.5 if p['road_class']=='secondary' else .4)

def run():
 bounds=unary_union([g for g,p in scope]).bounds;f,a=canvas(bounds,(10,9))
 for g,p in regions:fill(a,g,RC[p['id']],edge=INK,lw=.5);label(a,g,p['id'] if p['id'].startswith('D00') or p['id']=='D01' else p['id']+'\n'+p['name'].replace(' and ',' + ').replace(' research','\nresearch'),7)
 for g,p in roads:
  if p['road_class'] in ['primary','secondary'] and (p.get('study_only') or g.length>2000):line(a,g,BLUE,1.8 if p['road_class']=='primary' else 1,'--')
 for g,p in ch:line(a,g.intersection(unary_union([q for q,v in scope])),'#7D9D98',.55)
 a.annotate('SW town + campuses\nsee city enlargement',xy=(574.6,6555.0),xytext=(590,6551),arrowprops=dict(arrowstyle='->',color=RUST,lw=1),fontsize=8,color=INK,bbox=dict(facecolor=BG,pad=3,edgecolor='none'))
 save(f,'whole-site')
 f,a=canvas(SYSTEM,(7,10));base(a,SYSTEM)
 for g,p in dist:line(a,g,RUST,1.2);label(a,g,p['id'],9)
 for g,p in nodes:line(a,g,RUST,1.6);label(a,g,p['node_id'],10)
 label(a,Point(574500,6553700),'1.1 km town / campus edge separation\nNo residential heat pipe credited',8)
 save(f,'system-layout')
 for mode,name in [('land','city-composite'),('mobility','city-mobility'),('green','city-landscape'),('phase','city-phasing')]:
  f,a=canvas(TOWN);base(a,TOWN,mode)
  if mode=='land':
   for g,p in dist:line(a,g,RUST,1);label(a,g,p['id']+'\n'+('PUBLIC BAND' if p['id']=='CENTRE' else 'LIVING DISTRICT'),9)
  if mode=='mobility':
   for x in [573800,574600,575400]:
    for y in [6554500,6555500,6556500]:a.scatter(x/1000,y/1000,s=30,facecolor=RUST,edgecolor=BG,zorder=5)
   label(a,Point(574600,6555520),'MAIN STREET / BUS SPINE',9)
  if mode=='green':
   label(a,Point(574500,6556300),'DRY COMMONS\n+ proposed shade links',9)
  if mode in ['mobility','green']:
   for g,p in land:
    if p['use'] in ['school','daily_centre']:label(a,g,'S' if p['use']=='school' else 'D',8)
  legend(a,[('Homes',COL['residential']),('Civic band',COL['civic']),('Schools',COL['school']),('Daily care + shops',COL['daily_centre']),('Dry parks',COL['dry_park']),('Review / open ground',GREY)] if mode=='land' else [('Primary / secondary street',BLUE),('Bus / walk study',RUST),('Dry landscape / shade opportunity',GREEN)] if mode!='phase' else [('P1 / complete west',PC[1]),('P2 / east',PC[2]),('P3 / north',PC[3])]);save(f,name)
 # Services map measures distance along actual orthogonal streets rather than circular promise.
 f,a=canvas(TOWN);base(a,TOWN,'mobility')
 for g,p in land:
  if p['use'] in ['school','daily_centre']:label(a,g,('S / '+str(750 if p['phase']<3 else 400)) if p['use']=='school' else 'D / care + shops',7)
 label(a,Point(574600,6555400),'MARKETS / LIBRARY / HEALTH / SPORTS',8);save(f,'city-services')
 for g,p in nodes:
  nid=p['node_id'];bb=g.buffer(50 if nid=='A01' else 120).bounds;f,a=canvas(bb,(9,7));base(a,bb)
  for q,pr in assets:
   if q.intersects(box(*bb)):line(a,q,'#3E596F',1)
  line(a,g,RUST,1.2)
  if nid=='A01':
   label(a,g,'A01 / shared court',9);label(a,Point(g.centroid.x,g.centroid.y-78),'Four detached bars / corner access gaps',7)
  elif nid=='B03':
   for q,pr in bld:
    if q.intersects(g) and pr['use']=='compute':label(a,q,'2 MW IT\nP'+str(pr['phase']),7)
   label(a,Point(574600,6552320),'SEPARATE WORKER SHADE ROUTE',8)
  else:
   label(a,Point(573400,6551200),'NEW TRIAL ROWS\nNo irrigation right assumed',8);label(a,Point(573400,6551500),'TRAINING / FARM SERVICE',8)
  save(f,nid+'-plan')
 # Geometry-derived, unexaggerated sectional relationships in metres.
 for nid in ['A01','B03','C02']:
  f,a=plt.subplots(figsize=(12,3.8),facecolor=BG);a.set_facecolor(BG);a.axis('off')
  if nid=='A01':
   a.fill_between([0,12],[9.6,9.6],color='#CDAA7F');a.fill_between([118,130],[9.6,9.6],color='#CDAA7F');a.fill_between([28,108],[4.2,4.2],[3.9,3.9],color='#A57552');a.set(xlim=(-8,138),ylim=(-3,15));a.text(65,11,'3 storeys / 9.6 m     +     shared court / 106 m clear',ha='center',color=INK);a.text(65,-2,'Detached bars and a 6 m deep shade canopy / conceptual level section',ha='center',color=INK)
  elif nid=='B03':
   a.fill_between([0,100],[10,10],color='#90A9B8');a.fill_between([230,330],[10,10],color='#90A9B8');a.fill_between([150,156],[4.2,4.2],[3.7,3.7],color='#A57552');a.set(xlim=(-15,345),ylim=(-5,25));a.text(170,18,'10 m halls / independent service yards / 6 m worker shade band',ha='center',color=INK);a.text(170,-4,'Local heat test remains on the productive campus; no pipe to homes',ha='center',color=INK)
  else:
   for x in range(0,140,18):a.plot([x,x+4],[2.4,3],color=BLUE,lw=3)
   a.fill_between([170,176],[4.2,4.2],[3.8,3.8],color='#A57552');a.fill_between([260,290],[6,6],color='#B09D7B');a.set(xlim=(-10,310),ylim=(-5,14));a.text(150,10,'Trial PV rows / dry test ground / public shade / farm service shed',ha='center',color=INK);a.text(150,-4,'Under-panel crop trials require lawful water and soil evidence before planting',ha='center',color=INK)
  a.axhline(0,color=INK,lw=1);f.subplots_adjust(.02,.1,.98,.95);save(f,nid+'-section')
if __name__=='__main__':run();print('Coordinated diagrams generated')
