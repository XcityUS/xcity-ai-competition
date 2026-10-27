"""Formal source-derived territorial axon: allocated roles, not installed solar infill."""
from diagrams_v2 import *
import sys
sys.path.insert(0,str(R/'scripts'));import make_scene as ms
from shapely import contains_xy
from matplotlib.colors import LightSource
sc=ms.Scene(str(P));territory=unary_union([g for g,p in scope]);x0,y0,x1,y1=territory.bounds
xs=np.linspace(x0,x1,180);ys=np.linspace(y0,y1,180);xx,yy=np.meshgrid(xs,ys);db=sc.db;hh,ww=sc.dem.shape
ix=np.clip(((xx-db[0])/(db[2]-db[0])*ww).astype(int),0,ww-1);iy=np.clip(((db[3]-yy)/(db[3]-db[1])*hh).astype(int),0,hh-1);zz=sc.dem[iy,ix];inside=contains_xy(territory,xx,yy);zz=np.where(inside,zz,np.nan)
ox,oy=x0,y0
f=plt.figure(figsize=(12,9),facecolor=BG);a=f.add_subplot(111,projection='3d',computed_zorder=False);a.set_facecolor(BG)
a.plot_surface((xx-ox)/1000,(yy-oy)/1000,zz/1000,color='#C7B699',rstride=2,cstride=2,linewidth=0,antialiased=True,alpha=.9,zorder=1)
def z(x,y):
 i=np.clip(int((x-db[0])/(db[2]-db[0])*ww),0,ww-1);j=np.clip(int((db[3]-y)/(db[3]-db[1])*hh),0,hh-1);return sc.dem[j,i]/1000

def trace(g,c,lw=.8,ls='-',offset=.02):
 if g.is_empty:return
 if g.geom_type in ['Polygon','MultiPolygon']:
  for q in poly(g):trace(q.exterior,c,lw,ls,offset)
 elif g.geom_type in ['LineString','LinearRing']:
  gg=g.segmentize(250);pts=np.asarray(gg.coords);a.plot((pts[:,0]-ox)/1000,(pts[:,1]-oy)/1000,[z(x,y)+offset for x,y in pts],color=c,lw=lw,ls=ls,zorder=4)
 elif hasattr(g,'geoms'):
  for q in g.geoms:trace(q,c,lw,ls,offset)
trace(territory,'#8E4935',1.3)
for g,p in regions:
 if p.get('plan_role')=='base_zoning' or p.get('district_id'):
  trace(g,'#A29B85',.45)
  q=g.representative_point();ident=p.get('district_id',p.get('id'));a.text((q.x-ox)/1000,(q.y-oy)/1000,z(q.x,q.y)+.09,ident,fontsize=8,color=INK,zorder=10)
for g,p in ch:trace(g.intersection(territory),BLUE,.7)
for g,p in roads:
 if g.geom_type.endswith('LineString') and g.length>2000:trace(g,RUST,.7,'--',.04)
q=Point(574400,6554000);a.scatter([(q.x-ox)/1000],[(q.y-oy)/1000],[z(q.x,q.y)+.04],s=60,facecolor='none',edgecolor=RUST,zorder=10)
a.text((q.x-ox)/1000+1,(q.y-oy)/1000,z(q.x,q.y)+.12,'Town + production\nsee local views',fontsize=8,color=INK,zorder=10)
a.set(xlim=(0,(x1-x0)/1000),ylim=(0,(y1-y0)/1000),zlim=(.4,2.8));a.set_box_aspect(((x1-x0)/1000,(y1-y0)/1000,2.4));a.view_init(elev=52,azim=-65);a.set_axis_off();f.subplots_adjust(0,.08,1,.98)
f.text(.05,.96,'WHOLE ISSUED SITE / TERRITORIAL FRAMEWORK',fontsize=14,fontweight='bold',color=INK)
f.text(.05,.045,'Brown: issued boundary   Blue: source seasonal channels   Dashed: proposed corridor studies\nDistrict edges denote allocated roles; neither installed works nor permanent water. Terrain in true relative scale.',fontsize=9,color=INK)
f.savefig(D/'whole-site-axon.png',dpi=180,facecolor=BG);plt.close(f)
print('Source-derived territorial axon exported; no invented installed fields')
