"""Original English review sheets and geometry-derived massing controls. No legacy node aliases."""
import json, textwrap
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly,Patch
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import shape,box,LineString
from shapely.ops import transform,unary_union
from shapely.geometry.polygon import orient
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=R/'brief/site-package';O=P/'pages';O.mkdir(exist_ok=True)
t=Transformer.from_crs(4326,32719,always_xy=True).transform
load=lambda p:[(transform(t,shape(f['geometry'])),f['properties']) for f in json.loads(p.read_text())['features']]
geo={n:load(P/'geometry'/f'{n}.geojson') for n in ['structure','master_area','land_use','buildings','movement','nodes','phasing']}
scope=unary_union([g for g,p in load(S/'boundaries/scope_9_13.geojson')]);pilot=unary_union([g for g,p in load(S/'pilot-area/pilot_area.geojson')]);living=unary_union([g for g,p in load(S/'pilot-area/pilot_living_area.geojson')]);channels=unary_union([g for g,p in load(S/'water/channels_dem.geojson')]);flood=unary_union([g for g,p in load(S/'water/flood_sensitive_dem.geojson')])
master=geo['master_area'][0][0];x0,y0=json.loads((P/'tools/selected_site.json').read_text())['origin_utm_m'];qa=json.loads((P/'report/geometry-qa.json').read_text())
BG='#f5f1e8';INK='#263b3b';TEAL='#275f62';GOLD='#c79955';RED='#b7644e';COL={'living':'#c88868','energy_compute':'#6b8f95','agri_production':'#a9b397','industry':'#b8a079','port':'#b58b99','reserve':'#e3dfd3','residential':'#c88868','civic':'#cfb56c','compute':'#6b8f95','energy':'#a6b799','open_space':'#ece6d5','infrastructure':'#aeb9b8'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK,'axes.labelcolor':INK})
index=[]
def parts(g):
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from parts(q)
def fill(ax,g,c,edge='none',lw=.4,alpha=1):
 for q in parts(g):
  q=orient(q,sign=1);vs=[];codes=[]
  for ring in [q.exterior,*q.interiors]:
   a=np.asarray(ring.coords)/1000;vs.extend(a);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(a)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(vs,codes),facecolor=c,edgecolor=edge,lw=lw,alpha=alpha))
def line(ax,g,c,lw=1,ls='-'):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  a=np.asarray(g.coords)/1000;ax.plot(a[:,0],a[:,1],color=c,lw=lw,ls=ls)
 elif g.geom_type in ['Polygon','MultiPolygon']:line(ax,g.boundary,c,lw,ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(ax,q,c,lw,ls)
def new(num,title,sub):
 fig=plt.figure(figsize=(16.54,11.69),facecolor=BG)
 fig.text(.045,.953,'THE EVERYDAY CITY',size=11,weight='bold',color=TEAL)
 fig.text(.955,.953,f'XCITY / DESIGN REVIEW 01 / {num:02d}',size=9,ha='right')
 fig.text(.045,.898,title,size=25,weight='bold');fig.text(.045,.861,sub,size=11)
 fig.text(.045,.026,'Jingyuan Huang  |  27 October 2026  |  Concept proposal; capacities assumed unless stated; no approval claimed.',size=8)
 fig.text(.955,.026,f'{num:02d}',ha='right',size=10)
 return fig

def note(fig,x,y,title,body,width=45):
 fig.text(x,y,title,size=14,weight='bold',color=TEAL,va='top')
 fig.text(x,y-.04,'\n'.join(textwrap.wrap(body,width)),size=11,va='top',linespacing=1.55)
def finish(fig,num,key):
 path=O/f'{num:02d}-{key}.png';fig.savefig(path,dpi=150,facecolor=BG);plt.close(fig);index.append({'number':num,'path':str(path.relative_to(P)),'title':key.replace('-',' ').title()})
def frame(ax,bounds,pad=.05):
 a,b,c,d=bounds;dx=(c-a)*pad;dy=(d-b)*pad;ax.set_xlim((a-dx)/1000,(c+dx)/1000);ax.set_ylim((b-dy)/1000,(d+dy)/1000);ax.set_aspect('equal');ax.axis('off')
 ax.annotate('N',xy=(.965,.96),xytext=(.965,.86),xycoords='axes fraction',ha='center',arrowprops={'arrowstyle':'->','color':INK},color=INK)
 scale=100 if c-a<3000 else 1000 if c-a<15000 else 10000;xx=a/1000;yy=(b-(d-b)*.025)/1000;ax.plot([xx,xx+scale/1000],[yy,yy],color=INK,lw=2);ax.text(xx,yy-(d-b)/1000*.026,f'{scale:g} m',fontsize=8)
def mastermap(ax,bounds=None,movement=True):
 for g,p in geo['land_use']:fill(ax,g,COL.get(p['use'],'#d1c5ac'))
 for g,p in geo['buildings']:fill(ax,g,'#f9f7ef' if p.get('form')!='canopy' else '#dfc177',INK,.32)
 if movement:
  for g,p in geo['movement']:
   if g.geom_type=='LineString':line(ax,g,TEAL if p['network']=='people' else RED,.8 if p['network']=='people' else 1.2,'-' if p['network']=='people' else '--')
 frame(ax,bounds or (x0,y0,x0+1900,y0+1400))
