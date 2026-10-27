"""Original all-phase city study. Geometry, accounts and drawings share one source.
No edits to organiser data, no invented installed planting, and no legacy render reuse.
"""
import json, math, hashlib, textwrap, shutil, heapq, warnings
from pathlib import Path
warnings.filterwarnings('ignore',category=DeprecationWarning)
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import PathPatch,Patch,Rectangle,FancyArrowPatch
from matplotlib.path import Path as MP
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import shape,mapping,box,Point,LineString
from shapely.geometry.polygon import orient
from shapely.ops import transform,unary_union,nearest_points,triangulate
from shapely import contains_xy
from pyproj import Transformer

P=Path(__file__).resolve().parents[1];R=P.parents[2];S=R/'brief/site-package'
V8=P/'reviews/district-structure-v8';O=P/'reviews/complete-city-v9';G=O/'geometry'
OUT=R.parents[1]/'outputs/agua-finita-v9'
for d in [O,G,OUT]:d.mkdir(parents=True,exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:[(transform(T,shape(x['geometry'])),x['properties']) for x in json.loads(f.read_text())['features']]
U=lambda f:unary_union([g for g,p in load(f)])
scope=U(S/'boundaries/scope_9_13.geojson');fields=U(S/'pilot-area/pilot_area.geojson');living=U(S/'pilot-area/pilot_living_area.geojson');fixed=fields.union(living)
channels=U(S/'water/channels_dem.geojson');flood=U(S/'water/flood_sensitive_dem.geojson')
channel_screen=channels.buffer(150)
dem=np.asarray(Image.open(S/'terrain/dem_9_13_utm19s_60m.png'),dtype=float);dy,dx=np.gradient(dem,60);slope=np.hypot(dx,dy)*100
xs=559572.4+(np.arange(dem.shape[1])+.5)*60;ys=6608973.7-(np.arange(dem.shape[0])+.5)*60
district0={p['id']:g for g,p in load(V8/'districts.geojson')};res,core,prod=[district0[k] for k in ['R','C','P']]
solar=box(573300,6553300,574700,6554700).difference(flood.buffer(50)).intersection(scope).difference(fixed)
utility=box(574250,6552750,574600,6553100)
trial=box(573000,6554800,573600,6555200).difference(flood.buffer(100)).intersection(scope).difference(fixed)
roles0=load(V8/'whole-site-roles.geojson');gateway=unary_union([g for g,p in roles0 if p['role']=='gateway'])
centre_n=next(g for g,p in load(P/'reviews/whole-site-v3/centres.geojson') if p['id']=='C')
north=box(centre_n.x-210,centre_n.y-160,centre_n.x+210,centre_n.y+160).intersection(scope).difference(fixed)
regional=load(P/'reviews/whole-site-v3/corridors.geojson');access=load(V8/'access-studies.geojson')

def ft(g,**p):return dict(type='Feature',geometry=mapping(transform(I,g)),properties=p)
def writegeo(name,items):
 (G/name).write_text(json.dumps(dict(type='FeatureCollection',features=[ft(g,**p) for g,p in items]),separators=(',',':'))+'\n')
def stats(g):
 x0,y0,x1,y1=g.bounds;r=(ys>=y0)&(ys<=y1);c=(xs>=x0)&(xs<=x1);X,Y=np.meshgrid(xs[c],ys[r]);v=slope[np.ix_(r,c)][contains_xy(g,X,Y)]
 return (float(np.median(v)),float(np.percentile(v,95))) if len(v) else (0,0)

build=[];units=[];streets=[];paths=[];assets=[];services=[];notes=[]
def building(g,bid,use,phase,floors=1,dwellings=0,jobs=0,**extra):
 assert scope.buffer(.01).covers(g),(bid,'outside')
 assert not g.intersects(fixed),(bid,'fixed pilot')
 assert not g.intersects(channel_screen),(bid,'channel screen')
 build.append((g,dict(id=bid,use=use,phase=phase,floors=floors,height_m=round(floors*3.5,1),dwellings=dwellings,jobs=jobs,**extra)))
def unit(g,uid,district,use,phase,**extra):
 units.append((g,dict(id=uid,district=district,use=use,phase=phase,**extra)))

# Full city street and block structure, not just the first release.
xg=list(np.arange(573500,576001,240));yg=list(np.arange(6556500,6559001,220))
if xg[-1]<576000:xg.append(576000)
if yg[-1]<6559000:yg.append(6559000)
for x in xg:
 ln=LineString([(x,6556500),(x,6559000)]).intersection(res)
 streets.append((ln,dict(id=f'R-NS-{x}',district='R',phase=1 if x<=574700 else 2,network='shared',hierarchy='secondary' if x==574700 else 'local',width_m=30 if x==574700 else 20)))
for y in yg:
 ln=LineString([(573500,y),(576000,y)]).intersection(res)
 streets.append((ln,dict(id=f'R-EW-{y}',district='R',phase=1 if y<=6557820 else 3,network='shared',hierarchy='secondary' if y==6557820 else 'local',width_m=24 if y==6557820 else 20)))
road_r=unary_union([g.buffer(p['width_m']/2,cap_style=2) for g,p in streets]).intersection(res)
cells=[]
for j in range(len(yg)-1):
 for i in range(len(xg)-1):
  g=box(xg[i]+16,yg[j]+16,xg[i+1]-16,yg[j+1]-16).intersection(res)
  if g.is_empty:continue
  phase=1 if j<6 and i<5 else (2 if j<6 else 3)
  cells.append(dict(g=g,i=i,j=j,phase=phase,id=f'R-{j:02}-{i:02}'))
def choose(point,exclude=set(),phase=None):
 candidates=[c for c in cells if c['id'] not in exclude and c['g'].area>32000 and (phase is None or c['phase']==phase)]
 return min(candidates,key=lambda c:c['g'].centroid.distance(point))
reserved={}
school_specs=[]
for pt,ph in [(Point(574100,6557100),1),(Point(575300,6557100),2),(Point(574100,6558400),3),(Point(575300,6558400),3)]:
 c=choose(pt,set(reserved),ph);reserved[c['id']]='school';school_specs.append(c)
for pt in [Point(574650,6557550),Point(574100,6557900),Point(575300,6558250)]:
 c=choose(pt,set(reserved));reserved[c['id']]='dry_park'
for ph,pt in [(1,Point(574100,6556850)),(2,Point(575200,6557350)),(3,Point(574650,6558500))]:
 c=choose(pt,set(reserved),ph);reserved[c['id']]='daily_centre'

res_capacity={1:0,2:0,3:0};res_blocks=[]
for c in cells:
 g=c['g'];bid=c['id'];ph=c['phase'];cx,cy=g.centroid.coords[0]
 full=g.area>35000 and res.covers(box(cx-100,cy-90,cx+100,cy+90))
 med,p95=stats(g)
 if bid in reserved:
  use=reserved[bid];unit(g,bid,'R',use,ph);services.append((g,dict(id=bid,use=use,phase=ph)))
  continue
 if not full or p95>8 or med>3.5:
  unit(g,bid,'R','terrain_review',ph,reason='Edge or terrain-fit reserve; no dwelling capacity assigned');continue
 typ='apartments_and_terraces' if (c['i']+c['j'])%3 else 'terraces'
 start=len(build)
 if typ=='apartments_and_terraces':
  for k,(ox,oy) in enumerate([(-90,-82),(10,-82),(-90,70),(10,70)]):
   building(box(cx+ox,cy+oy,cx+ox+80,cy+oy+12),f'{bid}-A{k}','residential',ph,3,24,block=bid,roof_pv=False)
  for k,(ox,oy) in enumerate([(-60,-28),(12,-28),(-60,18),(12,18)]):
   building(box(cx+ox,cy+oy,cx+ox+48,cy+oy+10),f'{bid}-T{k}','residential',ph,2,8,block=bid)
 else:
  for k,(ox,oy) in enumerate([(x,y) for x in [-75,27] for y in [-65,-25,15,55]]):
   building(box(cx+ox,cy+oy,cx+ox+48,cy+oy+10),f'{bid}-T{k}','residential',ph,2,8,block=bid)
 dwell=sum(p['dwellings'] for h,p in build[start:]);res_capacity[ph]+=dwell
 unit(g,bid,'R','residential',ph,housing_type=typ,dwellings=dwell);res_blocks.append(c)
 # Public shared-court access reaches the street through the central gap, not through a building.
 paths.append((LineString([(cx,yg[c['j']]),(cx,cy),(cx,yg[c['j']+1])]),dict(id=bid+'-walk',network='people',phase=ph,shaded=True)))

# Daily-service centres contain local care, a small market and community work rooms.
for g,p in services:
 if p['use']=='daily_centre':
  cx,cy=g.centroid.coords[0]
  for k,(ox,oy) in enumerate([(-70,-60),(10,-60),(-70,30),(10,30)]):
   building(box(cx+ox,cy+oy,cx+ox+60,cy+oy+18),p['id']+f'-D{k}','civic',p['phase'],2,0,36,service='daily_shops_care_workrooms')

# Town centre: a real mixed-use block/street structure and staged activity core.
cxg=[573700,573950,574200,574450,574700];cyg=[6555900,6556100,6556300,6556500]
for x in cxg:streets.append((LineString([(x,cyg[0]),(x,cyg[-1])]),dict(id=f'C-NS-{x}',district='C',phase=1,network='shared',hierarchy='primary' if x==574200 else 'local',width_m=28 if x==574200 else 20)))
for y in cyg:streets.append((LineString([(cxg[0],y),(cxg[-1],y)]),dict(id=f'C-EW-{y}',district='C',phase=1,network='shared',hierarchy='secondary',width_m=22)))
streets.append((LineString([(574200,6556500),(574700,6556500)]),dict(id='C-R-transition',district='C',phase=1,network='shared',hierarchy='primary',width_m=28)))
c_dw={1:0,2:0,3:0}
commons=None
for j in range(3):
 for i in range(4):
  g=box(cxg[i]+16,cyg[j]+16,cxg[i+1]-16,cyg[j+1]-16);bid=f'C-{j}-{i}';cx,cy=g.centroid.coords[0]
  use='mixed_use';ph=1 if (i,j) in [(1,1),(2,1),(1,0)] else (2 if j<2 else 3)
  if (i,j)==(1,1):
   use='public_commons';commons=box(cx-40,cy-40,cx+40,cy+40)
   for k,(ox,oy,w,h) in enumerate([(-90,-65,180,18),(-90,48,180,18)]):
    building(box(cx+ox,cy+oy,cx+ox+w,cy+oy+h),f'{bid}-market{k}','civic',ph,1,0,81,service='market_library_climate_refuge')
  elif (i,j)==(2,1):
   use='civic';building(box(cx-80,cy-45,cx+80,cy+45),bid+'-health','civic',ph,2,0,180,service='primary_health_and_training_no_hospital_claim')
  elif (i,j)==(1,0):
   use='arrival';building(box(cx-90,cy-35,cx+90,cy+35),bid+'-arrival','civic',ph,1,0,90,service='arrival_market_and_audit')
  elif (i,j)==(0,2):
   use='culture';building(box(cx-80,cy-40,cx+80,cy+40),bid+'-culture','civic',ph,2,0,128,service='culture_learning')
  else:
   for k,(ox,oy) in enumerate([(-95,-70),(10,-70),(-95,35),(10,35)]):
    building(box(cx+ox,cy+oy,cx+ox+80,cy+oy+15),f'{bid}-M{k}','mixed_use',ph,4,20,70,residential_gfa_m2=2400,retail_gfa_m2=1200,office_gfa_m2=1200)
    c_dw[ph]+=20
  unit(g,bid,'C',use,ph)

# School capacity is computed after the housing yield; it is not invented from a school icon.
school_capacity=[];acc_seats=0
for phase in [1,2,3]:
 people=sum((res_capacity[k]+c_dw[k])*2.5 for k in range(1,phase+1))
 need=math.ceil(people*.15/30)*30;these=[c for c in school_specs if c['phase']==phase]
 allocate=max(360,math.ceil(max(0,need-acc_seats)/max(1,len(these))/360)*360)
 for c in these:
  wings=min(4,math.ceil(allocate/360));cx,cy=c['g'].centroid.coords[0]
  for w in range(wings):
   building(box(cx-80,cy-72+w*38,cx-20,cy-54+w*38),c['id']+f'-S{w}','civic',phase,2,0,26,service='education',places=360)
  seats=wings*360;acc_seats+=seats;school_capacity.append(dict(id=c['id'],phase=phase,places=seats,cumulative=acc_seats,required_at_phase=need))
 assert acc_seats>=need,(phase,acc_seats,need)

# Production is organised around its own service spine and controlled gates.
for k,(x,y) in enumerate([(x,y) for y in [6552250,6552400] for x in [573300,573550,573800,574050]]):
 phase=1 if k<2 else (2 if k<4 else 3)
 building(box(x,y,x+96,y+48),f'P-IT-{k}','compute',phase,1,0,16,it_mw=1)
for k,x in enumerate([573250,573500,573750,574000]):
 ph=1 if k==0 else (2 if k==1 else 3)
 building(box(x,6552720,x+140,6552770),f'P-W-{k}','industry',ph,1,0,70,service='repair_and_fabrication')
streets.append((LineString([(573180,6552550),(574600,6552550)]),dict(id='P-spine',district='P',phase=1,network='machine',hierarchy='production',width_m=16)))
for x in [573230,573480,573730,573980,574250]:
 streets.append((LineString([(x,6552100),(x,6552950)]),dict(id=f'P-yard-{x}',district='P',phase=1,network='machine',hierarchy='production',width_m=12)))
unit(box(573200,6552050,574600,6552530),'P-COMPUTE','P','compute',1)
unit(box(573200,6552650,574200,6553050),'P-REPAIR','P','industry',1)
unit(utility,'P-UTILITY','P','infrastructure',1)
building(box(574300,6552820,574390,6552850),'U-treatment','infrastructure',1,1,0,27,service='enclosed_water_reuse_treatment')
for k,(x,y) in enumerate([(574420,6552820),(574420,6552940)]):
 assets.append((box(x,y,x+55,y+55),dict(id=f'U-tank-{k}',type='covered_storage',phase=1,capacity_m3=5000)))

# Solar is explicitly designed as phased module fields; energy polygons do not invent PV.
solar_parts=[]
for phase,y0 in [(1,6553300),(2,6553760),(3,6554220)]:
 parcel=box(573350,y0,574650,y0+390).intersection(solar)
 unit(parcel,f'S-{phase}','S','energy',phase);solar_parts.append((parcel,phase))
 assets.append((parcel,dict(id=f'S-PV-{phase}',type='pv_field',phase=phase,mwp=16,capacity_basis='Declared 16 MWp per explicit field; equipment and interconnection unverified')))
 for yy in np.arange(y0+12,y0+375,18):
  g=LineString([(573375,yy),(574620,yy)]).intersection(parcel)
  if not g.is_empty:assets.append((g,dict(id=f'S-row-{phase}-{yy}',type='pv_row',phase=phase)))

# Northern farm-service hub: service facility, no automatic new town population.
ncx,ncy=north.centroid.coords[0]
for k,xx in enumerate([-110,10]):building(box(ncx+xx,ncy-70,ncx+xx+90,ncy-40),f'N-work{k}','industry',2,1,0,27,service='farm_solar_robot_service')
building(box(ncx-80,ncy+20,ncx+80,ncy+42),'N-office','civic',2,2,0,88,service='cooperative_training_and_day_services')
assets.append((north,dict(id='N-PV',type='roof_pv_scenario',phase=2,mwp=1)))

# Eastern gateway has a coherent workplace and roster accommodation, not an invented town.
eparts=sorted(list(gateway.geoms) if gateway.geom_type=='MultiPolygon' else [gateway],key=lambda g:g.area,reverse=True)
eg=eparts[0];x0,y0,x1,y1=eg.bounds;e_sites=[]
for yy in np.arange(y0+100,y1-80,180):
 for xx in np.arange(x0+80,x1-140,200):
  g=box(xx,yy,xx+120,yy+60)
  if eg.buffer(-20).covers(g) and not g.intersects(channel_screen):e_sites.append(g)
assert len(e_sites)>=10,('gateway platforms',len(e_sites))
for k,g in enumerate(e_sites[:10]):
 if k<6:building(g,f'E-log{k}','logistics',3,1,0,30,service='gateway_warehouse_and_workshop')
 elif k<8:building(g,f'E-office{k}','civic',3,2,0,60,service='trade_control_and_worker_services')
 else:building(g,f'E-lodge{k}','civic',3,2,0,20,service='roster_accommodation_not_households',worker_beds=160)
eroad=unary_union([LineString([(g.bounds[0]-25,g.bounds[1]-30),(g.bounds[2]+25,g.bounds[1]-30)]) for g in e_sites[:10]]+[LineString([(g.bounds[0]-25,g.bounds[1]-30),(g.bounds[0]-25,g.bounds[3]+150)]) for g in e_sites[:10]]) .intersection(eg)
streets.append((eroad,dict(id='E-service',district='E',phase=3,network='machine',hierarchy='production',width_m=16)))
assets.append((eg,dict(id='E-PV',type='roof_pv_scenario',phase=3,mwp=4)))
unit(trial,'A-TRIAL','A','agriculture',2,water_basis='Actual trial area x assumed 4000 m3/ha/year; not a pilot crop allocation')

# Net land accounts: every city district is partitioned without overlap.
envelopes={'R':res,'C':core,'P':prod,'S':solar,'A':trial,'N':north,'E':gateway}
final_units=[]
for district,envelope in envelopes.items():
 rem=envelope
 # Street right of way is a real accounting category, distinct from centreline length.
 roads=unary_union([g.buffer(p['width_m']/2,cap_style=2) for g,p in streets if p.get('district')==district]).intersection(rem)
 if not roads.is_empty:
  final_units.append((roads,dict(id=district+'-ROW',district=district,use='streets',phase=1 if district in ['R','C','P'] else (2 if district=='N' else 3))));rem=rem.difference(roads)
 for g,p in units:
  if p['district']!=district:continue
  q=g.intersection(rem)
  if not q.is_empty:final_units.append((q,p));rem=rem.difference(q)
 if district in ['N','E']:
  # Building plots plus service yards are functional units at their own scale.
  for g,p in build:
   if p['id'].startswith(district+'-'):
    q=g.buffer(25,join_style=2).intersection(rem)
    if not q.is_empty:final_units.append((q,dict(id=p['id']+'-plot',district=district,use=p['use'],phase=p['phase'])));rem=rem.difference(q)
 if not rem.is_empty:final_units.append((rem,dict(id=district+'-GROUND',district=district,use='dry_open_space' if district in ['R','C'] else 'operational_reserve',phase=1 if district in ['R','C','P'] else 3,capacity=0)))
units=final_units

# Same actual district and phase IDs connect geometry and programme.
districts=[(g,dict(id=k,name={'R':'Residential district','C':'Town centre','P':'Productive precinct','S':'Solar and storage','A':'Trial field','N':'Farm-service hub','E':'Eastern gateway'}[k])) for k,g in envelopes.items()]
phase_geoms=[]
programme=[];cum_by_d={};cumul_pop=0
def belongs(bid):
 if bid.startswith('R-'):return 'R'
 if bid.startswith('C-'):return 'C'
 if bid.startswith(('P-','U-')):return 'P'
 return bid[0]
for ph in [1,2,3]:
 zones=[]
 for district,envelope in envelopes.items():
  bs=[(g,p) for g,p in build if p['phase']==ph and belongs(p['id'])==district]
  us=[g for g,p in units if p['district']==district and p['phase']==ph and p['use'] not in ['streets','dry_open_space','operational_reserve']]
  if not bs and not us and not any(p['phase']==ph and p.get('type')=='pv_field' for g,p in assets if district=='S'):continue
  area=unary_union(us+[g.buffer(10) for g,p in bs]).intersection(envelope)
  if area.is_empty:area=envelope
  new_dw=sum(p['dwellings'] for g,p in bs);new_jobs=sum(p['jobs'] for g,p in bs);new_pop=new_dw*2.5
  old=cum_by_d.get(district,(0,0,0));now=(old[0]+new_pop,old[1]+new_dw,old[2]+new_jobs);cum_by_d[district]=now
  phase_geoms.append((area,dict(zone_id=district,phase=ph,name=district+f' Phase {ph}',trigger='Verified water, access, operations and service capacity before occupancy or expansion')))
  zones.append(dict(zone_id=district,name={'R':'Residential precincts','C':'Civic and mixed-use centre','P':'Independent productive campus','S':'Solar utility fields','A':'Irrigation trial','N':'Northern service hub','E':'Eastern gateway'}[district],works=[p['id'] for g,p in bs]+[p['id'] for g,p in assets if p.get('type')=='pv_field' and p['phase']==ph and district=='S'],services=[p.get('service',p['use']) for g,p in bs if p['use'] not in ['residential','mixed_use','compute','industry','logistics']],delivery_sequence='Access and verified utility supply first; occupied building release follows funded service opening',dependencies='Combined source-water balance, transport rights, operating funds and demonstrated use demand',new_residents=new_pop,cumulative_residents=now[0],new_dwellings=new_dw,cumulative_dwellings=now[1],new_jobs=new_jobs,cumulative_jobs=now[2],basis='Buildings and declared dwelling/employment coefficients; residents at 2.5/dwelling. Employment is uncontracted design capacity, not existing jobs. Roster beds are not residents.'))
 total_pop=sum(v[0] for v in cum_by_d.values());total_dw=sum(v[1] for v in cum_by_d.values());total_jobs=sum(v[2] for v in cum_by_d.values())
 programme.append(dict(phase=ph,period={1:'Scenario years 0-5 after enabling conditions',2:'Scenario years 5-10, conditional',3:'Scenario years 10-20, conditional'}[ph],zones=zones,new_residents=sum(z['new_residents'] for z in zones),total_residents=total_pop,new_dwellings=sum(z['new_dwellings'] for z in zones),total_dwellings=total_dw,new_jobs=sum(z['new_jobs'] for z in zones),total_jobs=total_jobs,trigger={1:'Secured combined fixed/new water balance, regional access, funded local services and household livelihood case',2:'Audited source headroom, demand for occupied blocks and funded school/health/utility expansion',3:'Independent gateway rights, transport, utilities, roster welfare and actual trade demand; complete northern residential services'}[ph]))

# An actual street-network distance test, block gate to school gate (not every dwelling door).
graph={};coords={}
def node(x,y):
 k=(round(x,2),round(y,2));graph.setdefault(k,{});coords[k]=k;return k
def edge(a,b):
 d=math.dist(a,b);graph[a][b]=d;graph[b][a]=d
for j,y in enumerate(yg):
 xx=sorted(set(xg+[(xg[i]+xg[i+1])/2 for i in range(len(xg)-1)]))
 for xa,xb in zip(xx,xx[1:]):
  seg=LineString([(xa,y),(xb,y)])
  if res.buffer(.01).covers(seg):edge(node(xa,y),node(xb,y))
for x in xg:
 for ya,yb in zip(yg,yg[1:]):
  if res.buffer(.01).covers(LineString([(x,ya),(x,yb)])):edge(node(x,ya),node(x,yb))
def gate(c):return node((xg[c['i']]+xg[c['i']+1])/2,yg[c['j']])
def multisource(starts,active):
 d={s:0 for s in starts};heap=[(0,s) for s in starts];heapq.heapify(heap)
 while heap:
  dist,u=heapq.heappop(heap)
  if dist>d[u]:continue
  for v,w in graph[u].items():
   if not active.covers(LineString([u,v])):continue
   nd=dist+w
   if nd<d.get(v,math.inf):d[v]=nd;heapq.heappush(heap,(nd,v))
 return d
walk_results={};walk_per_block={}
for ph in [1,2,3]:
 active=unary_union([box(xg[c['i']],yg[c['j']],xg[c['i']+1],yg[c['j']+1]) for c in cells if c['phase']<=ph]).intersection(res).buffer(.1)
 d=multisource([gate(c) for c in school_specs if c['phase']<=ph],active);vals=[]
 for c in res_blocks:
  if c['phase']<=ph:
   v=d.get(gate(c),math.inf);vals.append(v)
   if ph==3:walk_per_block[c['id']]=v
 assert all(math.isfinite(v) for v in vals),'Disconnected residential street graph'
 walk_results[ph]=dict(max_block_gate_m=round(max(vals)),median_block_gate_m=round(float(np.median(vals))),over_1000m=sum(v>1000 for v in vals),blocks=len(vals))

# First-phase dispatch is synthetic, not climate data or carbon certification.
p1=programme[0];rng=np.random.default_rng(901);hour=np.arange(8760);hod=hour%24;day=hour//24
raw=np.maximum(0,np.sin((hod-6)*math.pi/12))*(.82+.18*np.sin(2*math.pi*(day-75)/365))
raw*=rng.uniform(.70,1.0,365)[day];pv=raw/raw.mean()*.25*16
firm=p1['total_residents']*.00012+.6;it_peak=2.;soc=8.;batt=40.;eta=math.sqrt(.9);imports=[];itserved=[]
for production in pv:
 excess=production-firm;grid=0
 if excess<0:
  use=min(max(0,soc-8),-excess/eta);soc-=use;grid=max(0,-excess-use*eta);excess=0
 desired=it_peak*1.25
 renewable=min(excess,desired);excess-=renewable
 if renewable<desired and soc>12:
  use=min(soc-12,(desired-renewable)/eta);soc-=use;renewable+=use*eta
 itserved.append(renewable/1.25)
 soc+=min(batt-soc,excess*eta);imports.append(grid)
dispatch=dict(method='Synthetic hourly solar, 25% mean CF; firm services first; IT uses remaining PV/battery; imports support firm load only',pv_mwp=16,battery_mwh=40,it_peak_mw=2,firm_mw=round(firm,3),fully_matched_hours_pct=round(float(np.mean(np.asarray(imports)<1e-8)*100),2),unmatched_import_mwh=round(sum(imports)),it_served_mwh=round(sum(itserved)),it_utilisation_pct=round(sum(itserved)/8760/2*100,1))
np.savetxt(O/'phase1-synthetic-dispatch.csv',np.c_[hour,pv,np.full(8760,firm),itserved,imports],delimiter=',',header='hour,pv_mw,firm_mw,it_mw,unmatched_grid_mw',comments='',fmt='%.4f')
resource=[]
for q in programme:
 ph=q['phase'];pop=q['total_residents'];jobs=q['total_jobs'];itmw=sum(p.get('it_mw',0) for g,p in build if p['phase']<=ph)
 itenergy=dispatch['it_served_mwh'] if ph==1 else itmw*8760*.60
 water=dict(domestic=pop*.12*365,public_services=pop*.025*365,industry=jobs*.025*300,trial_irrigation=trial.area/1e4*4000 if ph>=2 else 0,pv_cleaning=ph*4000,cooling=itenergy*1000*.02/1000)
 gross=sum(water.values());recoverable=(water['domestic']+water['public_services'])*.65;reuse=min(recoverable,water['trial_irrigation']+pop*2)
 source=(gross-reuse)/.9
 resource.append(dict(phase=ph,water_gross_m3_y=round(gross),reclaimed_substitution_m3_y=round(reuse),fresh_requirement_m3_y=round(source),water_components=water,it_peak_mw=itmw,pv_mwp=16*ph+(1 if ph>=2 else 0)+(4 if ph==3 else 0),school_places=sum(s['places'] for s in school_capacity if s['phase']<=ph),school_need_assumed=math.ceil(pop*.15),fixed_pilot_and_quarter='Demand unknown and additional; source rights not supplied'))

# Geometry, all-phase accounts and explicit uncertainty in one review source package.
master=unary_union(list(envelopes.values()))
park=next(g for g,p in load(V8/'nodes.geojson') if p['node_id']=='C03')
nodegeom=[(commons,dict(node_id='A03',name='Market commons and climate refuge',phase=1)),(prod,dict(node_id='B03',name='Compute and repair precinct',phase=1)),(park,dict(node_id='C03',name='Seasonal wash park',phase=2))]
writegeo('districts.geojson',districts);writegeo('land_use.geojson',units);writegeo('buildings.geojson',build);writegeo('movement.geojson',streets+paths+access);writegeo('assets.geojson',assets);writegeo('phasing.geojson',phase_geoms);writegeo('nodes.geojson',nodegeom);writegeo('master_area.geojson',[(master,dict(name='Complete proposed multi-district city study; not the entire competition site'))])
# Whole-site roles are retained only as a territorial allocation context and updated for the actual city.
territory=[];remaining=scope
for g,p in districts:
 q=g.intersection(remaining);territory.append((q,dict(role=p['id'],name=p['name'])));remaining=remaining.difference(q)
for g,p in roles0:
 q=g.intersection(remaining)
 if not q.is_empty:territory.append((q,p));remaining=remaining.difference(q)
writegeo('structure.geojson',territory)
(O/'phasing_programme.json').write_text(json.dumps(dict(schema_version=1,status='all_phase_design_scenario_not_approved_calendar',phases=programme),indent=2)+'\n')
(O/'metrics.json').write_text(json.dumps(dict(evidence='computed geometry plus declared operating scenarios',phases=programme,resources=resource,dispatch_phase1=dispatch,school_capacity=school_capacity,school_walk_gate_network=walk_results,worker_beds_not_residents=sum(p.get('worker_beds',0) for g,p in build)),indent=2)+'\n')
qa=dict(status='design_review_not_organiser_approval',source_commit='ac96714',buildings=len(build),residential_blocks=len(res_blocks),dwelling_count=sum(p['dwellings'] for g,p in build),population_scenario=sum(p['dwellings'] for g,p in build)*2.5,jobs_design_capacity=sum(p['jobs'] for g,p in build),building_overlap_m2=round(sum(g.area for g,p in build)-unary_union([g for g,p in build]).area,4),district_accounts={},road_building_conflicts=[],block_terrain_reserves=sum(p['use']=='terrain_review' for g,p in units))
for name,envelope in envelopes.items():
 us=[g for g,p in units if p['district']==name];uu=unary_union(us);qa['district_accounts'][name]=dict(gross_m2=round(envelope.area),gap_m2=round(envelope.difference(uu).area,3),overlap_m2=round(sum(g.area for g in us)-uu.area,3))
 assert envelope.difference(uu).area<.1 and abs(sum(g.area for g in us)-uu.area)<.1
roadnet=unary_union([g.buffer(p['width_m']/2,cap_style=2) for g,p in streets])
qa['road_building_conflicts']=[p['id'] for g,p in build if g.intersects(roadnet)]
assert not qa['road_building_conflicts'],qa['road_building_conflicts']
assert qa['building_overlap_m2']<.1,qa['building_overlap_m2']
assert sum(q['new_dwellings'] for q in programme)==qa['dwelling_count']
qa['limits']=['Declared demographic, staffing, job-space, power and water coefficients are design assumptions, not observed demand','Source water and fixed-pilot/living-quarter demand remain unverified; occupancy cannot begin before the combined balance clears','School distances are street-network block-gate tests; individual doors and safe crossings require detailed design','All road/platform geometry remains concept design; local surveys, hydraulics, seismic and noise/dust studies are outstanding','Node finished perspectives have not been regenerated; the deliverable uses formal plans and explicitly diagrammatic axonometrics']
(O/'qa.json').write_text(json.dumps(qa,indent=2)+'\n')
(O/'assumptions.json').write_text(json.dumps(dict(status='declared_scenarios',items=['2.5 residents per dwelling at full occupancy','Residential bars: 24 dwellings in 2880 m2 GFA; terraces: 8 dwellings in 960 m2 GFA','Mixed-use building: 20 dwellings in upper 2400 m2; 70 design jobs in lower 2400 m2','Education demand 15% of residents; 360 places per 2160 m2 wing; operations and local standards to verify','School/block terrain screen uses 60 m DEM; housing blocks over median 3.5% or P95 8% held for terrain review','Water 120 L/resident/day + 25 L/resident/day services; employment water 25 L/job/day for 300 days; losses 10%; sewage recovery 65%','Compute cooling WUE 0.02 L/kWh, PUE 1.25, no credited heat reuse; independent nearby production receiver remains a later optional trial','Annual IT energy after Phase 1 uses 60% utilisation scenario; Phase 1 uses the explicit synthetic dispatch','Job totals are floor-space/programme capacity, not existing or contracted employment; household livelihood verification gates actual housing release','Fixed arrays keep forage grass/jojoba; their demand is unknown and not silently counted as zero']),indent=2)+'\n')
print('GEOMETRY',json.dumps(qa));print('PROGRAMME',json.dumps(programme));print('RESOURCES',json.dumps(resource));print('DISPATCH',json.dumps(dispatch))

# Shared graphics helpers: all thematic maps read the exact geometry above.
BG='#F8F6F0';INK='#263C43';MUT='#68766F'
COL={'residential':'#DECBAA','mixed_use':'#C99172','school':'#A5BCC8','daily_centre':'#C69E74','dry_park':'#B6C19F','terrain_review':'#E8E5DC','streets':'#B5BFC2','dry_open_space':'#EBE5D8','public_commons':'#C39177','civic':'#B78C7C','arrival':'#B2BFC4','culture':'#BD99A2','compute':'#899FAB','industry':'#A8AB99','infrastructure':'#9CADAA','energy':'#D0C08A','agriculture':'#B5C39B','logistics':'#AE99AA','operational_reserve':'#E4E1D7'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK})
CITY=(572200,6555600,576250,6559300);PRODUCT=(572800,6551700,574950,6555300)
pages=[];view_registry=[]
def polys(g):
 if g.is_empty:return
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from polys(q)
def fill(ax,g,c,edge='none',lw=.4,hatch=None,alpha=1):
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
def label(ax,g,s,size=9,dx=0,dy=0):
 p=g if g.geom_type=='Point' else g.centroid;ax.text(p.x/1000+dx,p.y/1000+dy,s,fontsize=size,ha='center',va='center',color=INK,bbox=dict(facecolor=BG,edgecolor='none',alpha=.88,pad=1.5))
