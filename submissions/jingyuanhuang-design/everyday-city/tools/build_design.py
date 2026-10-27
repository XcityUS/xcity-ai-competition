"""Original Everyday City geometry. Run from repository root. Source CRS UTM19S; exports WGS84."""
import json,math,heapq
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import shape,mapping,box,Point,LineString,Polygon
from shapely.ops import transform,unary_union,nearest_points
from shapely import contains_xy,make_valid,prepare
from pyproj import Transformer
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parents[1];S=R/'brief/site-package'
t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
G=lambda f:unary_union([transform(t,shape(v['geometry'])) for v in json.loads((S/f).read_text())['features']])
scope=G('boundaries/scope_9_13.geojson');pilot=G('pilot-area/pilot_area.geojson');living=G('pilot-area/pilot_living_area.geojson');fixed=pilot.union(living);flood=G('water/flood_sensitive_dem.geojson').intersection(scope);channels=G('water/channels_dem.geojson').intersection(scope)
raw=np.array(Image.open(S/'terrain/dem_9_13_utm19s_60m.png')).astype(float)
nr,nc=raw.shape[0]//5,raw.shape[1]//5;dem=raw[:nr*5,:nc*5].reshape(nr,5,nc,5).mean((1,3));dy,dx=np.gradient(dem,300);slope=np.hypot(dx,dy)*100
xs=559572.4+(np.arange(nc)+.5)*300;ys=6608973.7-(np.arange(nr)+.5)*300;X,Y=np.meshgrid(xs,ys);inside=contains_xy(scope,X,Y);wet=contains_xy(flood,X,Y)
def cells(mask):return unary_union([box(xs[c]-150,ys[r]-150,xs[c]+150,ys[r]+150) for r,c in zip(*np.where(mask))]).intersection(scope)
suitable=cells(inside & ~wet & (slope<3)&(dem<850)).difference(fixed.buffer(100)).difference(channels.buffer(150))
# Candidate selected by explicit 1.9 x 1.4 km programme fit test; not a prescribed regional boundary.
x0,y0=json.loads((P/'tools/selected_site.json').read_text())['origin_utm_m']
B=lambda a,b,c,d:box(x0+a,y0+b,x0+c,y0+d)
# The compact construction rectangle is intersected with source constraints and widened only at its access head.
master=B(0,0,1900,1400).intersection(scope).difference(fixed.buffer(30));assert master.area>2.65e6
# A dedicated research connection reaches the real field edge, stopping outside its fixed outline.
farm_contact=nearest_points(pilot,B(100,90,850,355))[0]
farm_end=nearest_points(pilot.buffer(35).boundary,B(100,90,850,355))[0]
farm_walk=LineString([(x0+450,y0+180),(farm_end.x,farm_end.y)])
assert scope.covers(farm_walk) and not farm_walk.intersects(fixed)
master=master.union(farm_walk.buffer(45,cap_style=2)).intersection(scope).difference(fixed.buffer(30))
build=[];land=[];moves=[(farm_walk,dict(network='people',shaded=False,name='Productive trail to fixed farm edge / enabling works'))];nodes=[]
def ft(g,**p):return {'type':'Feature','properties':p,'geometry':mapping(make_valid(transform(inv,g)))}
def save(n,fs):
 (P/'geometry'/f'{n}.geojson').write_text(json.dumps({'type':'FeatureCollection','features':fs},indent=2))
def bld(a,b,c,d,use,name,floors=1,**kw):
 g=B(a,b,c,d);assert master.covers(g) and not g.intersects(fixed) and not g.intersects(channels.buffer(150));build.append((g,dict(use=use,name=name,floors=floors,height_m=floors*3.3,**kw)))
