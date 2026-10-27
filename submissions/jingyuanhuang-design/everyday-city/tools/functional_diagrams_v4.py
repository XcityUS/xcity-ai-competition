"""Territorial land, overlapping functions and road argument from V4 geometry."""
from diagrams_v2 import *
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
O4=P/'reviews/functional-v4';account=json.loads((O4/'functional-account.json').read_text());basezones=[(g,p) for g,p in regions if p.get('plan_role')=='base_zoning'];over={p['system']:g for g,p in load(P/'geometry/structure.geojson') if p.get('plan_role')=='system_overlay'};territory=unary_union([g for g,p in scope]);bounds=territory.bounds
CC={'energy_compute':'#D9B957','agri_production':'#A9BD79','living':'#D99E83','industry':'#83A6B1','port':'#AE8CB6','retained':'#D3D2C8'}
NM={'energy_compute':'ENERGY + COMPUTE','agri_production':'AGRICULTURE','living':'LIVING + SERVICES','industry':'INDUSTRY','port':'TRADE + GATEWAYS','retained':'TERRAIN + DRAINAGE'}
def group(p):
 id=p['id'];return {'D00-F':'agri_production','D00-L':'living','D07':'retained','D06':'retained','D01':'living','D02':'agri_production','D04':'industry','D05-W':'port','D05-E':'port'}.get(id,'energy_compute')
def decorate(a,labels=True,roads_on=True):
 for g,p in ch:line(a,g.intersection(territory),'#638F99',.6)
 if roads_on:
  for g,p in roads:
   if p.get('road_class') in ['primary','secondary'] and (p.get('study_only') or g.length>2000):line(a,g.intersection(territory),'#37566B',1.4 if p['road_class']=='primary' else .75,'--')
 for g,p in fixed:line(a,g,'#53483C',.9)
 line(a,territory,'#604D44',1)
 if labels:
  for g,p in basezones:
   if g.area<5e6:continue
   label(a,g,p['id'],8)
 for g,p in nodes:
  q=g.centroid;a.scatter(q.x/1000,q.y/1000,s=16,c=RUST,edgecolor=BG,lw=.4,zorder=15)
def setup(a):
 a.set_aspect('equal');a.axis('off');x,y,X,Y=np.array(bounds)/1000;pad=1.6;a.set(xlim=(x-pad,X+pad),ylim=(y-pad,Y+pad));a.plot([x,x+10],[y-1,y-1],color=INK,lw=2);a.text(x,y-.3,'0                 10 km',fontsize=8,color=INK);a.annotate('N',xy=(X,Y),xytext=(X,Y-5),arrowprops=dict(arrowstyle='->',color=INK),ha='center',fontsize=9)
f=plt.figure(figsize=(14,9),facecolor=BG);a=f.add_axes([.025,.10,.66,.82]);setup(a)
for g,p in basezones:fill(a,g,CC[group(p)],edge=BG,lw=.6)
dual=over['energy_compute'].intersection(over['agri_production']).difference(unary_union([g for g,p in fixed]))
for q in poly(dual):
 # A translucent hatch marks shared agricultural territory, without panel geometry.
 pp=orient(q,1);v=[];co=[]
 for ring in [pp.exterior,*pp.interiors]:
  z=np.asarray(ring.coords)/1000;v.extend(z);co.extend([MP.MOVETO]+[MP.LINETO]*(len(z)-2)+[MP.CLOSEPOLY])
 a.add_patch(PathPatch(MP(v,co),facecolor='none',edgecolor='#847A47',lw=0,hatch='///',alpha=.55))
decorate(a)
f.text(.04,.96,'A PRODUCTIVE TERRITORY, WITH COMPACT LIVING',fontsize=18,fontweight='bold',color=INK)
f.text(.04,.925,'Whole issued site / V4 exclusive base land + co-use overlay / all allocations are resource-gated',fontsize=10,color=INK)
for i,k in enumerate(['energy_compute','agri_production','living','industry','port','retained']):
 y=.84-i*.106;v=account['exclusive_including_fixed'][k];f.patches.append(Rectangle((.72,y),.018,.025,transform=f.transFigure,facecolor=CC[k],edgecolor='none'));f.text(.75,y+.013,NM[k],fontsize=10,fontweight='bold',color=INK);f.text(.75,y-.012,f"{v['km2']:,.1f} km²  /  {v['pct']:.1f}% exclusive",fontsize=10,color=INK)
f.text(.72,.18,'HATCH / solar + crop co-use candidate\n362.2 km² new + 13.9 km² fixed context\nDo not add it to base land.',fontsize=9,color=INK,linespacing=1.5)
f.text(.72,.085,'Dashed: proposed regional road studies\nBlue: source seasonal channels\nDark outlines: unchanged fixed pilots\nA01 / B03 / C02: southwest detail views',fontsize=8,color=INK,linespacing=1.5)
f.text(.04,.025,'D01 living  |  D02 agriculture  |  D03-S/N/E energy  |  D04 processing corridor  |  D05-W/E compact gateways  |  D06/07 retained landscape',fontsize=9,color=INK)
f.savefig(D/'whole-site.png',dpi=190,facecolor=BG);plt.close(f)
# Distinct coverage plates: they answer an overlapping-functions question, not recoloured base land.
f=plt.figure(figsize=(14,8.6),facecolor=BG);f.text(.04,.955,'FIVE FUNCTIONS / THREE DIFFERENT ACCOUNTS',fontsize=18,fontweight='bold',color=INK)
f.text(.04,.915,'Whitepaper reference is strategic; exclusive land and overlapping coverage must not be confused.',fontsize=10,color=INK)
for j,(sys,title) in enumerate([('energy_compute','ENERGY COVERAGE / 61.0%'),('agri_production','AGRICULTURE / 31.1%'),('retained','RETAINED / 20.9%')]):
 a=f.add_axes([.035+j*.32,.35,.29,.53]);setup(a);fill(a,territory,'#E6E3D8')
 g=over[sys] if sys!='retained' else unary_union([g for g,p in basezones if group(p)=='retained']);fill(a,g,CC[sys]);decorate(a,False,False);a.set_title(title,fontsize=11,color=INK,fontweight='bold')