def tx(f,x,y,s,size=11,**kw):return f.text(x,y,s,fontsize=size,color=kw.pop('color',INK),**kw)
def wrap(s,n=51):return '\n'.join(textwrap.wrap(s,n))
def panel(f,y,title,body,x=.715,width=42):tx(f,x,y,title,13,weight='bold');tx(f,x,y-.035,wrap(body,width),10.5,va='top',linespacing=1.4)
def page(n,title,sub):
 f=plt.figure(figsize=(16.54,11.69),facecolor=BG);tx(f,.04,.957,'AGUA FINITA / V9 COMPLETE-CITY DESIGN REVIEW',10,weight='bold',color='#8A624B');tx(f,.04,.908,title,24,weight='bold');tx(f,.04,.866,sub,10.5)
 tx(f,.04,.025,f'{n:02} / Jingyuan Huang / 27 October 2026 / Requirements ac96714 / Concept geometry + declared operating scenarios; not approval',8,color=MUT)
 return f
def frame(ax,bounds,scale=500):
 x0,y0,x1,y1=np.array(bounds)/1000;pad=.03*(x1-x0);ax.set(xlim=(x0-pad,x1+pad),ylim=(y0-pad,y1+pad));ax.set_aspect('equal');ax.axis('off')
 x=x0+.025*(x1-x0);y=y0+.025*(y1-y0);ax.plot([x,x+scale/1000],[y,y],color=INK,lw=2);ax.text(x,y+.018*(y1-y0),f'{scale/1000:g} km',fontsize=8)
 ax.annotate('N',xy=(x1-.03*(x1-x0),y1-.015*(y1-y0)),xytext=(x1-.03*(x1-x0),y1-.12*(y1-y0)),arrowprops=dict(arrowstyle='->',color=INK),ha='center',fontsize=9)