# Six 320 m neighbourhoods, each four courtyard units. Shared vehicle/emergency loops at neighbourhood edges.
for j in range(2):
 for i in range(3):
  nx,ny=100+i*360,510+j*380;name=f'Neighbourhood {j*3+i+1}'
  land.append((B(nx-20,ny-20,nx+320,ny+320),'residential',name))
  for cy in range(2):
   for cx in range(2):
    a,b=nx+cx*150,ny+cy*150
    for k,r in enumerate([(a+30,b,a+78,b+12),(a+30,b+98,a+78,b+110),(a,b+30,a+12,b+78),(a+98,b+30,a+110,b+78)]):
     bld(*r,'residential',f'{name} / Court {cy*2+cx+1} / Wing {k+1}',3,dwellings=15)
    bld(a+80,b+82,a+94,b+98,'civic','Common room / laundry',1)
    bld(a+35,b+26,a+73,b+32,'civic','Courtyard shade',1,form='canopy')
    line=LineString([(x0+a+20,y0+b-20),(x0+a+20,y0+b+130)])
    moves.append((line,dict(network='people',shaded=True,name='Courtyard walk')))
  loop=LineString([(x0+nx-20,y0+ny-20),(x0+nx+320,y0+ny-20),(x0+nx+320,y0+ny+320),(x0+nx-20,y0+ny+320),(x0+nx-20,y0+ny-20)])
  moves.append((loop,dict(network='shared',shaded=False,name=name+' low-speed access loop',speed_kmh=10)))
# Civic spine: arrival square, school, health, market, library, indoor heat refuge and sports.
for a,b,c,d,use,name,f in [(1280,520,1430,555,'mixed_use','Market hall',1),(1450,520,1580,555,'mixed_use','Cooperative shops',1),(1280,650,1400,685,'civic','Primary school / 360 places',2),(1450,650,1570,685,'civic','Secondary and vocational school / 240 places',2),(1280,850,1360,885,'civic','Health and care centre / 8 consultation rooms',2),(1460,850,1550,885,'civic','Library and indoor heat refuge',2),(1280,1040,1400,1075,'civic','Community kitchen and childcare / 120 places',1),(1450,1040,1570,1075,'civic','Public assembly and arts workshop',1)]:bld(a,b,c,d,use,name,f)
land.append((B(1240,480,1610,1240),'civic','Everyday services spine'))
# Productive front: two compute halls, four workshops and one thermal reception building.
for i in range(2):bld(1080+i*240,130,1260+i*240,205,'compute',f'Compute hall {i+1}',1)
for i in range(4):bld(1000+i*145,280,1110+i*145,315,'industry',f'Repair / processing workshop {i+1}',1)
bld(1050,220,1130,250,'industry','Low-temperature heat reception / drying',1)
land.append((B(950,90,1600,355),'compute','Compute and cooperative processing'))
# New farm-side public interface remains outside the fixed array boundary.
for i in range(3):bld(180+i*190,180,320+i*190,200,'industry','Farm service / teaching workshop',1)
bld(200,260,760,268,'civic','Shaded farm-edge promenade',1,form='canopy')
land.append((B(100,90,850,355),'industry','Farm-edge service and training campus'))
land.append((B(1640,90,1850,1250),'energy','Solar / battery and utility yard'))
for r in range(20):
 for c in range(7):bld(1660+c*24,120+r*50,1676+c*24,128+r*50,'energy','Solar canopy',1,form='canopy')
# Actual layout for PV is partial; wider source-derived production reserves are not installed capacity.
for i in range(3):bld(1650+i*65,1170,1700+i*65,1190,'infrastructure','Water / battery service module',1)
# One continuous civic walk, east-west commons and south service road; no unmarked production crossing.
for pts,name,shade in [([(80,640),(1610,640)],'School and home walk',True), ([(80,1020),(1610,1020)],'Library and home walk',True), ([(1210,420),(1210,1300)],'Civic spine',True), ([(150,420),(1610,420)],'Productive buffer walk',True), ([(430,420),(430,1300)],'Neighbourhood connector west',True), ([(790,420),(790,1300)],'Neighbourhood connector east',True), ([(150,260),(850,260)],'Farm-edge promenade',True)]:
 moves.append((LineString([(x0+a,y0+b) for a,b in pts]),dict(network='people',shaded=shade,name=name)))
for pts,name in [([(60,60),(1870,60),(1870,1330)],'Utility and freight edge'), ([(60,60),(60,1330),(1610,1330)],'Public arrival and emergency edge'), ([(950,60),(950,355),(1600,355),(1600,60)],'Compute service loop'), ([(100,60),(100,355),(850,355),(850,60)],'Farm servicing loop')]:
 moves.append((LineString([(x0+a,y0+b) for a,b in pts]),dict(network='machine' if 'service' in name or 'freight' in name else 'shared',shaded=False,name=name)))
