"""Spatial diagrams from the current design geometry; symbolic line widths are not areas."""
import json,math
from pathlib import Path
import numpy as np
from shapely import make_valid
from shapely.geometry import shape,box,Point,LineString
from shapely.ops import transform,unary_union
from shapely.geometry.polygon import orient
from pyproj import Transformer
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch,Patch
P=Path(__file__).resolve().parents[1];R=P.parents[2];V9=P/'reviews/complete-city-v9';V10=P/'reviews/presentation-v10';O=P/'reviews/presentation-v11';D=O/'drawings';D.mkdir(parents=True,exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda p:[(make_valid(transform(T,shape(f['geometry']))),f['properties']) for f in json.loads(p.read_text())['features']]
G=V10/'scene/geometry';regions=load(V9/'geometry/planning_regions.geojson');land=load(G/'land_use.geojson');roads=load(G/'movement.geojson');build=load(G/'buildings.geojson');nodes=load(G/'nodes.geojson');districts=load(G/'districts.geojson');scope=unary_union([g for g,p in load(R/'brief/site-package/boundaries/scope_9_13.geojson')]);channels=unary_union([g for g,p in load(R/'brief/site-package/water/channels_dem.geojson')]);regional=load(P/'reviews/whole-site-v3/corridors.geojson');centres=load(P/'reviews/whole-site-v3/centres.geojson');access=load(P/'reviews/district-structure-v8/access-studies.geojson');fixed=load(R/'brief/site-package/pilot-area/pilot_area.geojson')+load(R/'brief/site-package/pilot-area/pilot_living_area.geojson')
BG='#FCFBF6';INK='#213C47';C={'residential':'#F0D18F','mixed_use':'#D99B8C','school':'#7CA7C8','daily_centre':'#C98157','dry_park':'#A8C479','terrain_review':'#E5E6DD','streets':'#E1E5E3','dry_open_space':'#E9E8DD','public_commons':'#D8785E','civic':'#9D90AF','arrival':'#75A5B3','culture':'#BDA0BD','compute':'#7A9EA8','industry':'#B1A28B','infrastructure':'#95B1A4','energy':'#D9C36D','agriculture':'#B7C289','logistics':'#A894B5','operational_reserve':'#E7E5DC'}
WHOLE=scope.bounds;CITY=(572200,6555650,576250,6559250)
def poly(g):
 if g.is_empty:return
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from poly(q)
def fill(a,g,c,edge='none',lw=.3,alpha=1):
 for q in poly(g):
  q=orient(q,1);v=[];codes=[]
  for ring in [q.exterior,*q.interiors]:
   xy=np.asarray(ring.coords)/1000;v.extend(xy);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(xy)-2)+[MP.CLOSEPOLY])
  a.add_patch(PathPatch(MP(v,codes),facecolor=c,edgecolor=edge,lw=lw,alpha=alpha))
def line(a,g,c,lw,ls='-',z=3):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  xy=np.asarray(g.coords)/1000;a.plot(xy[:,0],xy[:,1],color=c,lw=lw,ls=ls,zorder=z,solid_capstyle='round')
 elif g.geom_type in ['Polygon','MultiPolygon']:line(a,g.boundary,c,lw,ls,z)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(a,q,c,lw,ls,z)
def label(a,pt,s,size=10,color=INK):
 p=pt if pt.geom_type=='Point' else pt.representative_point();a.text(p.x/1000,p.y/1000,s,fontsize=size,ha='center',va='center',color=color,zorder=20,bbox=dict(facecolor=BG,edgecolor='none',alpha=.94,pad=2))
def dot(a,p,color='#C46549',size=80,open=False):a.scatter([p.x/1000],[p.y/1000],s=size,facecolors='white' if open else color,edgecolors=color if open else 'white',linewidths=1.6,zorder=14)
def frame(a,b):
 x0,y0,x1,y1=np.array(b)/1000;a.set(xlim=(x0-.015*(x1-x0),x1+.015*(x1-x0)),ylim=(y0-.015*(y1-y0),y1+.015*(y1-y0)));a.set_aspect('equal');a.axis('off');a.set_facecolor(BG)
 s=10 if x1-x0>20 else .5;x=x0+.03*(x1-x0);y=y0+.03*(y1-y0);a.plot([x,x+s],[y,y],color=INK,lw=2);a.text(x,y+.025*(y1-y0),f'{s:g} km',fontsize=9)
 a.annotate('N',xy=(x1-.045*(x1-x0),y1-.03*(y1-y0)),xytext=(x1-.045*(x1-x0),y1-.16*(y1-y0)),arrowprops=dict(arrowstyle='->',color=INK,lw=1.5),ha='center',fontsize=10)
def save(f,name):
 f.subplots_adjust(0,0,1,1);p=D/(name+'.png');f.savefig(p,dpi=240,facecolor=BG,bbox_inches='tight',pad_inches=.05);plt.close(f);return p