def base(ax,bounds,screen=False):
 w=box(*bounds);fill(ax,scope.intersection(w),'#EEEADF');line(ax,scope.intersection(w),INK,.8);line(ax,channels.intersection(w),'#9EB0AF',.7)
 if screen:fill(ax,flood.intersection(w),'none',edge='#C3CAC0',lw=.2,hatch='///')
 for g in [fields,living]:fill(ax,g.intersection(w),'#B5AA83',edge='#8E866A',lw=.7)
def citymap(ax,mode='land',bounds=CITY):
 base(ax,bounds,mode=='ecology');win=box(*bounds)
 for g,p in units:
  if not g.intersects(win):continue
  color=COL.get(p['use'],'#DDD8CE')
  if mode=='structure':color='#D9CDB9' if p['district']=='R' else '#BD8D75'
  if mode=='phase':color={1:'#B98062',2:'#9BAF92',3:'#8EA5B4'}[p['phase']]
  if mode=='services':
   if p['use']=='residential':
    dist=walk_per_block.get(p['id'],0);color='#D8C4A2' if dist<=1000 else '#D5A18D'
   elif p['use'] not in ['school','daily_centre','dry_park','public_commons','civic','culture']:color='#E7E3D8'
  if mode=='ecology' and p['use'] not in ['dry_park','dry_open_space','terrain_review','public_commons']:color='#E5DFD2'
  fill(ax,g.intersection(win),color,edge='#A8A396',lw=.18)
 for g,p in streets:
  q=g.intersection(win)
  if not q.is_empty:line(ax,q,'#6E858D' if p['hierarchy'] in ['primary','secondary'] else '#A1ACAC',1.1 if p['hierarchy'] in ['primary','secondary'] else .35)
 if mode in ['land','structure']:
  for g,p in build:
   if g.intersects(win):fill(ax,g,'#81766B' if p['use'] in ['residential','mixed_use'] else '#718990',lw=0)
 if mode in ['services','ecology']:
  for g,p in paths:
   if g.intersects(win):line(ax,g.intersection(win),'#4F8982',.55)
 frame(ax,bounds)