# Continuous low-speed emergency network joins all neighbourhood loops to the perimeter arrival.
for pts,name in [([(60,490),(1140,490)],'South neighbourhood access'), ([(60,1210),(1140,1210)],'North neighbourhood access'), ([(80,60),(80,1330)],'West emergency spine'), ([(440,830),(440,870)],'Middle access link'), ([(800,830),(800,870)],'East access link'), ([(1610,60),(1610,1330)],'Civic service and emergency spine')]:
 moves.append((LineString([(x0+a,y0+b) for a,b in pts]),dict(network='shared',shaded=False,name=name,speed_kmh=10)))
# Close each courtyard path onto its neighbourhood shared access. Intersections are registered below.
for node_id,g,name,why in [('A01',B(80,490,440,850),'Courtyard Homes','Everyday shared space without tying housing to an employer'),('B03',B(950,90,1600,355),'Useful Compute','Production accepts a civic boundary and has a named heat user'),('C02',B(100,90,850,355).union(farm_walk.buffer(45,cap_style=2)).intersection(master),'Working Farm Edge','Public learning and farm logistics meet outside the protected pilot')]:nodes.append((g,dict(node_id=node_id,name=name,why=why,phase=1)))
# Complete, exclusive master land partition, with remaining commons/open space explicitly accounted.
remain=master;land_features=[]
for g,use,name in land:
 q=g.intersection(remain);land_features.append(ft(q,use=use,name=name,phase=1));remain=remain.difference(q)
land_features.append(ft(remain,use='open_space',name='Public commons, streets and dry-land margins',phase=1))
# Regional structure: one primary city, two later service towns, a separate production backbone and eastern gateway.
centres={'P':master.centroid,'North':Point(582500,6589000),'East':Point(611500,6575000),'Energy':Point(581500,6576000),'Gateway':Point(623000,6561500)}
for k,p in list(centres.items()):
 if not suitable.covers(p):centres[k]=nearest_points(p,suitable.buffer(-100))[1]
zones=[];remaining=scope
sysmap={'P':'living','North':'living','East':'living','Energy':'energy_compute','Gateway':'port'}
def alloc(g,system,name,phase):
 global remaining
 q=g.intersection(remaining)
 if not q.is_empty:zones.append(ft(q,system=system,name=name,phase=phase));remaining=remaining.difference(q)
alloc(pilot,'agri_production','Fixed agrivoltaic pilot / unchanged',1);alloc(living,'living','Fixed first living quarter / outline only',1)
alloc(master,'living','Primary everyday city / complete first district',1)
for k in ['North','East','Energy','Gateway']:alloc(centres[k].buffer(1800 if k!='Energy' else 6000).intersection(suitable),sysmap[k],k+' conditional reserve',2 if k in ['North','Energy'] else 3)
mount=cells(inside & ((slope>=5)|(dem>=850)));alloc(mount,'reserve','Mountain and steep-ground conservation study',3)
alloc(channels.buffer(150).intersection(scope),'reserve','Channel conveyance study / assumed retreat',3)
alloc(cells(inside&(slope<2)&(dem<850)).difference(flood),'agri_production','Low-slope productive research / no irrigation promise',3)
alloc(remaining,'reserve','Dry landscape and unresolved flood-screening land',3)
prepare(scope);prepare(fixed)
# Regional least-cost routes respect the fixed outlines. Corridors are studies, not engineered roads.
cost=1+np.minimum(slope,30)**2*.15+wet*5;cost[~inside]=np.inf;cost[slope>12]=np.inf;cost[contains_xy(fixed,X,Y)]=np.inf
rr,cc=np.where(np.isfinite(cost))
def ij(p):
 i=np.argmin((xs[cc]-p.x)**2+(ys[rr]-p.y)**2);return int(rr[i]),int(cc[i])
def route(p,q):
 a,b=ij(p),ij(q);dist={a:0};prev={};heap=[(0,a)];seen=set()
 while heap:
  d,u=heapq.heappop(heap)
  if u in seen:continue
  seen.add(u)
  if u==b:break
  for dr,dc in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)]:
   v=u[0]+dr,u[1]+dc
   if not(0<=v[0]<nr and 0<=v[1]<nc) or not np.isfinite(cost[v]):continue
   seg=LineString([(xs[u[1]],ys[u[0]]),(xs[v[1]],ys[v[0]])])
   if not scope.covers(seg) or seg.intersects(fixed):continue
   nd=d+(cost[u]+cost[v])/2*math.hypot(dr,dc)
   if nd<dist.get(v,1e99):dist[v]=nd;prev[v]=u;heapq.heappush(heap,(nd,v))
 if b not in dist:raise RuntimeError('No regional connection')
 path=[b]
 while path[-1]!=a:path.append(prev[path[-1]])
 return LineString([(xs[c],ys[r]) for r,c in reversed(path)])