def whole():
 f,a=plt.subplots(figsize=(10,10));f.set_facecolor(BG)
 rc={'Z1':'#E4B59A','Z2':'#BECE9D','Z3':'#E3D189','Z4':'#9ABCC5','Z5':'#BBA5C9','Z6':'#CDD6C6'}
 for g,p in regions:fill(a,g,rc[p['id']],INK,.7)
 # Existing source washes: symbolic ecological lines, not a width/setback or forest claim.
 line(a,channels.intersection(scope),'#F6F7EF',4.3);line(a,channels.intersection(scope),'#719D85',2.2)
 for g,p in regional:
  if (p.get('from_id'),p.get('to_id')) not in [('A','K1'),('K1','K2'),('K2','C'),('K1','D'),('D','E')]:continue
  q=g.intersection(scope);line(a,q,'white',5);line(a,q,'#315C81',2.5,'--')
 for g,p in access:
  if p.get('id') in ['A','F']:line(a,g.intersection(scope),'#C47B42',2,'--')
 for g,p in districts:line(a,g,'#465961',1)
 for g,p in fixed:fill(a,g,'#8C8068',INK,.6)
 pos={'Z1':(579000,6553000),'Z2':(568000,6584000),'Z3':(585000,6586000),'Z4':(595000,6572200),'Z5':(624000,6563800),'Z6':(611000,6559000)}
 short={'Z1':'URBAN + SERVICES','Z2':'AGRICULTURE RESEARCH','Z3':'ENERGY RESEARCH','Z4':'PRODUCTION + TRANSFER','Z5':'GATEWAY + LOGISTICS','Z6':'MOUNTAIN STEWARDSHIP'}
 for g,p in regions:label(a,Point(*pos[p['id']]),p['id']+'\n'+short[p['id']],11)
 for g,p in centres:
  if p.get('id') in ['A','C','D','E','K1','K2']:dot(a,g,'#315C81',45,True)
 frame(a,WHOLE);return save(f,'diagram-whole-site-composite')
# Source-aligned route proposals: exact existing street alignments; no new structures or capacity.
walklinks=[LineString([(574220,6556500),(574220,6558920)]),LineString([(573500,6557820),(575900,6557820)])]
features=[]
for i,g in enumerate(walklinks):features.append(dict(type='Feature',geometry=__import__('shapely').geometry.mapping(transform(I,g)),properties=dict(id='walk-shade-opportunity-'+str(i),kind='concept_overlay',basis='Existing street alignment; proposed walking/shade opportunity, not existing continuous tree cover',capacity_credit=0)))
(O/'concept-layers.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),indent=2)+'\n')

def local(mode='composite'):
 f,a=plt.subplots(figsize=(10,9));f.set_facecolor(BG);w=box(*CITY)
 fill(a,scope.intersection(w),'#F0EEE4',INK,.7)
 for g,p in nodes:
  if p['node_id']=='C03':fill(a,g,'#CFDEC1',edge='#7E9D74',lw=1.1,alpha=.75)
 for g,p in land:
  q=g.intersection(w)
  if q.is_empty:continue
  c=C.get(p['use'],'#E7E5DD')
  if mode=='movement' and p['use'] not in ['school','daily_centre','public_commons','arrival','dry_park','civic']:c='#E5E0D2'
  if mode=='green' and p['use'] not in ['dry_park','dry_open_space','terrain_review','public_commons']:c='#E8E4D8'
  fill(a,q,c,edge='#FFFFFF',lw=.45)
 for g,p in build:
  if g.intersects(w):fill(a,g,'#B16F4D' if p.get('form')=='canopy' else '#918C81',alpha=.65)
 for g,p in roads:
  q=g.intersection(w)
  if q.is_empty:continue
  if p.get('district') in ['R','C']:
   hierarchy=p.get('hierarchy','local');wide=hierarchy in ['primary','secondary']
   line(a,q,'white',4 if wide else 1.8)
   if wide:line(a,q,'#315C81',2.0 if mode!='green' else 1.2)
  elif p.get('network')=='people':line(a,q,'#719E56',.65)
 line(a,channels.intersection(w),'#86A795',2)
 if mode in ['green','composite']:
  for g in walklinks:line(a,g,'white',6);line(a,g,'#78A14A',3.5)
 # Proposed passenger spine was already used in the V9 mobility sheet.
 bus=LineString([(574200,6556050),(574200,6556500),(574700,6556500),(574700,6558700)])
 if mode in ['movement','composite']:
  line(a,bus,'white',5.5);line(a,bus,'#BD6549',2.3,'--')
  for y in [6556650,6557100,6557550,6558000,6558450,6558700]:dot(a,Point(574700,y),'#BD6549',42,True)
 for g,p in land:
  if p['use'] in ['school','daily_centre'] and g.intersects(w):
   dot(a,g.centroid,'#4B7C9D' if p['use']=='school' else '#BD6549',80)
   if mode!='green':label(a,g.centroid,'S' if p['use']=='school' else 'D',8)
 if mode=='composite':
  label(a,Point(573870,6556900),'SOUTHWEST\nLIVING PRECINCT',10)
  label(a,Point(575230,6557200),'SOUTHEAST\nLIVING PRECINCT',10)
  label(a,Point(574900,6558700),'NORTH\nLIVING PRECINCT',10)
  label(a,Point(574200,6556220),'C / PUBLIC CENTRE',10)
  label(a,Point(572900,6558000),'C03 / DRY-WASH\nLANDSCAPE PARK',10)
 elif mode=='movement':
  label(a,Point(574075,6555990),'MAIN PASSENGER ARRIVAL',9)
  label(a,Point(575250,6558300),'BUS + SECONDARY\nSTREET SPINE',10)
  label(a,Point(573820,6556450),'FREIGHT SERVES P\nIN A SEPARATE INSET',8)
 else:
  label(a,Point(572920,6558050),'SEASONAL WASH\nLANDSCAPE STUDY',10)
  label(a,Point(574220,6558500),'PROPOSED SHADE\nAND WALK LINKS',10)
  label(a,Point(575450,6556650),'DRY PARKS +\nTARGETED PLANTING',9)
 frame(a,CITY);return save(f,'diagram-'+mode)

def build_diagrams():return {'whole-composite':whole(),'city-composite':local('composite'),'network-composite':local('movement'),'green-composite':local('green')}
if __name__=='__main__':print(build_diagrams())