def prod_inset(f,bounds=PRODUCT):
 a=f.add_axes([.72,.11,.24,.27]);citymap(a,'land',bounds);a.set_title('P + S / separate productive system',fontsize=9,loc='left');return a
def save(f,name,extent=CITY):
 if name in ['02-complete-city-plan','07-land-use-and-accounts']:
  f.legend(handles=[Patch(facecolor=COL[k],label=v) for k,v in [('residential','Housing'),('mixed_use','Mixed use'),('school','School'),('daily_centre','Daily services'),('dry_park','Dry park'),('compute','Compute'),('industry','Workshops'),('energy','Solar'),('terrain_review','Terrain reserve')]],loc='lower center',bbox_to_anchor=(.5,.05),ncol=5,fontsize=8,frameon=False)
 f.savefig(O/(name+'.png'),dpi=160,facecolor=BG);pages.append((f,name));view_registry.append(dict(path=name+'.png',type='formal_diagram',projection='orthographic plan unless explicitly axonometric',extent_utm19s=list(extent),phase='full planned build-out; phase legends identify exceptions',geometry_source='geometry/',note='Original geometry drawing; no inferred physical camera'))

f=page(1,'The whole site and the complete proposed settlement system','Issued boundary retained / full planned construction is distinguished from territorial options and unbuilt land.')
a=f.add_axes([.035,.14,.63,.68])
rolecol={'R':COL['residential'],'C':COL['mixed_use'],'P':COL['compute'],'S':COL['energy'],'A':COL['agriculture'],'N':COL['industry'],'E':COL['logistics'],'energy':'#DBCF9E','agri':'#C6D0B5','fixed_agri':'#B5AA83','fixed_living':'#B5AA83'}
for g,p in territory:fill(a,g,rolecol.get(p.get('role'),'#E8E5DB'))
line(a,scope,INK,1);line(a,channels.intersection(scope),'#A1B2B1',.5)
for g,p in regional:
 if (p.get('from_id'),p.get('to_id')) in [('A','K1'),('K1','K2'),('K2','C'),('K1','D'),('D','E')]:line(a,g,'#71858B',1,'--')
