"""Territorial axon and an explicitly enlarged production interface from source geometry."""
import runpy,math,json
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import box
from matplotlib.patches import Polygon
from matplotlib.colors import to_rgb
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];v=runpy.run_path(str(P/'tools/concept_diagrams_v11.py'));O=P/'reviews/production-v12';G=O/'geometry'
B=v['load'](G/'buildings.geojson');M=v['load'](G/'movement.geojson');plant=v['load'](G/'shared-plant.geojson');assets=v['load'](P/'reviews/complete-city-v9/geometry/assets.geojson');scope=v['scope'];dem=np.asarray(Image.open(v['R']/'brief/site-package/terrain/dem_9_13_utm19s_60m.png'),dtype=float);origin=scope.centroid
height=lambda x,y:float(dem[min(dem.shape[0]-1,max(0,int((6608973.7-y)/60))),min(dem.shape[1]-1,max(0,int((x-559572.4)/60)))])
def proj(x,y,z=0,flat=False):return(.84*(x-origin.x)-.53*(y-origin.y),.28*(x-origin.x)+.44*(y-origin.y)+(0 if flat else height(x,y))+z)
def pieces(g):
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from pieces(q)
def shape(ax,g,color,z=0,flat=False,edge=None,lw=.2):
 for q in pieces(g):ax.add_patch(Polygon([proj(x,y,z,flat) for x,y in q.exterior.coords],facecolor=color,edgecolor=edge or color,lw=lw))
def line(ax,g,c,lw=1,flat=False,ls='-'):
 if g.geom_type in ['LineString','LinearRing']:
  xy=np.array([proj(x,y,2,flat) for x,y in g.coords]);ax.plot(xy[:,0],xy[:,1],c=c,lw=lw,ls=ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(ax,q,c,lw,flat,ls)
def hall(ax,g,p,flat=False):
 h=p.get('height_m',7);xy=list(g.exterior.coords)
 for i in range(len(xy)-1):
  x,y=xy[i];xx,yy=xy[i+1];pts=[proj(x,y,0,flat),proj(xx,yy,0,flat),proj(xx,yy,h,flat),proj(x,y,h,flat)];ax.add_patch(Polygon(pts,facecolor='#AFB6AD',edgecolor='#707E78',lw=.15))
 shape(ax,g,'#456F7B' if p.get('use')=='compute' else '#B9AE95',h,flat,edge='#56706E')
f=plt.figure(figsize=(22,13),facecolor=v['BG']);f.text(.03,.95,'AGUA FINITA / THE ENERGY LANDSCAPE AND THE CITY',fontsize=24,color=v['INK'],weight='bold');f.text(.03,.915,'V12 spatial control / full issued territory with a production enlargement / source terrain, no vertical exaggeration',fontsize=12,color=v['INK'])
a=f.add_axes([.02,.13,.57,.72]);tiles=[]
for g,p in v['regions']:
 x0,y0,x1,y1=g.bounds
 for x in np.arange(math.floor(x0/1500)*1500,x1,1500):
  for y in np.arange(math.floor(y0/1500)*1500,y1,1500):
   for q in pieces(g.intersection(box(x,y,x+1500,y+1500))):
    if q.area>1:tiles.append((q,p))
for q,p in sorted(tiles,key=lambda t: .28*t[0].centroid.x+.44*t[0].centroid.y,reverse=True):
 c=q.centroid;shade=max(.84,min(1.08,1+(height(c.x-250,c.y)-height(c.x+250,c.y))/1800));col=np.clip(np.array(to_rgb(p['color']))*shade,0,1);shape(a,q,col)
future=v['load'](G/'territorial-fields.geojson') if (G/'territorial-fields.geojson').exists() else []
for g,p in future:shape(a,g,'#A8B56E',edge='#D5D5B3',lw=.12)
line(a,v['channels'].intersection(scope),'#53889F',.6)
for g,p in v['regional']:line(a,g,'#55655F',.7,ls='--')
for g,p in v['fixed']:shape(a,g,'#C8A84F',edge='#786A3C',lw=.7)
for g,p in v['land']:
 if p.get('use') in ['residential','compute','energy','industry','civic','mixed_use']:shape(a,g,v['C'].get(p['use'],'#B5BBAE'))
for g,p in assets:
 if p['type']=='pv_field':shape(a,g,'#4D7379')
for q in pieces(scope):line(a,q.boundary,v['INK'],1.1)
for g,p in v['regions']:
 c=g.representative_point();x,y=proj(c.x,c.y);a.text(x,y,p['id'],fontsize=11,color=v['INK'],ha='center',bbox=dict(facecolor=v['BG'],edgecolor='none',alpha=.9,pad=2))
a.autoscale();a.set_aspect('equal');a.axis('off')
b=f.add_axes([.61,.33,.37,.49]);clip=box(573050,6552000,574800,6554800)
for g,p in v['land']:
 q=g.intersection(clip)
 if not q.is_empty:shape(b,q,v['C'].get(p['use'],'#D8D4C3'),flat=True)
for g,p in M:
 q=g.intersection(clip)
 if not q.is_empty:line(b,q,'#8C9C90',1,True)
for g,p in assets:
 q=g.intersection(clip)
 if not q.is_empty:
  if p['type']=='pv_row':line(b,q,'#375E69',.5,True)
  elif p['type']=='pv_field':shape(b,q,'#CABF76',flat=True,edge='#9E8B3C')
for g,p in plant:shape(b,g,'#8FA78E',flat=True)
for g,p in sorted(B,key=lambda t:t[0].centroid.y,reverse=True):
 if clip.covers(g):hall(b,g,p,True)
b.autoscale();b.set_aspect('equal');b.axis('off');b.set_title('PRODUCTION INTERFACE / ENLARGED',loc='left',fontsize=13,color=v['INK'])
f.text(.61,.27,'PV extensions + crop operations\nShared power / cooling plots + modular compute halls\nRepair workshops + separate service access',fontsize=12,color=v['INK'],linespacing=1.6,va='top')
f.text(.61,.12,'Z1  Southwest city + production     Z2  Agricultural research\nZ3  Energy / solar-agricultural opportunity\nZ4  Production + transfer     Z5  Gateway     Z6  Mountain stewardship',fontsize=10,color=v['INK'],linespacing=1.7)
f.text(.03,.045,'Olive fields are resource-gated long-term agrivoltaic proposals, not completed arrays. Gold outlines identify fixed pilots without replacing their internal layout.\nIndividual buildings are small at territorial scale. The inset uses a flat working datum; terrain fit and equipment engineering remain open.',fontsize=10,color=v['INK'],linespacing=1.7)
f.savefig(O/'overall-energy-axon.png',dpi=150,facecolor=v['BG']);plt.close(f)
print(O/'overall-energy-axon.png')
