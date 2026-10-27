"""Render public-brief maps from the issued repository site package (no new screening model)."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Polygon as Patch,Circle
from matplotlib.path import Path as MPath
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
O=Path(__file__).resolve().parent;R=O.parents[1]/'brief/site-package';BG='#F7F5F0';INK='#30302E'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'figure.facecolor':BG,'savefig.facecolor':BG})
def read(p):return json.loads((R/p).read_text())
def geometries(p):
 d=read(p);return [shape(f['geometry']) for f in d['features']]
to_utm=Transformer.from_crs(4326,32719,always_xy=True).transform
site=transform(to_utm,geometries('boundaries/scope_9_13.geojson')[0]); bounds=site.bounds;xm=(bounds[0]+bounds[2])/2;ym=(bounds[1]+bounds[3])/2;delta=max(bounds[2]-bounds[0],bounds[3]-bounds[1])/2+4500
x0,x1,y0,y1=xm-delta,xm+delta,ym-delta,ym+delta
summary=read('terrain/terrain_summary_9_13.json');rb=summary['files']['hillshade_utm_bounds_m'];ext=(rb[0],rb[2],rb[1],rb[3])
dem=np.asarray(Image.open(R/'terrain/dem_9_13_utm19s_60m.png')).astype(float);hill=np.asarray(Image.open(R/'terrain/hillshade_9_13_utm.png'))
dy,dx=np.gradient(dem,60);slope=np.sqrt(dx*dx+dy*dy)*100
padded=np.pad(slope,2,mode='edge');slope=sum(padded[i:i+slope.shape[0],j:j+slope.shape[1]] for i in range(5) for j in range(5))/25
h,w=dem.shape;xx=np.linspace(rb[0]+30,rb[2]-30,w);yy=np.linspace(rb[3]-30,rb[1]+30,h);gx,gy=np.meshgrid(xx,yy)
mask=np.zeros(dem.shape,bool)
def parts(g):return list(g.geoms) if hasattr(g,'geoms') else [g]
for p in parts(site):mask|=MPath(np.asarray(p.exterior.coords)).contains_points(np.c_[gx.ravel(),gy.ravel()]).reshape(dem.shape)
roads=[transform(to_utm,g) for g in geometries('access/roads_osm.geojson')]
channels=[transform(to_utm,g) for g in geometries('water/channels_dem.geojson')]
flood=[transform(to_utm,g) for g in geometries('water/flood_sensitive_dem.geojson')]
pilot=[transform(to_utm,g) for g in geometries('pilot-area/pilot_area.geojson')]
living=[transform(to_utm,g) for g in geometries('pilot-area/pilot_living_area.geojson')]
colors={'compute':'#5E92BE','agri':'#73A467','living':'#DB873D','industry':'#B56699','port':'#8E7AB5'}
def lines(ax,gs,color,lw,z=2):
 for g in gs:
  for p in parts(g):
   if p.geom_type=='Polygon':p=p.exterior
   if p.geom_type in ['LineString','LinearRing']:ax.plot(*p.xy,color=color,lw=lw,zorder=z)
def fill(ax,gs,color,alpha=1,z=3):
 for g in gs:
  for p in parts(g):
   if p.geom_type=='Polygon':ax.add_patch(Patch(np.asarray(p.exterior.coords),facecolor=color,edgecolor='none',alpha=alpha,zorder=z))
def base(wh=(5,5.6),streams=True,road=True):
 fig,ax=plt.subplots(figsize=wh,dpi=220);fig.subplots_adjust(left=.01,right=.99,bottom=.01,top=.99);ax.set_facecolor(BG)
 ax.imshow(hill,extent=ext,cmap='Greys_r',vmin=-80,vmax=330,origin='upper',zorder=0)
 if road:lines(ax,roads,'#8C7B60',.55)
 if streams:lines(ax,channels,'#4E8DB8',.6)
 lines(ax,[site],INK,.9,6);ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal');ax.axis('off');return fig,ax

def embellish(ax):
 ax.annotate('N',xy=(x1-3500,y1-1800),xytext=(x1-3500,y1-9500),ha='center',fontsize=8,arrowprops={'arrowstyle':'->','lw':.7},zorder=10)
 ax.plot([x1-24000,x1-4000],[y0+4500]*2,color=INK,lw=.8,zorder=10);ax.text(x1-24000,y0+5600,'20 km',fontsize=7,zorder=10)
def save(fig,name):
 for lang in ['en','zh']:fig.savefig(O/f'assets/{lang}/{name}',dpi=220)
 plt.close(fig)
fig,ax=base();embellish(ax);save(fig,'site-context.png')
fig,ax=base();fill(ax,pilot,'#D6AA39',1,7);fill(ax,living,'#DB873D',1,7)
for num,g in enumerate(pilot,1):ax.text(g.centroid.x,g.centroid.y,str(num),fontsize=6,ha='center',zorder=8)
ax.annotate('L',xy=(living[0].centroid.x,living[0].centroid.y),xytext=(living[0].centroid.x+6500,living[0].centroid.y-3000),fontsize=9,color='#A85823',arrowprops={'arrowstyle':'-','lw':.5},zorder=9)
embellish(ax);save(fig,'lead-zone.png')
for name,data,cmap,norm in [('elevation.png',dem,'terrain',None),('slope.png',slope,ListedColormap(['#DAD7AD','#A7B790','#A88B61','#666254']),BoundaryNorm([0,2,5,15,1e6],4))]:
 fig,ax=base(streams=False,road=False);ax.imshow(np.ma.masked_where(~mask,data),extent=ext,cmap=cmap,norm=norm,zorder=3);lines(ax,[site],INK,.9,6);embellish(ax);save(fig,name)
fig,ax=base(road=False);embellish(ax);save(fig,'drainage.png')
fig,ax=base(streams=False,road=False);fill(ax,flood,'#78A5C2',.85);embellish(ax);save(fig,'flood-screen.png')
fig,ax=base(streams=False,road=False);flat=mask&(slope<2);ax.imshow(np.ma.masked_where(~flat,np.ones(dem.shape)),extent=ext,cmap=ListedColormap(['#84A478']),vmin=0,vmax=1,zorder=3);fill(ax,flood,BG,1,4);lines(ax,[site],INK,.9,6);embellish(ax);save(fig,'buildable-screen.png')
systems=read('zoning/indicative_systems_9_13.json')['systems']
def drawsystem(ax,name):
 obj=systems[name]
 for lon,lat in obj['points_lonlat']:
  x,y=to_utm(lon,lat)
  if name in ['agri','compute']:
   circ=Circle((x,y),obj['halo_km']*1000,color=colors[name],alpha=.12,zorder=4);ax.add_patch(circ)
  ax.scatter(x,y,s=28,facecolors='none' if obj.get('later_phase') else colors[name],edgecolors=colors[name],linewidths=1.3,zorder=8)
for name in systems:
 fig,ax=base((2.6,2.8));drawsystem(ax,name);save(fig,'system-'+name+'.png')
fig,ax=base((5.4,6.6))
for name in systems:drawsystem(ax,name)
embellish(ax);save(fig,'systems-overview.png')
print('Updated maps from issued site package')