for g,p in districts:label(a,g,p['id'],9,1,.4)
label(a,living,'FIXED LIVING QUARTER',7,3,-2);label(a,fields,'FIXED FIELDS',7,0,-2)
frame(a,scope.bounds,10000)
panel(f,.78,'A complete city, built in three stages',f"{qa['dwelling_count']:,} designed dwellings / {qa['population_scenario']:,.0f} resident scenario at full occupancy. All R/C blocks are assigned a phase and use. These are conditional design capacities, not observed demand.")
panel(f,.56,'Production at its own scale','P contains compute, repair and metered utility works. S contains explicit phased PV fields. N is a farm-service hub. E is a gateway workplace with roster beds, not a second residential city.')
panel(f,.34,'Territorial land is not all construction','Remaining energy/agriculture roles are options, not installed PV or irrigated fields. No added population is assigned to them. Fixed pilots are unchanged; forage grass and jojoba stay under their arrays.')
tx(f,.04,.075,'Full-site map / current geometric area 1,658.82 km2; nominal competition label 1,656 km2 / dashed regional corridors are studies, not secured roads.',9,color=MUT)
save(f,'01-whole-site',scope.bounds)

f=page(2,'Complete urban layout and its productive counterpart','Readable blocks, streets, heights and anchors across all three phases; the productive inset is geographically separate.')
a=f.add_axes([.035,.14,.65,.68]);citymap(a)
for g,p in services:
 if p['use']=='school':label(a,g,'SCHOOL',6)
label(a,commons,'A03',8);label(a,park,'C03',8)
panel(f,.79,'R / continuous residential fabric',f"{len(res_blocks)} housing blocks. Three-storey street-front apartments and two-storey terraces share public courts and streets. Terrain and boundary remnants are explicitly unbuilt, rather than counted as housing.")
panel(f,.57,'C / mixed-use centre at arrival','A compact market/commons, primary-health and learning buildings, passenger arrival and phased mixed-use blocks. Local schools and daily services remain in R; C does not replace them.')
prod_inset(f);save(f,'02-complete-city-plan')

f=page(3,'01 / Planning structure','One residential district with connected release precincts, a town-level centre and separate production; no repeated micro-city packages.')
a=f.add_axes([.035,.14,.65,.68]);citymap(a,'structure')
for yy,title in [(6557100,'SOUTH RESIDENTIAL PRECINCT'),(6558500,'NORTH RESIDENTIAL PRECINCT')]:label(a,Point(575000,yy),title,8)
label(a,Point(574250,6556200),'TOWN CENTRE',9);label(a,park,'SEASONAL WASH EDGE',8,-.1,.1)
panel(f,.79,'Decision / keep housing continuous','Secondary streets connect the south and north precincts. Services and open-space blocks reinforce the residential fabric. There is no compute campus, logistics yard or institutional barrier inserted between them.')
panel(f,.55,'Decision / scale centres by role','Daily centres support their surrounding homes. C serves the wider town. P/N/E serve productive systems with their own access and operating arrangements. More distance by itself earns no design credit.')
prod_inset(f);save(f,'03-planning-structure')

