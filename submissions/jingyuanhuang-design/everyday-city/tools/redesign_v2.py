"""Everyday City V2: one complete town, independent productive estate and territorial districts."""
import json,math,sys,shutil,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from shapely import make_valid,contains_xy
from shapely.geometry import shape,mapping,box,Point,LineString,Polygon
from shapely.ops import transform,unary_union,nearest_points
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=R/'brief/site-package';O=P/'reviews/redesign-v2';G=P/'geometry';O.mkdir(parents=True,exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda p:[(make_valid(transform(T,shape(f['geometry']))),f['properties']) for f in json.loads(p.read_text())['features']]
U=lambda p:unary_union([g for g,v in load(p)])
scope=U(S/'boundaries/scope_9_13.geojson');pilot=U(S/'pilot-area/pilot_area.geojson');living=U(S/'pilot-area/pilot_living_area.geojson');fixed=pilot.union(living);channels=U(S/'water/channels_dem.geojson');flood=U(S/'water/flood_sensitive_dem.geojson');screen=channels.buffer(150)
# Preserve the version that was displayed, without presenting it as a recommended exemplar.
archive=P/'reviews/withdrawn-v1'
if not archive.exists():
 archive.mkdir()
 for n in ['geometry','drawings']:shutil.copytree(P/n,archive/n)
 for n in ['manifest.json','proposal.md','image_provenance.json','metrics.json']:shutil.copy2(P/n,archive/n)
 (archive/'STATUS.md').write_text('Withdrawn from recommendation. Original public preview retained for traceability; no design approval. Replaced by V2 complete-city redesign.\n')
dem=np.asarray(Image.open(S/'terrain/dem_9_13_utm19s_60m.png'),dtype=float);dy,dx=np.gradient(dem,60);slope=np.hypot(dx,dy)*100;xs=559572.4+(np.arange(dem.shape[1])+.5)*60;ys=6608973.7-(np.arange(dem.shape[0])+.5)*60

def stats(g):
 x0,y0,x1,y1=g.bounds;r=(ys>=y0)&(ys<=y1);c=(xs>=x0)&(xs<=x1);X,Y=np.meshgrid(xs[c],ys[r]);v=slope[np.ix_(r,c)][contains_xy(g,X,Y)];return dict(median_slope_pct=round(float(np.median(v)),2),p95_slope_pct=round(float(np.percentile(v,95)),2)) if len(v) else {}
def ft(g,**p):return dict(type='Feature',geometry=mapping(transform(I,make_valid(g))),properties=p)
def write(path,items):path.write_text(json.dumps(dict(type='FeatureCollection',features=[ft(g,**p) for g,p in items]),separators=(',',':'))+'\n')
build=[];land=[];roads=[];assets=[];nodes=[];districts=[]
def bld(g,id,use,phase,floors=1,homes=0,jobs=0,**kw):
 assert scope.covers(g),(id,'scope');assert g.intersection(fixed).area<.01,(id,'pilot');assert g.intersection(screen).area<.01,(id,'channel')
 build.append((g,dict(id=id,name=id,use=use,phase=phase,floors=floors,height_m=(10 if use=='compute' else 6 if use=='industry' else 4.2 if kw.get('form')=='canopy' else floors*3.2),dwellings=homes,jobs=jobs,**kw)))
def unit(g,id,use,phase,district,**kw):land.append((g,dict(id=id,name=id,use=use,phase=phase,district=district,**kw)))
def road(g,id,network='shared',hier='local',width=18,phase=1,**kw):roads.append((g,dict(id=id,name=id,network=network,road_class=hier,width_m=width,phase=phase,shaded=False,**kw)))
x0,y0=573400,6554300;town=box(x0,y0,x0+2400,y0+2400).intersection(scope).difference(fixed)
# Reserve a 200m civic band, a continuous north-south dry commons, and distributed services before housing.
for i in range(13):
 xx=x0+i*200
 for low,high,ph in [(0,1200,1 if i<=6 else 2),(1200,2400,3)]:road(LineString([(xx,y0+low),(xx,y0+high)]),f'T-NS-{i}-P{ph}',hier='secondary' if i in [0,6,12] else 'local',width=28 if i==6 else 20,phase=ph)
for j in range(13):
 yy=y0+j*200
 for left,right,ph in [(0,1200,1 if j<=6 else 3),(1200,2400,2 if j<=6 else 3)]:road(LineString([(x0+left,yy),(x0+right,yy)]),f'T-EW-{j}-{left}',hier='primary' if j==6 else ('secondary' if j in [0,12] else 'local'),width=32 if j==6 else 20,phase=ph)
streetland=unary_union([g.buffer(p['width_m']/2,cap_style=2) for g,p in roads]).intersection(town)
services={(2,2):'school',(9,2):'school',(2,9):'school',(9,9):'school',(2,7):'school',(9,7):'school',(3,3):'daily_centre',(8,3):'daily_centre',(3,10):'daily_centre',(8,10):'daily_centre',(1,1):'dry_park',(10,1):'dry_park',(1,10):'dry_park',(10,10):'dry_park'}
counts={};schoolplaces={};resblocks=[]
for j in range(12):
 for i in range(12):
  ph=1 if j<6 and i<6 else (2 if j<6 else 3);dist='WEST' if j<6 and i<6 else ('EAST' if j<6 else 'NORTH');id=f'{dist}-{j:02}-{i:02}';g=box(x0+i*200+16,y0+j*200+16,x0+(i+1)*200-16,y0+(j+1)*200-16);cx,cy=g.centroid.coords[0]
  use='civic' if j==5 else ('dry_park' if i==5 else services.get((i,j),'residential'))
  st=stats(g)
  if use=='residential' and (st.get('p95_slope_pct',0)>8 or g.intersection(flood).area>1):use='terrain_review'
  unit(g,id,use,ph,dist,**st)
  if use=='residential':
   # Four separate low-rise bars around an open court; 2-storey terraces in alternate blocks.
   typ='court_bars' if (i+j)%3 else 'terrace_lanes';n=0
   if typ=='court_bars':
    for k,(a,b,w,h) in enumerate([(-65,-65,130,12),(-65,53,130,12),(-65,-40,12,80),(53,-40,12,80)]):
     homes=30 if k<2 else 18;bld(box(cx+a,cy+b,cx+a+w,cy+b+h),id+f'-B{k}','residential',ph,3,homes=homes,typology=typ);n+=homes
    bld(box(cx-40,cy-4,cx+40,cy+2),id+'-court-shade','civic',ph,form='canopy',height_override_m=3.8)
   else:
    for k in range(4):
     xx=cx-65+k*35;bld(box(xx,cy-55,xx+12,cy+55),id+f'-T{k}','residential',ph,2,homes=12,typology=typ);n+=12
   resblocks.append((g,dict(id=id,phase=ph,dwellings=n,district=dist,typology=typ)));counts[ph]=counts.get(ph,0)+n
  elif use=='school':
   for k in range(2):bld(box(cx-64,cy-58+k*38,cx+64,cy-42+k*38),id+f'-school-{k}','civic',ph,2,jobs=25)
   schoolplaces[id]=750 if ph in [1,2] else 400
  elif use=='daily_centre':
   bld(box(cx-60,cy-48,cx+60,cy-25),id+'-health-care','civic',ph,2,jobs=45);bld(box(cx-60,cy+25,cx+60,cy+48),id+'-shops','mixed_use',ph,2,jobs=60)
  elif use=='civic':
   role=['sports','market','library','health','workspaces','commons'][i%6]
   if i%6!=5:
    bld(box(cx-65,cy-52,cx+65,cy-29),id+'-'+role,'mixed_use' if role in ['market','workspaces'] else 'civic',ph,2,jobs=70)
    bld(box(cx-65,cy+29,cx+65,cy+52),id+'-hall','civic',ph,2,jobs=30)
   bld(box(cx-60,cy-2,cx+60,cy+4),id+'-public-shade','civic',ph,form='canopy')
# Exclusive territorial unit not street+park leftover double count.
used=unary_union([g for g,p in land]);left=streetland;verges=town.difference(used.union(streetland))
for ph,mask in [(1,box(x0,y0,x0+1200,y0+1200)),(2,box(x0+1200,y0,x0+2400,y0+1200)),(3,box(x0,y0+1200,x0+2400,y0+2400))]:
 unit(left.intersection(mask),f'TOWN-STREETS-P{ph}','infrastructure',ph,'TOWN');unit(verges.intersection(mask),f'TOWN-VERGES-P{ph}','open_space',ph,'TOWN')
# Three coherent neighbourhoods and a civic band, not compute among homes.
for name,g,ph in [('WEST',box(x0,y0,x0+1200,y0+1000),1),('EAST',box(x0+1200,y0,x0+2400,y0+1000),2),('NORTH',box(x0,y0+1200,x0+2400,y0+2400),3),('CENTRE',box(x0,y0+1000,x0+2400,y0+1200),1)]:districts.append((g.intersection(town),dict(id=name,name=name.title()+' district',phase=ph)))
# Productive campus is 1.1km south of the town, served from an independent perimeter road.
prod=box(574000,6551900,575200,6553200);unit(prod,'P-WORKS','compute',1,'WORKS')
for j in range(2):
 for i in range(2):
  xx,yy=574100+i*470,6552050+j*480;ph=1 if j==0 else (2 if i==0 else 3);bld(box(xx,yy,xx+300,yy+100),f'P-HALL-{j}-{i}','compute',ph,jobs=30,it_mw=2)
for i in range(4):bld(box(574100+i*250,6553100,574280+i*250,6553130),f'P-REPAIR-{i}','industry',1 if i<2 else 2,jobs=45)
# Local drying/testing shed is the only proposed heat recipient; demand must be metered before connection.
bld(box(575000,6552800,575140,6552850),'P-DRYING-TEST','industry',2,jobs=30)
bld(box(574080,6552300,575100,6552306),'P-WORKER-SHADE','civic',1,form='canopy')
road(LineString([(574050,6551950),(575150,6551950),(575150,6553150),(574050,6553150),(574050,6551950)]),'P-FREIGHT-LOOP','machine','secondary',24)
road(LineString([(574050,6552315),(575150,6552315)]),'P-WORKER-ROUTE','people','local',4)
for xx in [574250,574720]:
 for yy in [6552050,6552530]:road(LineString([(xx,6551950 if yy==6552050 else 6553150),(xx,yy+50)]),f'P-SPUR-{xx}-{yy}','machine','local',16)
solar=box(573350,6551900,573950,6553200);unit(solar,'P-SOLAR','energy',1,'WORKS')
for y in np.arange(6551950,6553180,20):assets.append((LineString([(573380,y),(573920,y)]),dict(type='pv_row',id=f'PV-{y}',phase=1)))
util=box(575250,6551900,575550,6552350);unit(util,'P-UTILITY','infrastructure',1,'WORKS')
for i in range(3):bld(box(575280,6551950+i*120,575500,6552000+i*120),f'U-{i}','infrastructure',1,jobs=10)
# Farm-edge campus is NEW land outside both fixed pilots; fixed fields are not replanted.
farm=box(573000,6551100,573800,6551600);assert not farm.intersects(fixed);unit(farm,'F-LEARNING','agriculture',1,'FARM')
for i in range(2):bld(box(573100+i*300,6551400,573300+i*300,6551430),f'F-TRAINING-{i}','industry',1,jobs=35)
bld(box(573080,6551310,573720,6551316),'F-PUBLIC-SHADE','civic',1,form='canopy')
for y in np.arange(6551140,6551280,18):assets.append((LineString([(573100,y),(573700,y)]),dict(type='pv_row',id=f'F-PV-{y}',phase=1,trial_only=True)))
road(LineString([(573050,6551550),(573750,6551550),(573750,6551120)]),'F-FARM-SERVICE','machine','secondary',18)
road(LineString([(573080,6551325),(573720,6551325)]),'F-VISITOR-PROMENADE','people','local',4)
# Parallel public/service approaches with a named controlled arrival, no secured external road claim.
road(LineString([(573400,6554300),(573200,6553600),(573200,6551700),(573050,6551550)]),'SW-PUBLIC-SPINE',hier='primary',width=28)
road(LineString([(575800,6554300),(575800,6551700),(575150,6551950)]),'SW-SERVICE-SPINE','machine','primary',26)
road(LineString([(573200,6553200),(574050,6553200),(574050,6553150)]),'P-WORKER-BUS-LINK',hier='secondary',width=24)
road(LineString([(573200,6551700),(575800,6551700)]),'SOUTH-CONNECTOR',hier='secondary',width=24)
# Public walk along the actual street and engineered shade opportunity, not installed forest.
for xx in [x0+400,x0+1200,x0+2000]:road(LineString([(xx+7,y0+40),(xx+7,y0+2360)]),f'T-WALK-{xx}','people','local',4,shade_intent=True)
# Exact representative nodes. Full city extent is larger than every node crop.
A=next((g,p) for g,p in resblocks if p['phase']==1 and p['typology']=='court_bars' and g.centroid.distance(Point(x0+700,y0+500))<180)
nodes=[(A[0].buffer(25),dict(node_id='A01',name='Open-court homes',phase=1,role='Housing and shared everyday ground')),(prod,dict(node_id='B03',name='Independent compute and repair campus',phase=1,role='Staged production; short local heat trial only')),(farm,dict(node_id='C02',name='Farm learning edge',phase=1,role='New trial interface outside fixed pilots'))]
# Territorial district edges are explicit design choices following the SW access basin, a proposed transfer axis,
# the north shoulder and SE terrain reserve. They do not assert statutory ownership or development rights.
remaining=scope;regions=[]
def region(g,id,name,use,system,logic):
 global remaining
 q=make_valid(g.intersection(remaining));remaining=remaining.difference(q)
 if not q.is_empty:regions.append((q,dict(id=id,district_id=id,name=name,primary_use=use,system=system,plan_role='base_zoning',basis_ref='proposal.md#territorial-districts',edge_logic=logic,area_km2=q.area/1e6)))
region(pilot,'D00-F','Fixed agrivoltaic pilot','fixed_context','agri_production','Exact issued fixed boundary; unchanged')
region(living,'D00-L','Fixed living pilot','fixed_context','living','Exact issued fixed boundary; no internal redesign')
# Source-derived mountain study retained from prior site reading, explicitly attributed, not copied urban geometry.
old=load(archive/'geometry/structure.geojson');mount=unary_union([g for g,p in old if 'Mountain and steep' in p.get('name','')]);region(mount,'D07','Mountain stewardship','ecology','reserve','Source DEM steep/high terrain; preliminary conservation study, not statutory exclusion')
region(Polygon([(559000,6540000),(582000,6540000),(579000,6560000),(571800,6561000),(559000,6561000)]),'D01','Southwest settlement and farm services','mixed_use','living','SW access basin; northeastern edge is a declared urban service limit, not a built-up boundary')
region(Polygon([(550000,6559000),(572000,6560000),(581000,6574000),(581500,6600000),(550000,6615000)]),'D02','Western dry agriculture research','agriculture','agri_production','Western fan and seasonal drainage system; testing sites only after water/soil verification')
region(Polygon([(581500,6580000),(590000,6580500),(601000,6608000),(575000,6620000)]),'D03','Northern energy research','solar_agriculture','energy_compute','North shoulder north of proposed research access; no installed full-district PV claim')
region(Polygon([(577000,6558000),(589000,6557000),(603000,6571500),(597000,6584000),(581500,6580000)]),'D04','Central production and transfer','industry','energy_compute','Transfer-corridor operating basin; no residential capacity credited')
region(Polygon([(594000,6560000),(631000,6550000),(634000,6588000),(603000,6586000)]),'D05','Eastern gateway and logistics','logistics','port','Eastern access/transfer study outside mountain reserve; external connection unsecured')
region(remaining,'D06','Dry landscape and field-service links','reserve','reserve','Remaining seasonal-drainage links and unresolved terrain; explicit landscape/research role, not a lake')
# Reuse credited terrain-routed regional studies, connecting the old SW endpoint to the new town access.
regional=load(P/'report/regional-corridors.geojson')
for k,(g,p) in enumerate(regional):
 if p['name'].startswith('Fixed'):continue
 road(g.intersection(scope).difference(fixed),f'REGIONAL-{k}',hier='primary' if k in [0,2] else 'secondary',width=30,phase=p['phase'],study_only=True,secured=False,source_ref='reviews/withdrawn-v1; original terrain-cost study retained')
road(LineString([(574400,6552200),(575800,6553500),(575800,6554300)]),'REGIONAL-TOWN-JOIN',hier='secondary',width=24,phase=2,study_only=True,secured=False)
# A real pilot connection is a study to its edge, never an internal pilot redesign.
contact=nearest_points(fixed,Point(573050,6551550))[0];pilotlink=LineString([(573050,6551550),(contact.x,contact.y)]).difference(fixed).intersection(scope);road(pilotlink,'PILOT-EDGE-STUDY',hier='secondary',width=18,study_only=True,secured=False)
master=unary_union([town,prod,solar,util,farm])
for name,items in [('structure',regions),('master_area',[(master,dict(name='Complete all-phase town and associated campuses'))]),('land_use',land),('buildings',build),('movement',roads),('nodes',nodes),('assets',assets)]:write(G/(name+'.geojson'),items)
write(O/'districts.geojson',districts);write(O/'residential-blocks.geojson',resblocks)
phases=[];programme=[]
for ph in [1,2,3]:
 bg=[(g,p) for g,p in build if p['phase']==ph];homes=sum(p['dwellings'] for g,p in bg);jobs=sum(p['jobs'] for g,p in bg);polys=[g for g,p in land if p['phase']==ph];phases.append((unary_union(polys),dict(phase=ph,name=f'P{ph}',trigger='Verified access, fresh water, power, funded services and detailed ground design before occupation')))
 programme.append(dict(phase=ph,new_dwellings=homes,cumulative_dwellings=sum(p['dwellings'] for g,p in build if p['phase']<=ph),new_residents=homes*2.5,cumulative_residents=sum(p['dwellings']*2.5 for g,p in build if p['phase']<=ph),new_jobs=jobs,cumulative_jobs=sum(p['jobs'] for g,p in build if p['phase']<=ph),period={1:'Years 0-5 scenario',2:'Years 5-10 conditional',3:'Years 10-20 conditional'}[ph],objective={1:'Complete western neighbourhood, civic core, utilities and first productive halls',2:'Eastern living district and additional productive capacity',3:'Northern neighbourhoods and final staged halls'}[ph],works=['Homes, school, care, shops, access and utilities before occupancy'],sequence_dependencies=['Lawful external access and water/power rights','First occupied phase independently funded'],trigger='Demand, operating budget and audited resource margin verified; no calendar-only expansion',basis='computed building inventory; assumed 2.5 residents per dwelling'))
write(G/'phasing.geojson',phases)
# Register real public/machine crossing coordinates; no automatic guarantee of safe junction design.
cross=[]
for a,pa in roads:
 if pa['network']!='people':continue
 for b,pb in roads:
  if pb['network'] not in ['machine','shared']:continue
  g=a.intersection(b)
  for q in [g] if g.geom_type=='Point' else getattr(g,'geoms',[]):
   if q.geom_type=='Point' and all(q.distance(v)>1 for v in cross):cross.append(q)
write(G/'interfaces.geojson',[(q,dict(kind='interface',name='Proposed controlled crossing',rule='Pedestrian priority, machine stop, interlock/manual release; detailed design required')) for q in cross])
qa=dict(source_boundary='brief/site-package/boundaries/scope_9_13.geojson',whole_site_km2=scope.area/1e6,master_km2=master.area/1e6,town_km2=town.area/1e6,dwellings=sum(p['dwellings'] for g,p in build),residents=sum(p['dwellings']*2.5 for g,p in build),jobs=sum(p['jobs'] for g,p in build),housing_blocks=len(resblocks),school_places=sum(schoolplaces.values()),building_fixed_overlap_m2=sum(g.intersection(fixed).area for g,p in build),building_channel_screen_overlap_m2=sum(g.intersection(screen).area for g,p in build),building_flood_screen_overlap_m2=sum(g.intersection(flood).area for g,p in build),base_gap_m2=scope.difference(unary_union([g for g,p in regions])).area,base_overlap_m2=sum(g.area for g,p in regions)-unary_union([g for g,p in regions]).area,town_ground_screen=stats(town),productive_ground_screen=stats(prod),town_to_compute_edge_m=town.distance(prod),interfaces=len(cross),school_capacity_basis='Two southern schools x 750 places plus four northern schools x 400; assumed, need 15% of population; demographics/funding review required',land_partition_gap_m2=master.difference(unary_union([g for g,p in land])).area,programme=programme,regions=[p for g,p in regions],land_use_km2={u:sum(g.area for g,p in land if p['use']==u)/1e6 for u in set(p['use'] for g,p in land)})
(O/'design-account.json').write_text(json.dumps(qa,indent=2));(P/'phasing_programme.json').write_text(json.dumps(dict(schema_version=1,status='declared_scenario_not_approved',phases=programme),indent=2));print(json.dumps({k:v for k,v in qa.items() if k not in ['programme','regions','land_use_km2']},indent=2))
