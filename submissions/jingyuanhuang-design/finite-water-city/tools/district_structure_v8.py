"""AGUA FINITA V8: district relationships before dwelling quotas or rendering.
Run from the repository root. V7 and the published submission are preserved.
"""
import json, hashlib, heapq, math, textwrap, shutil, warnings
from pathlib import Path
warnings.filterwarnings('ignore',category=DeprecationWarning)
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import PathPatch, Patch
from matplotlib.path import Path as MP
from shapely.geometry import shape, mapping, box, Point, LineString
from shapely.geometry.polygon import orient
from shapely.ops import transform, unary_union, nearest_points
from shapely import contains_xy
from pyproj import Transformer

P=Path(__file__).resolve().parents[1]; R=P.parents[2]; S=R/'brief/site-package'
O=P/'reviews/district-structure-v8'; O.mkdir(parents=True,exist_ok=True)
OUT=R.parents[1]/'outputs/agua-finita-v8'; OUT.mkdir(parents=True,exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform; I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:[(transform(T,shape(z['geometry'])),z['properties']) for z in json.loads(f.read_text())['features']]
U=lambda f:unary_union([g for g,p in load(f)])
scope=U(S/'boundaries/scope_9_13.geojson'); fields=U(S/'pilot-area/pilot_area.geojson'); living=U(S/'pilot-area/pilot_living_area.geojson'); fixed=fields.union(living)
channel=U(S/'water/channels_dem.geojson'); flood=U(S/'water/flood_sensitive_dem.geojson')
dem=np.asarray(Image.open(S/'terrain/dem_9_13_utm19s_60m.png'),dtype=float); dy,dx=np.gradient(dem,60); slope=np.hypot(dx,dy)*100
xmin,ymax=559572.4,6608973.7
xs=xmin+(np.arange(dem.shape[1])+.5)*60; ys=ymax-(np.arange(dem.shape[0])+.5)*60
revision=json.loads((S/'boundaries/boundary-revision.json').read_text())
added_seam=scope.difference(U(S/'boundaries/archive/2026-10-26/scope_9_13.geojson'))

res=box(573500,6556500,576000,6559000).intersection(scope)
core=box(573700,6555900,574700,6556500).intersection(scope)
prod=box(573100,6552000,574700,6553100)
res_s=res.intersection(box(570000,6550000,580000,6557800));res_n=res.difference(res_s)
r0=box(573600,6556500,574800,6557800).intersection(res)
c0=box(574000,6556100,574400,6556400)
p0=box(573400,6552200,574000,6552500)
commons=box(574060,6556160,574210,6556260)
park=box(572300,6556800,573450,6558400).intersection(scope)
old_v7=box(575400,6551300,576100,6551900)
old_east=box(575400,6551000,576500,6552200)
districts=[(res,dict(id='R',role='residential_district',name='Continuous residential district',phase='1-2',extent_basis='Planning envelope; not fully built in Phase 1')),
 (core,dict(id='C',role='town_centre',name='Town-centre transition and reserve',phase='1-2',extent_basis='Gross mixed-use study; only C0 is the initial activity core')),
 (prod,dict(id='P',role='productive_precinct',name='Separate compute / repair precinct',phase='1-2',extent_basis='Production planning envelope; first works P0'))]
releases=[(r0,dict(id='R0',parent='R',phase=1,role='first_release',name='First housing release candidate')),(c0,dict(id='C0',parent='C',phase=1,role='first_release',name='First activity / arrival core')),(p0,dict(id='P0',parent='P',phase=1,role='first_release',name='First production module'))]
nodes=[(commons,dict(node_id='A03',phase=1,name='Arrival commons and climate refuge')),(prod,dict(node_id='B03',phase=1,name='Independent compute and repair precinct')),(park,dict(node_id='C03',phase=2,name='Seasonal wash park; conveyance protected from outset'))]
services=[(box(574050,6557000,574250,6557200),dict(kind='school',name='South school / shared sport reservation',phase=1,capacity_status='Derive from housing and age scenario before occupancy')),
 (box(574050,6558100,574250,6558300),dict(kind='school',name='North school expansion reservation',phase=2,capacity_status='Only opens with corresponding housing and service need')),
 (Point(574100,6556900),dict(kind='daily_centre',name='South daily centre',phase=1)),
 (Point(574650,6558150),dict(kind='daily_centre',name='North daily centre',phase=2)),
 (Point(574250,6556300),dict(kind='civic_service',name='Initial care / market / public transport',phase=1))]
def ft(g,**p):return dict(type='Feature',geometry=mapping(transform(I,g)),properties=p)
def write_geo(name,items):
 (O/name).write_text(json.dumps(dict(type='FeatureCollection',features=[ft(g,**p) for g,p in items]),indent=2)+'\n')
write_geo('districts.geojson',districts);write_geo('release-candidates.geojson',releases);write_geo('nodes.geojson',nodes);write_geo('service-reservations.geojson',services)

# Full distribution of source DEM cell slopes, not a convenient single centre-cell sample.
def stats(g):
 x0,y0,x1,y1=g.bounds;rr=(ys>=y0)&(ys<=y1);cc=(xs>=x0)&(xs<=x1);X,Y=np.meshgrid(xs[cc],ys[rr]);v=slope[np.ix_(rr,cc)][contains_xy(g,X,Y)]
 return dict(hydrologically_unclassified_seam_m2=round(g.intersection(added_seam).area,1),projected_km2=round(g.area/1e6,4),source_dem_cells=len(v),slope_median_pct=round(float(np.median(v)),2),slope_p95_pct=round(float(np.percentile(v,95)),2),share_cells_below_3pct=round(float(np.mean(v<3)*100),1),flood_screen_overlap_pct=round(g.intersection(flood).area/g.area*100,2),distance_to_dem_channel_m=round(g.distance(channel)),fixed_pilot_overlap_m2=round(g.intersection(fixed).area,3))
terrain={k:stats(g) for k,g in [('R',res),('C',core),('P',prod),('V7_east_plot',old_v7),('V7_east_alternative',old_east)]}

# 300 m route search. These are alternative corridor studies, never engineered roads.
nr,nc=dem.shape[0]//5,dem.shape[1]//5
z=dem[:nr*5,:nc*5].reshape(nr,5,nc,5).mean((1,3));gy,gx=np.gradient(z,300);sg=np.hypot(gx,gy)*100
rx=xmin+(np.arange(nc)+.5)*300;ry=ymax-(np.arange(nr)+.5)*300;X,Y=np.meshgrid(rx,ry)
inside=contains_xy(scope.buffer(-35),X,Y);wet=contains_xy(flood,X,Y)
basecost=1+np.minimum(sg,30)**2*.2+wet*4
basecost[~inside]=np.inf;basecost[sg>12]=np.inf;basecost[contains_xy(fixed.buffer(120),X,Y)]=np.inf
freight_exclusion=res.buffer(200).union(core.buffer(200))
costfreight=basecost.copy();costfreight[contains_xy(freight_exclusion,X,Y)]=np.inf
west_row=scope.intersection(LineString([(scope.bounds[0]-1000,6557400),(scope.bounds[2]+1000,6557400)]))
gate=Point(west_row.bounds[0],6557400)
def snap(p,cost):
 rr,cc=np.where(np.isfinite(cost));ii=np.argmin((rx[cc]-p.x)**2+(ry[rr]-p.y)**2);return int(rr[ii]),int(cc[ii])
def route(p,q,cost):
 a,b=snap(p,cost),snap(q,cost);dist={a:0};previous={};heap=[(0,a)];seen=set()
 while heap:
  d,u=heapq.heappop(heap)
  if u in seen:continue
  seen.add(u)
  if u==b:break
  for dr,dc in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
   v=(u[0]+dr,u[1]+dc)
   if not(0<=v[0]<nr and 0<=v[1]<nc) or not np.isfinite(cost[v]):continue
   seg=LineString([(rx[u[1]],ry[u[0]]),(rx[v[1]],ry[v[0]])])
   if not scope.covers(seg) or seg.intersects(fixed.buffer(100)):continue
   if cost is costfreight and seg.intersects(freight_exclusion):continue
   nd=d+math.hypot(dr,dc)*(cost[u]+cost[v])/2
   if nd<dist.get(v,math.inf):dist[v]=nd;previous[v]=u;heapq.heappush(heap,(nd,v))
 if b not in dist:raise RuntimeError('No route: do not invent a direct connection')
 cells=[b]
 while cells[-1]!=a:cells.append(previous[cells[-1]])
 pts=[(rx[c],ry[r]) for r,c in reversed(cells)]
 # Endpoint links are separately tested and retained only if they meet the same exclusions.
 for point,front in [(p,True),(q,False)]:
  endpoint=Point(pts[0] if front else pts[-1]);seg=LineString([point,endpoint])
  if scope.buffer(.01).covers(seg) and not seg.intersects(fixed.buffer(100)) and (cost is not costfreight or not seg.intersects(freight_exclusion)):
   if front:pts.insert(0,(point.x,point.y))
   else:pts.append((point.x,point.y))
 return LineString(pts)
gate_inner=gate
freight=route(gate,Point(573300,6552500),costfreight)
passenger=route(gate,Point(574000,6556250),basecost)
shuttle=route(Point(574000,6556250),Point(573300,6552500),basecost)
fixed_edge=nearest_points(living,Point(580000,6550000))[0]
fixed_link=route(fixed_edge.buffer(160).boundary.interpolate(.5,normalized=True),Point(574000,6556250),basecost)
route_items=[(freight,dict(id='F',kind='freight_study',name='Production access bypasses R and C',phase=1)),(passenger,dict(id='A',kind='passenger_study',name='Regional arrival to town-centre edge',phase=1)),(shuttle,dict(id='S',kind='shuttle_study',name='Worker shuttle between independent districts',phase=1)),(fixed_link,dict(id='L',kind='fixed_quarter_study',name='Fixed-quarter connection; not a walking catchment',phase=1))]
for g,p in route_items:
 p.update(channel_intersection_empty=g.intersection(channel).is_empty,channel_overlap_m=round(g.intersection(channel).length,2),status='study_only',authority='not_secured',basis='300 m source DEM least-cost alignment; not engineering or right of way',length_km=round(g.length/1000,2),flood_screen_km=round(g.intersection(flood).length/1000,2),channel_intersection=g.intersection(channel).geom_type)
write_geo('access-studies.geojson',route_items)
write_geo('access-gate.geojson',[(gate,dict(name='Candidate boundary access; regional junction unselected',status='study_only'))])

# Residential network is passenger/local-access/public transport, never the freight link.
local=[(LineString([(574650,6556500),(574650,6558900)]),dict(kind='residential_collector',name='Residential distributor / bus',phase='1-2')),
 (LineString([(573600,6557800),(575900,6557800)]),dict(kind='residential_collector',name='Cross-district local street',phase=2)),
 (LineString([(574650,6556500),(574200,6556350),(574000,6556250)]),dict(kind='centre_transition',name='Residential street to town-centre transition',phase=1)),
 (LineString([(574100,6556900),(574260,6556900),(574260,6557100),(574650,6557100)]),dict(kind='daily_walk',name='South daily-service walk',phase=1)),
 (LineString([(574250,6558200),(574650,6558200),(574650,6558150)]),dict(kind='daily_walk',name='North daily-service walk',phase=2))]
write_geo('residential-backbone.geojson',local)

old_structure=load(P/'geometry/structure.geojson')
gateway=unary_union([g for g,p in old_structure if p.get('system')=='port' or 'Eastern shared gateway' in p.get('name','')])
central=unary_union([g for g,p in old_structure if 'K1 Compute' in p.get('name','')])
north_point=next(g for g,p in load(P/'reviews/whole-site-v3/centres.geojson') if p['id']=='C')
agri=unary_union([g for g,p in old_structure if p.get('system')=='agri_production']).difference(fixed)
energy=unary_union([g for g,p in old_structure if p.get('system')=='energy_compute']).difference(fixed)
roles=[];remaining=scope
def allocate(g,role,name,status):
 global remaining
 q=g.intersection(remaining)
 if not q.is_empty:roles.append((q,dict(role=role,name=name,status=status)));remaining=remaining.difference(q)
allocate(fields,'fixed_agri','Fixed agrivoltaic fields','fixed_context');allocate(living,'fixed_living','Fixed living-quarter outline','fixed_context')
allocate(res,'residential','Primary continuous residential district','planning_envelope');allocate(core,'civic','Town centre','planning_envelope');allocate(prod,'production','Separate productive precinct','planning_envelope')
allocate(gateway,'gateway','Eastern trade and gateway industry','conditional');allocate(central,'production','Central compute option','conditional')
allocate(energy,'energy','Energy-led research / option area','conditional_not_installed')
allocate(agri,'agri','Crop research / production role','conditional_not_irrigated')
allocate(remaining,'stewardship','Unbuilt land / mountains / channel and terrain review','not_urbanised')
write_geo('whole-site-roles.geojson',roles)

qa={
 'version':'V8','source_commit':'307eca185e442c7cbb517dea848824a876b92415','date':'2026-10-27','status':'district_structure_review_not_final_submission',
 'whole_site_geodesic_km2':revision['revised_scope_geodesic_km2'],
 'terrain':terrain,'zone_gap_R_to_P_m':round(res.distance(prod)),
 'R_gross_km2':round(res.area/1e6,4),'C_gross_km2':round(core.area/1e6,4),'P_gross_km2':round(prod.area/1e6,4),
 'first_release_candidates':{p['id']:round(g.area/1e6,4) for g,p in releases},
 'first_release_seam_overlap_m2':{p['id']:round(g.intersection(added_seam).area,1) for g,p in releases},
 'whole_site_partition_gap_m2':round(scope.difference(unary_union([g for g,p in roles])).area,4),
 'whole_site_partition_overlap_m2':round(sum(g.area for g,p in roles)-unary_union([g for g,p in roles]).area,4),
 'district_overlap_m2':round(sum(g.area for g,p in districts)-unary_union([g for g,p in districts]).area,4),
 'freight_start_gap_to_boundary_gate_m':round(Point(freight.coords[0]).distance(gate),4),
 'passenger_start_gap_to_boundary_gate_m':round(Point(passenger.coords[0]).distance(gate),4),
 'freight_inside_residential_m':round(freight.intersection(res).length,4),
 'freight_inside_core_m':round(freight.intersection(core).length,4),
 'district_outside_scope_m2':round(unary_union([g for g,p in districts]).difference(scope).area,4),
 'fixed_pilot_overlap_m2':round(unary_union([g for g,p in districts]).intersection(fixed).area,4),
 'C03_source_channel_m':round(channel.intersection(park).length),
 'routes':[{**p} for g,p in route_items],
 'capacity_status':'V7 960 dwellings / 2400 residents and three-town population ledger withdrawn. New capacity not fixed at this structure stage.',
 'heat_credit_status':'No residential heat-network or reuse credit asserted.',
 'do_not_change':['Issued boundary and both fixed pilot outlines','Forage grass and jojoba under fixed arrays','No permanent construction on actual channels','English final deliverables'],
 'warnings':['300 m routes require detailed engineering, junction rights and channel crossings','R and P are gross planning extents, not fully buildable or constructed land','R/C local streets are a backbone only; blocks, plots, doors and service capacities remain to design','Existing living-quarter capacity, service provision and actual completion are unknown','Any added-seam land is hydrologically unclassified, not demonstrated safe',
 'P still includes non-flat terrain; next stage locates actual platforms within its footprint','A complete current-schema submission and new compliant A0 have not been generated'],
}
for key in ['freight_start_gap_to_boundary_gate_m','passenger_start_gap_to_boundary_gate_m','district_overlap_m2','freight_inside_residential_m','freight_inside_core_m','district_outside_scope_m2','fixed_pilot_overlap_m2']:
 assert qa[key]<.01,(key,qa[key])
assert qa['C03_source_channel_m']>0
(O/'qa.json').write_text(json.dumps(qa,indent=2)+'\n')
source_names=['submissions/jingyuanhuang-design/finite-water-city/tools/district_structure_v8.py','submissions/jingyuanhuang-design/finite-water-city/geometry/structure.geojson','submissions/jingyuanhuang-design/finite-water-city/reviews/whole-site-v3/corridors.geojson','submissions/jingyuanhuang-design/finite-water-city/reviews/whole-site-v3/centres.geojson','brief/site-package/boundaries/archive/2026-10-26/scope_9_13.geojson','AGENTS.md','skills/xcity-agent-submission/SKILL.md','brief/requirements.json','brief/design-depth.json','brief/site-package/boundaries/scope_9_13.geojson','brief/site-package/boundaries/boundary-revision.json','brief/site-package/water/channels_dem.geojson','brief/site-package/water/flood_sensitive_dem.geojson','brief/site-package/terrain/dem_9_13_utm19s_60m.png']
(O/'source-freeze.json').write_text(json.dumps({name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in source_names},indent=2)+'\n')

# English formal planning diagrams. There are deliberately no invented dwelling grids.
BG='#F8F6F0';INK='#253C44';MUT='#62736F'
COL={'residential':'#E4D5BC','civic':'#BE8169','production':'#9CADB7','energy':'#D7C78E','agri':'#BCC9A4','gateway':'#B79BA9','stewardship':'#ECE8DE','fixed_agri':'#B3A67F','fixed_living':'#B3A67F'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK})
pages=[]
def polys(g):
 if g.is_empty:return
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from polys(q)
def fill(ax,g,c,edge='none',lw=.6,hatch=None,alpha=1):
 for q in polys(g):
  q=orient(q,sign=1);vv=[];codes=[]
  for ring in [q.exterior,*q.interiors]:
   xy=np.asarray(ring.coords)/1000;vv.extend(xy);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(xy)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(vv,codes),facecolor=c,edgecolor=edge,lw=lw,hatch=hatch,alpha=alpha))