f=page(4,'02 / Functional programme and operating links','Functions are relationships between activities; the separate land-use sheet accounts for spatial units and areas.')
a=f.add_axes([.035,.14,.48,.68]);citymap(a,'structure')
b=f.add_axes([.56,.19,.40,.60]);b.set(xlim=(0,1),ylim=(0,1));b.axis('off')
boxes={'R':(.05,.72,'R / homes + daily services'),'C':(.50,.72,'C / arrival + mixed centre'),'P':(.50,.32,'P / compute + repair'),'S':(.05,.32,'S / PV + storage'),'U':(.27,.06,'U / water + reuse')}
for k,(x,y,t) in boxes.items():b.add_patch(Rectangle((x,y),.41,.16,facecolor=COL.get({'R':'residential','C':'mixed_use','P':'compute','S':'energy','U':'infrastructure'}[k]),edgecolor=INK,lw=.8));b.text(x+.205,y+.08,t,ha='center',va='center',fontsize=9)
for k,l,labtxt in [('R','C','daily trips'),('C','P','worker shuttle'),('S','P','power / controlled load'),('U','R','metered supply'),('U','P','process + reuse')]:
 x,y,_=boxes[k];xx,yy,_=boxes[l];b.annotate('',xy=(xx+.205,yy+.08),xytext=(x+.205,y+.08),arrowprops=dict(arrowstyle='<->',color='#577C82',lw=1.2));b.text((x+xx)/2+.20,(y+yy)/2+.08,labtxt,fontsize=8,ha='center',bbox=dict(facecolor=BG,edgecolor='none',pad=1))
tx(f,.56,.12,'No residential heat pipe is credited. Production heat reuse requires a real nearby receiver and tested temperatures, demand and economics.',10)
save(f,'04-functional-programme')

f=page(5,'03 / Streets, mobility and arrival','Connected primary/secondary/local streets, public transport and court access; regional and production freight are separate corridor studies.')
a=f.add_axes([.035,.14,.65,.68]);citymap(a,'ecology')
for g,p in streets:
 if p.get('district') in ['R','C']:line(a,g,'#4D6C7B' if p['hierarchy'] in ['primary','secondary'] else '#9AA8A9',1.8 if p['hierarchy'] in ['primary','secondary'] else .5)
for g,p in access:
 if p['id']=='A':line(a,g,'#A87951',1.6,'--')
bus=LineString([(574200,6556050),(574200,6556500),(574700,6556500),(574700,6558700)])
line(a,bus,'#A85F48',2.4)
for yy in [6556650,6557100,6557550,6558000,6558450,6558700]:a.scatter(574700/1000,yy/1000,s=20,color='#A85F48',zorder=8)
panel(f,.79,'Town movement hierarchy','Primary arrival meets C. Secondary distributors and a bus spine connect residential precincts. Local streets and public court paths reach individual blocks; school entrances are served by local routes, not production freight.')
panel(f,.56,'Associated corridors are measured studies','F bypasses R and C; the worker shuttle connects C and P. RN40 access and bridge/culvert designs remain unresolved enabling works. A drawn line does not establish an acquired right or an operating road.')
prod_inset(f);save(f,'05-streets-and-mobility')

f=page(6,'04 / Ecology, landscape and water-sensitive public space','Landscape connects existing terrain/channel structure to dry public space and engineered shade; flood screening is not a lake.')
a=f.add_axes([.035,.14,.65,.68]);citymap(a,'ecology');line(a,park,'#6C897B',1.5)
for g,p in units:
 if p['use'] in ['dry_park','dry_open_space'] and g.intersects(box(*CITY)):fill(a,g.intersection(box(*CITY)),'#BCC6AC',edge='#8DA184',lw=.3)
panel(f,.79,'Source landscape and designed ground','Mapped washes retain conveyance; C03 visitor paths are removable and close on warning. The eastern edge has terrain-review land. Neither area is treated as a verified hydraulic boundary or as ornamental water.')
panel(f,.56,'Shade does not mean irrigated forest','Public court routes, arcades and roofed stops provide explicit shade opportunities. Dry parks use mineral ground and limited planting subject to reuse supply. No procedural trees, canals or lawns are inferred.')
prod_inset(f);save(f,'06-ecology-landscape')

f=page(7,'05 / Land-use units and reconciled accounts','Districts, functional activities, net land-use units and construction phases are different accounts, linked by stable IDs.')
a=f.add_axes([.035,.14,.65,.68]);citymap(a,'phase' if False else 'land')
landtot={}
for g,p in units:landtot[p['use']]=landtot.get(p['use'],0)+g.area/1e4
textrows=sorted(landtot.items(),key=lambda kv:-kv[1])
tx(f,.715,.79,'NET LAND / hectares',13,weight='bold')
for i,(k,v) in enumerate(textrows[:14]):tx(f,.715,.75-i*.031,f'{k.replace("_"," "):<23} {v:8.1f}',9.5,family='DejaVu Sans Mono')
tx(f,.715,.27,wrap('All seven district accounts close without overlap or omission. Open and terrain-review ground has no residential capacity. Floor area is computed from actual submitted footprints x floors.',42),10.5,va='top',linespacing=1.4)
tx(f,.04,.071,'Housing form is a design scenario: 120 m2 gross residential floor area per dwelling. GFA, dwellings, school provision and phase quantities share the same building IDs.',9,color=MUT)
save(f,'07-land-use-and-accounts')

f=page(8,'06 / Public space, education and daily services','Capacity and access are checked together: this is a block-gate network test, not an unverified door-to-door walkability claim.')
a=f.add_axes([.035,.14,.65,.68]);citymap(a,'services')
for c in school_specs:label(a,c['g'],f"EDU / P{c['phase']}",7)
panel(f,.79,'Education grows with housing',f"Full-city resident scenario {qa['population_scenario']:,.0f}; education demand at assumed 15% is {resource[-1]['school_need_assumed']:,}. Designed school capacity is {resource[-1]['school_places']:,} places. The age model and local operating standards require verification.")
panel(f,.55,'Measured street-network coverage',f"Full-layout median block-gate distance {walk_results[3]['median_block_gate_m']} m; maximum {walk_results[3]['max_block_gate_m']} m. {walk_results[3]['over_1000m']} blocks exceed the 1,000 m review marker. Those routes need safe crossings and school transport; the marker is not a legal standard.")
prod_inset(f);save(f,'08-public-space-and-services')

def axon(ax,bounds,height_factor=3,elev=48,azim=-62):
 win=box(*bounds);x0,y0,x1,y1=bounds
 faces=[];colors=[]
 for g,p in units:
  q=g.intersection(win)
  for poly in polys(q):
   for tri in triangulate(poly):
    if poly.covers(tri.representative_point()):
     xy=np.asarray(tri.exterior.coords);faces.append([(x-x0,y-y0,0) for x,y in xy]);colors.append(COL.get(p['use'],'#E2DDCF'))
 for g,p in build:
  if not win.intersects(g):continue
  xy=np.asarray(g.exterior.coords)[:-1];z=p['height_m']*height_factor
  faces.append([(x-x0,y-y0,z) for x,y in xy]);colors.append('#9D7965' if p['use'] in ['residential','mixed_use'] else '#718C96')
  for i in range(len(xy)):
   j=(i+1)%len(xy);faces.append([(xy[i,0]-x0,xy[i,1]-y0,0),(xy[j,0]-x0,xy[j,1]-y0,0),(xy[j,0]-x0,xy[j,1]-y0,z),(xy[i,0]-x0,xy[i,1]-y0,z)]);colors.append('#D2BDA7' if p['use'] in ['residential','mixed_use'] else '#ADBCC2')
 ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors='none',zsort='average'))
 ax.set(xlim=(0,x1-x0),ylim=(0,y1-y0),zlim=(0,180));ax.set_box_aspect((x1-x0,y1-y0,(x1-x0)*.12));ax.view_init(elev=elev,azim=azim);ax.set_proj_type('ortho');ax.axis('off');ax.set_facecolor(BG)

f=page(9,'Overall spatial view from the same complete layout','Diagrammatic orthographic axonometric / full build-out / flat analytical datum; building heights x3 for legibility, not terrain or a physical camera.')
a=f.add_axes([.02,.16,.71,.67],projection='3d');axon(a,(573350,6555750,576100,6559150))
panel(f,.81,'The urban whole is visible','Every drawn housing block, town-centre building and school is taken from the same geometry as the plans and accounts. The main frame covers R and C, not the full competition site.')
b=f.add_axes([.72,.20,.25,.30],projection='3d');axon(b,PRODUCT);b.set_title('Separate P + S inset / same orientation',fontsize=10)
tx(f,.72,.14,wrap('P is not moved beside R to fit this sheet. The full-site locator shows N and E; their workplace plans are accounted separately. No local aerial is presented as the whole territory.',44),9.5,va='top')
save(f,'09-overall-axonometric');view_registry[-1].update(type='diagrammatic_overall_spatial_view',projection='orthographic axonometric',elevation_deg=48,azimuth_deg=-62,building_height_scale=3,terrain='flat analytical datum explicitly not a terrain rendering',insets=[dict(name='P + S',extent_utm19s=list(PRODUCT))])