labels=['ENERGY + COMPUTE','AGRICULTURE','LIVING','INDUSTRY','TRADE / PORT'];keys=list(account['reference_pct'])
for i,k in enumerate(keys):
 x=.045+i*.19;ref=account['reference_pct'][k];val=account['functional_coverage'][k]['pct'];f.text(x,.275,labels[i],fontsize=9,fontweight='bold',color=INK);f.text(x,.235,f"REFERENCE ~{ref}%",fontsize=9,color=INK);f.text(x,.19,f"V4 {val:.1f}%",fontsize=16,fontweight='bold',color=CC[k])
f.text(.04,.12,'The 376.1 km² solar/agriculture intersection is counted in both functional systems, once in base land. Coverage does not sum to 100%.',fontsize=10,color=INK)
f.text(.04,.065,'CURRENT WORKS / 8.635 km² study footprint; 7.656 ha of new crop bands. Territorial envelopes do not add homes, IT MW or irrigation rights.\nRetained mountains and drainage remain visible. Future co-use requires soil, water, grid and access verification before a field is commissioned.',fontsize=9,color=INK,linespacing=1.6)
f.savefig(D/'functional-coverage.png',dpi=190,facecolor=BG);plt.close(f)
# Source-based terrain axon with functional colour; no solar panels invented in territorial polygons.
import sys;sys.path.insert(0,str(R/'scripts'));import make_scene as ms
from shapely import contains_xy
from matplotlib.colors import to_rgba
sc=ms.Scene(str(P));x0,y0,x1,y1=bounds;xs=np.linspace(x0,x1,220);ys=np.linspace(y0,y1,220);xx,yy=np.meshgrid(xs,ys);db=sc.db;hh,ww=sc.dem.shape
ix=np.clip(((xx-db[0])/(db[2]-db[0])*ww).astype(int),0,ww-1);iy=np.clip(((db[3]-yy)/(db[3]-db[1])*hh).astype(int),0,hh-1);zz=sc.dem[iy,ix]/1000;zz=np.where(contains_xy(territory,xx,yy),zz,np.nan);colors=np.zeros(xx.shape+(4,))
for g,p in basezones:colors[contains_xy(g,xx,yy)]=to_rgba(CC[group(p)])
f=plt.figure(figsize=(13,9),facecolor=BG);a=f.add_subplot(111,projection='3d',computed_zorder=False);a.set_facecolor(BG);a.plot_surface((xx-x0)/1000,(yy-y0)/1000,zz,facecolors=colors,rstride=1,cstride=1,shade=True,linewidth=0,antialiased=True)
def height(x,y):return sc.dem[np.clip(int((db[3]-y)/(db[3]-db[1])*hh),0,hh-1),np.clip(int((x-db[0])/(db[2]-db[0])*ww),0,ww-1)]/1000
def trace(g,color,lw=.6):
 if g.is_empty:return
 if g.geom_type in ['Polygon','MultiPolygon']:trace(g.boundary,color,lw)
 elif g.geom_type in ['LineString','LinearRing']:
  z=np.array(g.segmentize(250).coords);a.plot((z[:,0]-x0)/1000,(z[:,1]-y0)/1000,[height(x,y)+.025 for x,y in z],color=color,lw=lw,zorder=8)
 elif hasattr(g,'geoms'):
  for q in g.geoms:trace(q,color,lw)
trace(territory,'#604D44',1.1)
for g,p in ch:trace(g.intersection(territory),'#3D7589',.6)
for g,p in roads:
 if p.get('study_only') and g.geom_type.endswith('LineString'):trace(g,'#3C5060',.65)
for g,p in basezones:
 if g.area<15e6:continue
 q=g.representative_point();a.text((q.x-x0)/1000,(q.y-y0)/1000,height(q.x,q.y)+.1,p['id'],fontsize=8,color=INK,zorder=12)
a.view_init(elev=55,azim=-65);a.set_box_aspect(((x1-x0)/1000,(y1-y0)/1000,2.4),zoom=1.4);a.set_proj_type('ortho');a.set_axis_off();f.subplots_adjust(0,.1,1,.95)
f.text(.04,.96,'WHOLE-SITE TERRAIN + FUNCTIONAL STRUCTURE',fontsize=17,fontweight='bold',color=INK)
f.text(.04,.91,'Source terrain in true relative scale / issued boundary / source seasonal channels / proposed route studies',fontsize=10,color=INK)
f.legend(handles=[Patch(facecolor=CC[k],label=NM[k]) for k in CC],loc='lower center',bbox_to_anchor=(.5,.065),ncol=3,frameon=False,fontsize=9)
f.text(.04,.025,'Colours show allocated roles, not installed fields. Fixed pilots are retained. Local town/compute/farm rendering cameras remain local views.',fontsize=9,color=INK);f.savefig(D/'whole-site-axon.png',dpi=190,facecolor=BG);plt.close(f)
print('V4 territorial plan, overlapping functional plates and source-based colour axon exported')