def line(ax,g,c=INK,lw=1,ls='-'):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  xy=np.asarray(g.coords)/1000;ax.plot(xy[:,0],xy[:,1],color=c,lw=lw,ls=ls)
 elif g.geom_type in ['Polygon','MultiPolygon']:line(ax,g.boundary,c,lw,ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(ax,q,c,lw,ls)
def lab(ax,g,s,size=10,dx=0,dy=0):
 p=g if g.geom_type=='Point' else g.centroid;ax.text(p.x/1000+dx,p.y/1000+dy,s,fontsize=size,ha='center',va='center',color=INK,bbox=dict(facecolor=BG,edgecolor='none',alpha=.9,pad=2))
def text(f,x,y,s,size=11,**kw):return f.text(x,y,s,fontsize=size,color=kw.pop('color',INK),**kw)
def panel(f,x,y,title,body,width=51):
 text(f,x,y,title,13,weight='bold');text(f,x,y-.038,'\n'.join(textwrap.wrap(body,width)),10.6,va='top',linespacing=1.5)
def page(n,title,sub):
 f=plt.figure(figsize=(16.54,11.69),facecolor=BG)
 text(f,.045,.954,'AGUA FINITA / V8 DISTRICT STRUCTURE',10,weight='bold',color='#8A634D');text(f,.045,.901,title,25,weight='bold');text(f,.045,.859,sub,10.6)
 text(f,.045,.028,f'{n:02} / Jingyuan Huang / 27 October 2026 / Source 307eca1 / Planning geometry; not an approved or final submission',8,color=MUT)
 return f
def frame(ax,bounds,scale):
 x0,y0,x1,y1=np.array(bounds)/1000;pad=(x1-x0)*.045;ax.set(xlim=(x0-pad,x1+pad),ylim=(y0-pad,y1+pad));ax.set_aspect('equal');ax.axis('off')
 x=x0+.025*(x1-x0);y=y0+.025*(y1-y0);ax.plot([x,x+scale/1000],[y,y],color=INK,lw=2);ax.text(x,y+.018*(y1-y0),f'{scale/1000:g} km',fontsize=9)
 ax.annotate('N',xy=(x1-.03*(x1-x0),y1-.01*(y1-y0)),xytext=(x1-.03*(x1-x0),y1-.11*(y1-y0)),arrowprops={'arrowstyle':'->','color':INK},ha='center',fontsize=10)
def base(ax,bounds,screen=False):
 win=box(*bounds);fill(ax,scope.intersection(win),'#EEEAE0');line(ax,scope.intersection(win),INK,1)
 if screen:fill(ax,flood.intersection(win),'none',edge='#BFC6BC',lw=.3,hatch='///')
 line(ax,channel.intersection(win),'#A1B2B2',.75)
 fill(ax,fields.intersection(win),COL['fixed_agri'],edge='#8A8165');fill(ax,living.intersection(win),COL['fixed_living'],edge='#8A8165')
def save(f,name):f.savefig(O/(name+'.png'),dpi=160,facecolor=BG);pages.append((f,name))

f=page(1,'One primary living district; production at regional scale','Whole-site structure / the existing fixed living quarter remains distinct / no new remote town population is assumed.')
a=f.add_axes([.035,.15,.59,.66])
for g,p in roles:fill(a,g,COL[p['role']])
line(a,scope,INK,1.1);line(a,channel.intersection(scope),'#A1B2B2',.55)
for g,p in load(P/'reviews/whole-site-v3/corridors.geojson'):
 if p.get('from_id') in ['A','K1','K2','D'] and p.get('to_id') not in ['B']:
  line(a,g.difference(res.buffer(300).union(core.buffer(300))),'#778E96',1,'--')
for g,p in districts:line(a,g,INK,1.1)
lab(a,res,'R / MAIN LIVING DISTRICT',8,2,1.5);lab(a,prod,'P / LOCAL PRODUCTION',8,4,-1.3)
lab(a,central,'K / COMPUTE OPTION',8,2,1);lab(a,north_point,'N / FARM SERVICE OPTION',8,2,1)
lab(a,gateway,'E / TRADE + INDUSTRY',8,3,-1)
lab(a,living,'FIXED LIVING QUARTER',8,3,-2);lab(a,fields,'FIXED FIELDS',8,0,-2)
lab(a,Point(608000,6559000),'PIE DE PALO',10)
frame(a,scope.bounds,10000)
panel(f,.66,.78,'A continuous residential district','R is the primary new residential planning envelope. It grows in connected precincts, with everyday services inside. Existing pilot housing is a separate fixed project; its capacity and completion are unknown.')
panel(f,.66,.58,'A hierarchy of production places','P handles initial compute, repair and maintenance outside residential land. K is a later central compute option. N is a conditional farm-service point, not an automatic new town. E holds gateway industry and trade.')
panel(f,.66,.36,'Connections carry different flows','Passenger arrival goes to the town-centre edge. Regional freight bypasses residential land. Remote production relies on verified service and transport arrangements rather than a repeated miniature city.')
panel(f,.66,.16,'Capacity is re-established','The V7 three-town population ledger is withdrawn. New capacities follow land, service, access and resource tests. All five systems retain a whole-site role; reserves are not installed capacity.')
f.legend(handles=[Patch(facecolor=COL[k],label=n) for k,n in [('residential','Residential'),('civic','Town centre'),('production','Production'),('energy','Energy option'),('agri','Agriculture role'),('gateway','Trade / gateway')]],loc='upper left',bbox_to_anchor=(.045,.117),ncol=6,fontsize=8,frameon=False)
save(f,'01-whole-site-hierarchy')

f=page(2,'Separate districts and measured corridor studies','South-west site / real boundaries and terrain screening / gross planning envelopes are distinct from first releases.')
bounds=(568000,6544000,586500,6561500);a=f.add_axes([.04,.145,.59,.67]);base(a,bounds,True)
for g,p in districts:fill(a,g,COL[{'residential_district':'residential','town_centre':'civic','productive_precinct':'production'}[p['role']]],edge=INK,lw=1)
for g,p in route_items:line(a,g,{'F':'#8A6257','A':'#355D72','S':'#698D8E','L':'#899280'}[p['id']],1.4,'--')
for g,p in releases:fill(a,g,'none',edge='#655248',lw=1,hatch='...')
lab(a,res,'R / residential district',10,1,0);lab(a,core,'C / town-centre transition',9,1,-.4);lab(a,prod,'P / productive precinct',10,1,-.2)
for g,p in nodes:lab(a,g,p['node_id'],9,-.3,.3)
lab(a,fields,'FIXED AGRIVOLTAIC FIELDS',8,-1,0);lab(a,living,'FIXED LIVING QUARTER',8,0,-1)
frame(a,bounds,2000)
panel(f,.67,.78,'R and P are different districts',f"R planning envelope: {res.area/1e6:.2f} km2. P: {prod.area/1e6:.2f} km2. Nearest R-to-P boundary gap: {res.distance(prod)/1000:.2f} km. This is a design separation, not a claimed legal or acoustic setback.")
panel(f,.67,.57,'C / a compact mixed-use transition',f"The {core.area/1e6:.2f} km2 gross centre envelope meets R at its southern edge. Initial C0 is only {c0.area/1e4:.0f} ha. Passenger arrival, public activity and later mixed-use blocks concentrate here; the entire envelope is not paved or built at once.")
panel(f,.67,.34,'The fixed quarter is not next door',f"The candidate fixed-quarter connection is {fixed_link.length/1000:.1f} km. It is a route study, not an acquired or operating road. The new district cannot claim to provide walkable services to that separate quarter.")
panel(f,.67,.15,'Protection and uncertainty','Hatching is DEM flood sensitivity, not a lake. Channel crossings need engineering. Both fixed pilot parts remain unchanged; array crops remain forage grass and jojoba.')
save(f,'02-district-relationships')

f=page(3,'Residential continuity comes before the housing count','R contains homes, daily services, local streets and neighbourhood public space. Compute, yards and heavy freight remain outside R.')
bounds=(573200,6555100,576250,6559400);a=f.add_axes([.04,.135,.59,.69]);base(a,bounds)
fill(a,res,COL['residential'],edge=INK,lw=1.2);fill(a,core,COL['civic'],edge=INK,lw=1)
line(a,LineString([(573500,6557800),(575900,6557800)]),'#94866F',1,'--')
fill(a,r0,'none',edge='#9D7351',lw=1.2,hatch='...');fill(a,c0,'#A45D49',edge=INK,lw=.7)
for g,p in local:line(a,g,'#608C89' if p['kind']=='daily_walk' else '#6E858E',1.8 if p['kind']=='daily_walk' else 2.1)
for g,p in services:
 if g.geom_type=='Point':a.scatter(g.x/1000,g.y/1000,s=45,color='#8A6651',zorder=5)
 else:fill(a,g,'#A7BCC8',edge=INK,lw=.7)
lab(a,res_n,'R-N / connected next precinct',10,0,.25);lab(a,res_s,'R-S / residential precinct',10,.55,-.15)
lab(a,r0,'R0 / first-release candidate',9,-.1,-.35);lab(a,c0,'C0 / initial core',9,-.15,-.15)
lab(a,services[0][0],'South school reserve',8,-.4,.2);lab(a,services[1][0],'North school reserve',8,-.5,.2)
lab(a,core,'C / town-centre reserve',9,0,-.35);lab(a,commons,'A03',9,.1,.12)
frame(a,bounds,500)
panel(f,.67,.78,'One fabric, developed in increments','R-S and R-N are connected precincts of one residential district. Their dividing collector is a local street, not an industrial or institutional strip. Complete blocks and housing types will be fitted to this structure next.')
panel(f,.67,.57,'Daily service stays with residents','Schools and shared sport, daily shops, local care and neighbourhood public space belong inside R. The two school reservations correspond to different release stages; their places are not assumed from a rectangle on the map.')
panel(f,.67,.35,'Town-centre and daily-service roles','C provides town-level public activity, arrival, mixed use and higher-order services. It does not replace the residential daily network. Large institutions are not added without a service catchment and delivery case.')
panel(f,.67,.15,'Capacity follows the land and services','R0 is a 156 ha release-search area. Define net housing land, service capacity and a reliable water budget, then determine first occupancy. The first release need not fill the entire search area.')
save(f,'03-continuous-residential-district')

f=page(4,'Keep heavy freight out of the living district','All route lengths are measured candidate alignments. The corridor search uses 300 m terrain cells and requires detailed survey and engineering.')
bounds=(568800,6551000,577000,6560000);a=f.add_axes([.04,.14,.59,.68]);base(a,bounds,True)
for g,p in districts:fill(a,g,COL[{'residential_district':'residential','town_centre':'civic','productive_precinct':'production'}[p['role']]],edge=INK,lw=.9)
for g,p in route_items[:3]:line(a,g,{'F':'#8A6257','A':'#355D72','S':'#698D8E'}[p['id']],2,'--')
for g,p in local:line(a,g,'#647F85',1.2)
lab(a,res,'RESIDENTIAL / LOCAL ACCESS',9,0,.1);lab(a,core,'ARRIVAL + TOWN CENTRE',9,.1,-.15);lab(a,prod,'PRODUCTION / CONTROLLED GATES',9,0,-.25)
lab(a,gate_inner,'WEST BOUNDARY ACCESS',9,1.1,.3)
frame(a,bounds,1000)
panel(f,.67,.79,'F / freight to production',f"{freight.length/1000:.2f} km corridor candidate. Geometry intersects R for {qa['freight_inside_residential_m']:.0f} m and C for {qa['freight_inside_core_m']:.0f} m. This tests district separation; it does not prove junction design, road capacity or noise performance.")
panel(f,.67,.58,'A / people arrive at the centre',f"{passenger.length/1000:.2f} km candidate approach to the town-centre edge. Local streets and public transport continue into R. Long-distance goods do not use the residential collector as a shortcut.")
panel(f,.67,.37,'S / workers connect between places',f"{shuttle.length/1000:.2f} km shuttle alignment between C and P. Some approach segments may share road infrastructure under managed operations. A road connection does not make P a walkable neighbourhood facility.")
panel(f,.67,.16,'Engineering and access work','Mapped channel and sensitivity crossings remain explicit engineering work. Regional RN40 access rights and its final junction are unselected. No road is described as existing merely because it is drawn.')
save(f,'04-movement-and-interfaces')

f=page(5,'Function and phase have different scales','A complete first phase is a connected operating system. Each residential neighbourhood is not required to reproduce every urban function.')
tableax=f.add_axes([.045,.56,.91,.23]);tableax.axis('off')
rows=[['R / residential','Homes; daily shops; schools; care; local public space','Local streets and walking; no compute campus'],['C / town centre','Arrival; public activity; mixed use; staged higher services','Connects to R; does not replace local provision'],['P / production','Compute; cooling; repair; service yards; plant','Own gates, freight access and operating controls'],['Regional systems','Power; agriculture; gateway; major resource corridors','Distributed; conditional; separate rights and accounts']]
tb=tableax.table(cellText=rows,colLabels=['Scale / role','Belongs here','Interface rule'],cellLoc='left',colWidths=[.16,.49,.35],bbox=[0,0,1,1]);tb.auto_set_font_size(False);tb.set_fontsize(9.1)
for (r,c),cell in tb.get_celld().items():cell.set_facecolor('#E1D5BF' if r==0 else BG);cell.set_edgecolor('#D3CEC2');cell.PAD=.08
phase_text=[('PHASE 1 / establish the system','R0 + C0 + P0, with their enabling works. First housing opens only with local education/care, water, waste, power, access and operating funding. Verify fixed-quarter stock and demand before releasing competing housing.'),('PHASE 2 / complete connected districts','Extend the same residential fabric and its service capacity before another housing centre. Expand C and P independently as demand and resources permit. C03 visitor paths may open after hydraulic and access work; channel protection starts immediately.'),('PHASE 3 / test regional options','K and the eastern gateway require separate power, water, access and demand decisions. A remote service point does not become a town by default. No population is assigned to a coloured production reservation.')]
for i,(title,body) in enumerate(phase_text):panel(f,.045+i*.315,.47,title,body,43)
text(f,.045,.17,'SOURCE-BASED CORRECTION',11,weight='bold',color='#8A634D')
text(f,.045,.13,f"V7 east alternative: 95th-percentile source-cell slope {terrain['V7_east_alternative']['slope_p95_pct']:.2f}%. Current P envelope: {terrain['P']['slope_p95_pct']:.2f}%.\nThe new selection still requires platform studies. A low slope at one centre cell was not sufficient evidence for the former site.",10.5,linespacing=1.5)
text(f,.045,.063,'NEXT DESIGN TEST / terrain-fit blocks, net land and service capacity, occupancy tranches and a matching resource budget. No new final rendering or compliant A0 is claimed.',9,color=MUT)
save(f,'05-service-hierarchy-and-phasing')

with PdfPages(O/'agua-finita-v8-district-structure.pdf') as pdf:
 for f,name in pages:pdf.savefig(f,facecolor=BG);plt.close(f)
for name in ['agua-finita-v8-district-structure.pdf','01-whole-site-hierarchy.png','02-district-relationships.png','03-continuous-residential-district.png','04-movement-and-interfaces.png','qa.json']:
 shutil.copy2(O/name,OUT/name)
print(json.dumps(qa,indent=2));print('OUTPUT',OUT)