for n,(node,prop) in enumerate(nodegeom,start=10):
 nid=prop['node_id'];f=page(n,nid+' / '+prop['name'],'Node extent and phase are independent of the urban-design enlargement. Plans and sections refer to the current geometry.')
 bounds=node.buffer(170 if nid=='A03' else 220).bounds
 a=f.add_axes([.04,.32,.63,.49]);citymap(a,'land',bounds)
 if nid=='C03':
  line(a,node,'#698C7B',1.3);line(a,channels.intersection(box(*bounds)),'#829E9F',1.8)
  p=node.centroid;trail=LineString([(node.bounds[2]-50,node.bounds[1]+120),(node.bounds[2]-50,node.bounds[3]-120)])
  line(a,trail,'#8F6B50',2,'--')
 elif nid=='A03':
  line(a,commons,'#885B49',1.4)
  for yy in [commons.bounds[1]+5,commons.bounds[3]-11]:fill(a,box(commons.bounds[0]+5,yy,commons.bounds[2]-5,yy+6),'#826A57')
 b=f.add_axes([.055,.12,.60,.14]);b.axis('off')
 if nid=='A03':
  b.plot([0,150],[0,0],color=INK);b.plot([15,15,45,45],[0,5,5,0],color='#8C6C55',lw=2);b.plot([105,105,135,135],[0,5,5,0],color='#8C6C55',lw=2);b.text(75,1,'Public commons / clear step-free ground',ha='center',fontsize=9);b.set(xlim=(0,150),ylim=(-1,9));txt='A 0.64 ha commons belongs to the town-level market/refuge, not to every housing block. Two canopy bands, shaded edges and nearby indoor refuge support public use. Seasonal shade, structure and operational staffing remain to verify.'
 elif nid=='B03':
  b.plot([0,600],[0,0],color=INK)
  for x in [50,220,390]:b.add_patch(Rectangle((x,0),96,8,facecolor='#A5B9C2',edgecolor=INK))
  b.text(300,12,'Concept hall section / 8 MW in eight staged 1 MW halls',ha='center',fontsize=9);b.set(xlim=(0,600),ylim=(-2,20));txt='Compute and repair share a controlled productive precinct with water metering and dry cooling. Housing remains in R. No long residential heat network is credited. Phase 1 is 2 MW; expansion reaches 8 MW only after resource and demand gates.'
 else:
  b.plot([0,80,160,240,320,400,500],[4,4,1,0,1,4,4],color='#7C918C',lw=2);b.plot([400,500],[4.5,4.5],color='#8F6B50',lw=2);b.text(250,6,'Diagrammatic wash section / not surveyed flood levels',ha='center',fontsize=9);b.set(xlim=(0,500),ylim=(-1,9));txt='The source channel is a seasonal conveyance route, not a lake. The visitor path stays on the edge, is removable and closes on warning. No occupied pavilion or dam is placed on the channel. Actual safe edges depend on survey and hydraulics.'
 panel(f,.76,'City promise tested',txt)
 panel(f,.43,'Current view status','These are formal source plans and explanatory sections. New finished aerial and eye-level perspectives must later use matching controls and registered camera footprints. Older node images are not used for this redesign.')
 save(f,f'{n:02}-{nid}-plan-section',bounds)

f=page(13,'Three construction phases with matching capacity accounts','Every proposed development zone appears in the same geometry-linked programme; timing is conditional, not an approved calendar.')
a=f.add_axes([.035,.30,.62,.51]);citymap(a,'phase')
b=f.add_axes([.70,.39,.25,.32]);citymap(b,'phase',PRODUCT);b.set_title('Separate productive phases',fontsize=10)
tax=f.add_axes([.045,.105,.91,.15]);tax.axis('off');rows=[[q['phase'],q['new_residents'],q['total_residents'],q['new_dwellings'],q['total_dwellings'],q['new_jobs'],q['total_jobs']] for q in programme]
tbl=tax.table(cellText=[[f'{v:,.0f}' for v in row] for row in rows],colLabels=['Phase','New people','Total people','New homes','Total homes','New jobs','Total jobs'],cellLoc='center',bbox=[0,0,1,1]);tbl.auto_set_font_size(False);tbl.set_fontsize(10)
for (i,j),cell in tbl.get_celld().items():cell.set_facecolor('#DED5C2' if i==0 else BG);cell.set_edgecolor('#D3CFC4')
tx(f,.70,.30,'P1: core life + production\nP2: connected district expansion\nP3: northern fabric + gateway\n\nN and E have their own service,\ntransport and utility conditions.',10,linespacing=1.5)
save(f,'13-phasing-and-capacities')

f=page(14,'Resources, livelihoods and independent first operation','Demand is computed before claiming supply. Missing rights and fixed-pilot demand are not treated as zero.')
r=resource[0]
panel(f,.79,'Phase 1 / a measured demand scenario',f"{p1['total_residents']:,.0f} residents; {p1['total_jobs']:,.0f} design job capacity. Fresh source requirement for the NEW programme: {r['fresh_requirement_m3_y']:,.0f} m3/year. Existing fixed pilots/quarter remain additional and unverified.",x=.05,width=63)
panel(f,.57,'First works and independent operation','Regional access and corridor rights; verified source/yield/quality; covered storage and reuse; power/fibre and protected essential loads; school/health/market operators; wastewater/waste and emergency response. Housing occupancy waits for these, even if later stages stop.',x=.05,width=63)
panel(f,.32,'Livelihood and demand are real gates','Employment totals are design capacity, not signed jobs. The workforce/income mix and the demand for occupied homes require an evidenced case. Release housing in funded tranches rather than constructing the entire capacity scenario at once.',x=.05,width=63)
panel(f,.79,'Synthetic hourly dispatch',f"16 MWp PV / 40 MWh battery / 2 MW peak IT. Fully matched hours: {dispatch['fully_matched_hours_pct']}%; achieved IT utilisation: {dispatch['it_utilisation_pct']}%. Unmatched grid imports are not credited carbon-free. No power export is assumed.",x=.57,width=57)
panel(f,.54,'A 30% water shortage changes use','Protect drinking water, care, wastewater and essential safety. Curtail new irrigation trials and discretionary cleaning, then interruptible production/IT. Existing pilot obligations need operator agreement; their water is not silently confiscated.',x=.57,width=57)
panel(f,.29,'Checks and remaining verification',f"{len(build):,} buildings; {len(res_blocks)} housing blocks. Land accounts close and encoded building/road overlaps are checked. These checks do not establish water rights, school operation, highway access, seismic design, noise performance or image approval.",x=.57,width=57)
save(f,'14-resource-and-delivery')

# Regional planning is a separate gross territorial account, not a land-use colour map.
# Demarcations are explicit design choices for review, not cadastral or hydraulic limits.
mountain_region=unary_union([g for g,p in load(P/'geometry/structure.geojson') if p.get('screening_class')=='protect']).intersection(box(590000,6530000,640000,6570000))
regional_specs=[
 ('Z6','Southeast mountain stewardship region',mountain_region,'#C9CEC3','Mountain and dryland stewardship; no urban allocation. DEM terrain screening governs any access intervention.'),
 ('Z1','Southwest urban and service region',box(550000,6530000,590000,6566500),'#D3AD8E','R + C continuous living district; separate P/S utilities; fixed pilots retained.'),
 ('Z2','Northwest agricultural research region',box(550000,6566500,578000,6620000),'#B8C49B','Dryland crop trials and agricultural service; no blanket irrigation or new town assumed.'),
 ('Z3','Northern energy research region',box(578000,6577000,640000,6620000),'#D9CB92','Energy research and northern maintenance hub; installations follow demand and power rights.'),
 ('Z4','Central production and transfer region',box(578000,6566500,606000,6577000),'#ABC2C4','Regional transfer and conditional productive sites; source washes and terrain remain overlays.'),
 ('Z5','Eastern gateway and logistics region',box(606000,6530000,640000,6577000),'#B9AAC4','Conditional gateway with worker services. Trade and access rights precede works.'),
 ('ZX','Unassigned review land',box(550000,6530000,640000,6620000),'#C9CEC3','Residual boundary and dryland review land, assigned to mountain stewardship.')]
regions=[];rem=scope
for rid,name,mask,color,desc in regional_specs:
 q=rem.intersection(mask)
 if not q.is_empty:
  regions.append((q,dict(id=rid,name=name,area_km2=round(q.area/1e6,3),color=color,programme=desc,boundary_basis='Proposed strategic demarcation by geographic sector and service role; not an issued regulatory boundary')));rem=rem.difference(q)