regional=[]
for a,b,phase in [('P','Energy',2),('Energy','North',2),('Energy','East',3),('East','Gateway',3)]:
 g=route(centres[a],centres[b]);regional.append(ft(g,name=a+' to '+b,phase=phase,study_only=True,length_km=round(g.length/1000,3)))
# Both pilot contacts are explicit, no fabricated interiors.
for name,target in [('Fixed farm connection',pilot),('Fixed living-quarter connection',living)]:
 p=nearest_points(target,master)[0];g=route(master.centroid,p);regional.append(ft(g,name=name,phase=1,study_only=True,length_km=round(g.length/1000,3)))
(P/'report/regional-corridors.geojson').write_text(json.dumps({'type':'FeatureCollection','features':regional},indent=2))
(P/'report/centres.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[ft(p,name=k,role=sysmap[k]) for k,p in centres.items()]},indent=2))
# Register all geometric people-versus-service intersections, including shared neighbourhood loops.
people=[g for g,p in moves if p['network']=='people'];vehicles=[g for g,p in moves if p['network'] in ['machine','shared']];cross=[]
for a in people:
 for b in vehicles:
  q=a.intersection(b)
  qs=[q] if q.geom_type=='Point' else list(q.geoms) if q.geom_type=='MultiPoint' else []
  for v in qs:
   if all(v.distance(w)>1 for w in cross):cross.append(v)
move_features=[ft(g,**p) for g,p in moves]+[ft(v,kind='interface',name=f'Controlled crossing {i+1}',rule='Human priority; machine stop; manual release') for i,v in enumerate(cross)]
save('structure',zones);save('master_area',[ft(master,name='Complete phase-one district',phase=1)]);save('land_use',land_features);save('buildings',[ft(g,**p) for g,p in build]);save('movement',move_features);save('nodes',[ft(g,**p,**({'eye_from':list(inv(x0+1000,y0+230)),'eye_to':list(inv(x0+1160,y0+170))} if p['node_id']=='B03' else {'eye_from':list(inv(x0+450,y0+245)),'eye_to':list(inv(x0+450,y0+190))} if p['node_id']=='C02' else {})) for g,p in nodes]);save('phasing',[ft(master,phase=1,name='Complete first district',trigger='Verified access, water, grid, services and maintenance before occupancy')]+[ft(centres[k].buffer(1800).intersection(suitable),phase=2 if k=='North' else 3,name=k+' conditional town',trigger='Audited resource margin >=20%; 80% occupancy; funded services and access') for k in ['North','East','Gateway']])
qa={'origin_utm_m':[x0,y0],'source_commit':'9e504de','source_boundary_revision':'2026-10-27-seam-closure','phase_one_planar_km2':master.area/1e6,'housing_buildings':sum(p['use']=='residential' for g,p in build),'dwellings':sum(p.get('dwellings',0) for g,p in build),'residents_scenario':3600,'jobs_scenario':1500,'interfaces':len(cross),'buildings':len(build),'people_path_building_conflict_m':sum(g.intersection(unary_union([b for b,bp in build if bp.get('form')!='canopy'])).length for g,mp in moves if mp.get('network')=='people'),'building_fixed_overlap_m2':sum(g.intersection(fixed).area for g,p in build),'building_channel_screen_overlap_m2':sum(g.intersection(channels.buffer(150)).area for g,p in build),'building_flood_screen_overlap_m2':sum(g.intersection(flood).area for g,p in build),'land_partition_gap_m2':master.difference(unary_union([transform(t,shape(f['geometry'])) for f in land_features])).area,'regional_links':[f['properties'] for f in regional],'limits':['300m regional route grid; 60m terrain is not engineering','No secured water, grid or external access rights','A/B/C IDs requested by human; organiser checker still expects old numbering; no compatibility aliases included','Not submitted; not independent design approval']}
(P/'report/geometry-qa.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2))