extra=[g for g,p in regions if p['id']=='ZX']
regions=[(g.union(unary_union(extra)),dict(p,area_km2=round(g.union(unary_union(extra)).area/1e6,3))) if p['id']=='Z6' else (g,p) for g,p in regions if p['id']!='ZX']
regions.sort(key=lambda item:item[1]['id'])
assert rem.area<.1,('unassigned regional land',rem.area)
assert abs(sum(g.area for g,p in regions)-scope.area)<.1
qa['regional_partition']=dict(regions=len(regions),gap_m2=round(scope.difference(unary_union([g for g,p in regions])).area,4),overlap_m2=round(sum(g.area for g,p in regions)-unary_union([g for g,p in regions]).area,4))
(O/'qa.json').write_text(json.dumps(qa,indent=2)+'\n')
writegeo('planning_regions.geojson',regions)
(O/'regional-programme.json').write_text(json.dumps(dict(status='proposed_strategic_regions_for_review',gross_area_km2=scope.area/1e6,regions=[p for g,p in regions],distinction='Regions partition the whole site. Land-use units subdivide development districts. Flood/terrain/fixed-pilot layers constrain each region independently. Gross region areas are not construction land.'),indent=2)+'\n')
def regionalmap(ax,labels=True,labelsize=10):
 for g,p in regions:fill(ax,g,p['color'],edge=INK,lw=.8)
 line(ax,channels.intersection(scope),'#718B91',.65)
 for g in [fields,living]:fill(ax,g,'#847766',edge=INK,lw=.5,hatch='///')
 for g,p in regional:
  if (p.get('from_id'),p.get('to_id')) in [('A','K1'),('K1','K2'),('K2','C'),('K1','D'),('D','E')]:line(ax,g,'#4B6069',1.5,'--')
 for g,p in districts:line(ax,g,INK,.85)
 if labels:
  positions={'Z1':(581000,6552500),'Z2':(568500,6583500),'Z3':(586000,6587500),'Z4':(595000,6571800),'Z5':(624000,6562000),'Z6':(610000,6558500)}
  short={'Z1':'SOUTHWEST\nURBAN + SERVICES','Z2':'NORTHWEST\nAGRICULTURAL RESEARCH','Z3':'NORTHERN\nENERGY RESEARCH','Z4':'CENTRAL\nPRODUCTION + TRANSFER','Z5':'EASTERN\nGATEWAY + LOGISTICS','Z6':'SOUTHEAST\nMOUNTAIN STEWARDSHIP'}
  for g,p in regions:
   label(ax,Point(*positions[p['id']]),p['id']+' / '+short[p['id']],labelsize)
 frame(ax,scope.bounds,10000)
f=page(0,'Whole-site regional plan / six coordinated regions','Strategic regions cover the entire issued site; construction land, ecological constraints and phases are separate layers.')
a=f.add_axes([.03,.13,.66,.70]);regionalmap(a)
for i,(g,p) in enumerate(regions):
 yy=.81-i*.116
 tx(f,.715,yy,p['id']+' / '+p['name'].split(' region')[0],11.3,weight='bold')
 tx(f,.715,yy-.031,f"{p['area_km2']:,.1f} km2 gross / proposed role",9.5,color=MUT)
 tx(f,.715,yy-.057,wrap(p['programme'],52),8.8,va='top',linespacing=1.35)
tx(f,.04,.075,'Solid edges: proposed service-region demarcations (not statutory lines). Thin grey-blue: source seasonal channels. Dashed: regional corridor studies. Hatched: fixed pilots.',8.5)
tx(f,.04,.053,'Z1 contains the detailed urban plan. Z2-Z6 remain region-scale proposals with stated activation gates; their gross areas are not approved buildable land.',8.5)
save(f,'00-whole-site-regions',scope.bounds);pages.insert(0,pages.pop())

with PdfPages(O/'agua-finita-v9-complete-city-review.pdf') as pdf:
 for f,name in pages:pdf.savefig(f,facecolor=BG);plt.close(f)

# Review A0: plans/diagrammatic massing and a readable phase account, not raw model captures.
f=plt.figure(figsize=(46.81,33.11),facecolor=BG)
tx(f,.035,.962,'AGUA FINITA',56,weight='bold',color='#315D60');tx(f,.035,.924,'CONTINUOUS LIVING DISTRICTS / INDEPENDENT PRODUCTION / WATER-GATED CONSTRUCTION',22)
tx(f,.965,.963,'JINGYUAN HUANG / 27 OCT 2026',17,ha='right');tx(f,.965,.933,'V9 / COMPLETE-CITY PLANNING REVIEW',17,ha='right')
a=f.add_axes([.025,.43,.39,.46]);regionalmap(a,labelsize=18);a.set_title('WHOLE-SITE REGIONAL PLAN / Z1-Z6',fontsize=24,loc='left')
b=f.add_axes([.43,.48,.35,.40]);citymap(b,'land');b.set_title('Z1 / COMPLETE URBAN PLAN / ALL PHASES',fontsize=22)
c=f.add_axes([.80,.59,.17,.26],projection='3d');axon(c,(573350,6555750,576100,6559150));c.set_title('URBAN AXON / HEIGHTS x3',fontsize=20)
e=f.add_axes([.82,.40,.14,.17]);citymap(e,'land',PRODUCT);e.set_title('SEPARATE P + S',fontsize=16)
f.legend(handles=[Patch(facecolor=COL[k],label=v) for k,v in [('residential','Housing'),('mixed_use','Mixed use'),('school','Schools'),('daily_centre','Daily services'),('dry_park','Dry parks'),('civic','Civic'),('compute','Compute'),('energy','Solar')]],loc='lower center',bbox_to_anchor=(.61,.445),ncol=4,fontsize=16,frameon=False)
d=f.add_axes([.025,.075,.24,.30]);citymap(d,'phase');d.set_title('PHASE 1 / 2 / 3 MAP',fontsize=23,loc='left')
f.legend(handles=[Patch(facecolor=c,label=t) for c,t in [('#B98062','PHASE 1'),('#9BAF92','PHASE 2'),('#8EA5B4','PHASE 3')]],loc='lower left',bbox_to_anchor=(.035,.052),ncol=3,fontsize=17,frameon=False)
t=f.add_axes([.31,.23,.66,.13]);t.axis('off');tbl=t.table(cellText=[[f'{v:,.0f}' for v in row] for row in rows],colLabels=['Phase','New people','Total people','New homes','Total homes','New jobs','Total jobs'],cellLoc='center',bbox=[0,0,1,1]);tbl.auto_set_font_size(False);tbl.set_fontsize(22)
for (i,j),cell in tbl.get_celld().items():cell.set_facecolor('#DED5C2' if i==0 else BG);cell.set_edgecolor('#BEB7A8')
tx(f,.31,.42,f"{qa['dwelling_count']:,} DWELLINGS  /  {qa['population_scenario']:,.0f} RESIDENT SCENARIO  /  {resource[-1]['school_places']:,} SCHOOL PLACES",29,weight='bold')
for x,title,body in [(.31,'P1 / ESTABLISH','Core housing, school, care, market, production and enabling utilities.\nCombined fixed/new water and access cleared before occupancy.'),(.54,'P2 / CONNECT','Extend the same residential fabric, services, production and trial field.\nStart only with demand and audited resource headroom.'),(.77,'P3 / COMPLETE','Northern residential precinct and conditional eastern gateway.\nIndependent trade, access, roster welfare and utilities required.')]:
 tx(f,x,.18,title,23,weight='bold');tx(f,x,.145,body,17,linespacing=1.5)
tx(f,.035,.025,'SOURCE: XCITY issued site / requirements ac96714. All buildings, plans, phase totals and massing use the same V9 geometry. Capacities are declared scenarios, not demand, rights or approval.',14,color=MUT)
f.savefig(O/'a0-planning-review.jpg',dpi=120,facecolor=BG)
with PdfPages(O/'agua-finita-v9-a0-planning-review.pdf') as pdf:pdf.savefig(f,facecolor=BG)
plt.close(f)
(O/'view-registry.json').write_text(json.dumps(view_registry,indent=2)+'\n')
sources=[R/'AGENTS.md',R/'brief/requirements.json',R/'brief/design-depth.json',S/'boundaries/scope_9_13.geojson',S/'water/channels_dem.geojson',S/'terrain/dem_9_13_utm19s_60m.png',V8/'districts.geojson',V8/'access-studies.geojson',V8/'whole-site-roles.geojson',P/'geometry/structure.geojson',P/'reviews/whole-site-v3/centres.geojson',P/'reviews/whole-site-v3/corridors.geojson',Path(__file__)]
(O/'source-freeze.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')
for name in ['agua-finita-v9-complete-city-review.pdf','agua-finita-v9-a0-planning-review.pdf','02-complete-city-plan.png','09-overall-axonometric.png','13-phasing-and-capacities.png','a0-planning-review.jpg','qa.json','metrics.json','00-whole-site-regions.png','regional-programme.json']:
 shutil.copy2(O/name,OUT/name)
print('OUTPUT',OUT)
