"""Compact the southwest works, reallocate existing PV/crops, and remove the unresolved gap."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image
from shapely.geometry import shape,mapping,box,LineString,Point
from shapely.affinity import translate
from shapely.ops import transform,unary_union
from shapely import contains_xy
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];G=P/'geometry';O=P/'reviews/compact-v5';O.mkdir(exist_ok=True);A=O/'before';A.mkdir(exist_ok=True);DY=1050
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
for name in ['geometry','drawings']:
 if not (A/name).exists():shutil.copytree(P/name,A/name)
for name in ['manifest.json','proposal.md','image_provenance.json','reviews/redesign-v2/design-account.json','reviews/redesign-v2/module-positions.geojson']:
 target=A/name;target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copy2(P/name,target)
load=lambda f:[(transform(T,shape(x['geometry'])),dict(x['properties'])) for x in json.loads(f.read_text())['features']]
def write(path,items):
 def encode(g):
  q=transform(I,g)
  if q.geom_type in ['Polygon','MultiPolygon'] and not q.is_valid:q=q.buffer(0)
  return mapping(q)
 path.write_text(json.dumps(dict(type='FeatureCollection',features=[dict(type='Feature',geometry=encode(g),properties=p) for g,p in items]),separators=(',',':'))+'\n')
# Local housing/civic buildings stay exactly where they were. Production and farm move as one system.
bld=[]
for g,p in load(A/'geometry/buildings.geojson'):
 if p['id'].startswith('U-'):g=translate(g,xoff=-450,yoff=1250)
 elif not p['id'].startswith(('WEST-','EAST-','NORTH-','CENTRE-')):g=translate(g,yoff=DY)
 bld.append((g,p))
# Preserve all62 main solar rows and their total line length, redistribute52 north +10 west.
oldassets=load(A/'geometry/assets.geojson');mainrows=[(g,p) for g,p in oldassets if p.get('type')=='pv_row' and not p['id'].startswith('F-PV')];assert len(mainrows)==62
positions=[]
for y in range(6554000,6554241,20):
 for x in [573420,573980,574540,575100]:positions.append(LineString([(x,y),(x+540,y)]))
for y in range(6553010,6553191,20):positions.append(LineString([(573380,y),(573920,y)]))
rowmap={p['id']:(g,positions[i]) for i,(g,p) in enumerate(mainrows)}
assets=[]
for g,p in oldassets:
 id=p.get('id','')
 if id in rowmap:g=rowmap[id][1];p['field_block']='NORTH' if g.centroid.y>6553900 else 'WEST'
 elif id.startswith('DRIP-') and id[5:] in rowmap:g=rowmap[id[5:]][1]
 else:g=translate(g,yoff=DY)
 assets.append((g,p))
crops=[]
for g,p in load(A/'geometry/crops.geojson'):
 row=p['id'][5:]
 if row in rowmap:
  old,new=rowmap[row];g=translate(g,xoff=new.centroid.x-old.centroid.x,yoff=new.centroid.y-old.centroid.y);p['field_block']='NORTH' if new.centroid.y>6553900 else 'WEST'
 else:g=translate(g,yoff=DY)
 crops.append((g,p))
# The former1.56km2 gross works estate shrinks to0.60km2, retaining0.35km2 active campus.
active=box(574100,6553200,574600,6553900);gross=box(574000,6553150,574750,6553950)
solar=box(573400,6553980,575640,6554260).union(box(573350,6553000,573950,6553200))
land=[]
for g,p in load(A/'geometry/land_use.geojson'):
 id=p['id']
 if id=='P-WORKS':g=active
 elif id=='P-FUTURE-RESERVE':g=gross.difference(active);p.update(name='Compact unserviced reserve, no additional capacity',capacity_basis='0.25km2 future reserve; no added IT MW, people or jobs')
 elif id=='P-SOLAR':g=solar;p.update(name='North productive interface and west solar field',capacity_basis='62 existing proposed540m rows redistributed; unchanged26.784MWp scenario and crop-net area')
 elif id=='P-UTILITY':g=translate(g,xoff=-450,yoff=1250).difference(next(q for q,v in load(A/'geometry/structure.geojson') if v['id']=='D07'))
 elif id=='F-LEARNING':g=translate(g,yoff=DY)
 land.append((g,p))
# Selected nodes and internal module positions keep IDs/phases, move with their buildings.
nodes=[]
for g,p in load(A/'geometry/nodes.geojson'):
 if p['node_id']=='B03':g=gross;p['role']='Compact shared campus and0.25km2 unserviced reserve;400m active/town edge separation'
 elif p['node_id']=='C02':g=translate(g,yoff=DY)
 nodes.append((g,p))
roads=[]
for g,p in load(A/'geometry/movement.geojson'):
 if g.geom_type=='Point':continue
 id=p.get('id','')
 if id.startswith(('P-','F-')):g=translate(g,yoff=DY)
 if id=='SW-PUBLIC-SPINE':g=LineString([(573400,6554300),(573200,6554300),(573200,6552750),(573050,6552600)])
 if id=='SW-SERVICE-SPINE':g=LineString([(575800,6554300),(575800,6552750),(575150,6553000)])
 if id=='SOUTH-CONNECTOR':g=LineString([(573200,6552750),(575800,6552750)])
 if id=='P-WORKER-BUS-LINK':g=LineString([(573200,6553955),(574050,6553955),(574050,6553850),(574120,6553850)])
 if id=='P-COMPACT-FREIGHT-APPROACH':g=LineString([(575800,6552750),(574780,6552750),(574780,6553220),(574580,6553220)])
 if id=='SW-ARRIVAL-LINK':
  first=list(g.coords)[0];g=LineString([first,(572500,6551700),(573050,6552600)])
 if id=='PILOT-EDGE-STUDY':g=LineString([(573050,6552600),list(g.coords)[-1]])
 if id=='REGIONAL-0':
  coords=list(g.coords);keep=next(i for i,v in enumerate(coords) if v[1]>=6554523);g=LineString([(573200,6554300)]+coords[keep:]);p['basis']='V5 joins town-west arrival directly to retained regional terrain corridor; no loop back into the former vacant strip.'
 roads.append((g,p))
# The public route remains outside the solar/electrical fields. New access is explicitly drawn.
roads.append((LineString([(573200,6552990),(573350,6552990)]),dict(id='V5-WEST-FIELD-ACCESS',name='West-field maintenance access',network='machine',road_class='local',width_m=10,phase=1,shaded=False,status='proposed_service_route')))
# No lawns/forest or invented drainage added to make a photograph look occupied.
surfaces=[(translate(g,yoff=DY),p) for g,p in load(A/'geometry/courtyard_details.geojson')]
interstice=[(box(573400,6554260,575640,6554290),dict(id='V5-TOWN-EDGE',name='Dry town-edge inspection verge',use='dry_verge',basis='30m entrant reservation; no planting/irrigation credit')),(box(573400,6553950,575640,6553980),dict(id='V5-FIELD-SERVICE',name='Farm/service interface corridor',use='service_corridor',basis='30m concept reservation for access/isolated utilities; public bus link drawn within it'))]
for n,v in [('buildings',bld),('assets',assets),('crops',crops),('land_use',land),('nodes',nodes),('movement',roads),('courtyard_details',surfaces),('interface_landscape',interstice)]:write(G/(n+'.geojson'),v)
master=unary_union([g for g,p in land]);write(G/'master_area.geojson',[(master,dict(name='V5 complete town and compact associated works',basis='Union of actual detailed land-use units, not a camera frame'))])
modules=[(translate(g,yoff=DY),p) for g,p in load(A/'reviews/redesign-v2/module-positions.geojson')];write(P/'reviews/redesign-v2/module-positions.geojson',modules)
# Map phases from the current exclusive detailed parcels rather than translating an old outline.
phased=[]
for phase in [1,2,3]:
 q=unary_union([g for g,p in land if p['phase']==phase]);phased.append((q,dict(id='PHASE-'+str(phase),phase=phase,name='Phase '+str(phase)+' land release',basis='Current detailed land-use phase union; no regional reserve capacity invented')))
write(G/'phasing.geojson',phased)
# Reconcile territorial roles at the changed local interfaces. Rest of V4 stays intact.
rs=load(A/'geometry/structure.geojson');newlocal=unary_union([g for g,p in land]);local_by={'living':unary_union([g for g,p in land if p.get('district') in ['WEST','EAST','NORTH','CENTRE','TOWN']]),'agri_production':unary_union([g for g,p in land if p['id']=='F-LEARNING']),'energy_compute':unary_union([g for g,p in land if p.get('district')=='WORKS'])}
fixed=unary_union([g for file in ['pilot_area.geojson','pilot_living_area.geojson'] for g,p in load(R/'brief/site-package/pilot-area'/file)]);scope=unary_union([g for g,p in load(R/'brief/site-package/boundaries/scope_9_13.geojson')]);ch=unary_union([g for g,p in load(R/'brief/site-package/water/channels_dem.geojson')]);screen=ch.buffer(150)
assert all(g.intersection(fixed).area<.01 for g,p in bld);assert all(scope.buffer(.01).covers(g) for g,p in bld)
assert all(g.intersection(screen).area<.01 for g,p in bld),[(p['id'],g.intersection(screen).area) for g,p in bld if g.intersection(screen).area>.01]
base=[]
for g,p in rs:
 if p['plan_role']!='base_zoning':continue
 if p['id'] in ['D01','D02','D03-S']:
  g=g.difference(newlocal)
  key={'D01':'living','D02':'agri_production','D03-S':'energy_compute'}[p['id']];g=g.union(local_by[key]);p['area_km2']=g.area/1e6
 base.append((g.buffer(0),p))
# New local patches may have touched other strategic base units; excise only actual patches not their enclosing bbox.
for i,(g,p) in enumerate(base):
 if p['id'] not in ['D01','D02','D03-S']:base[i]=(g.difference(newlocal).buffer(0),p)
by={p['id']:g for g,p in base};energy=unary_union([g for g,p in base if p['id'].startswith('D03')]);ag=by['D02'].union(by['D00-F']);dualold=next(g for g,p in rs if p.get('id')=='F-energy_compute').intersection(next(g for g,p in rs if p.get('id')=='F-agri_production'));du=dualold.difference(newlocal).union(local_by['agri_production'])
coverage=dict(energy_compute=energy.union(du),agri_production=ag,living=by['D01'].union(by['D00-L']),industry=by['D04'],port=by['D05-W'].union(by['D05-E']))
for key,g in coverage.items():base.append((g.buffer(0),dict(id='F-'+key,district_id='F-'+key,name='Functional coverage / '+key,primary_use='functional_coverage',system=key,plan_role='system_overlay',basis_ref='proposal.md#territorial-districts',edge_logic='V4 strategic coverage with V5 local interfaces coordinated; not installed area',area_km2=g.area/1e6)))
write(G/'structure.geojson',base)
# Ground stats and geometry checks, not universal separation standards.
dem=np.asarray(Image.open(R/'brief/site-package/terrain/dem_9_13_utm19s_60m.png'),dtype=float);sy,sx=np.gradient(dem,60);sl=np.hypot(sx,sy)*100;xs=559572.4+(np.arange(dem.shape[1])+.5)*60;ys=6608973.7-(np.arange(dem.shape[0])+.5)*60
X,Y=np.meshgrid(xs,ys)
def stats(g):
 vals=sl[contains_xy(g,X,Y)];return dict(median_slope_pct=float(np.median(vals)),p95_slope_pct=float(np.percentile(vals,95)))
conf=[]
for g,p in roads:
 for b,v in bld:
  if v.get('form')!='canopy' and g.intersection(b).length>1:conf.append([p['id'],v['id'],g.intersection(b).length])
assert not conf,conf
qa=json.loads((A/'reviews/redesign-v2/design-account.json').read_text());qa.update(master_km2=master.area/1e6,active_compute_campus_km2=.35,productive_gross_estate_km2=.6,unserviced_productive_reserve_km2=.25,town_to_compute_edge_m=350,town_to_active_compute_edge_m=400,productive_ground_screen=stats(gross),regions=[p for g,p in base if p['plan_role']=='base_zoning'],land_use_km2={u:sum(g.area for g,p in land if p['use']==u)/1e6 for u in set(p['use'] for g,p in land)})
(P/'reviews/redesign-v2/design-account.json').write_text(json.dumps(qa,indent=2));audit=dict(shift_north_m=DY,gross_campus_km2=.6,active_campus_km2=.35,reserve_km2=.25,former_gross_campus_km2=1.56,town_gross_edge_gap_m=350,town_active_edge_gap_m=400,main_pv_rows=62,main_pv_line_m=sum(g.length for g,p in assets if p.get('type')=='pv_row' and not p['id'].startswith('F-PV')),crop_ha=sum(g.area for g,p in crops)/1e4,crop_water_m3y=sum(g.area/1e4*p['annual_irrigation_m3_ha_assumed'] for g,p in crops),new_solar_gross_km2=solar.area/1e6,productive_ground=stats(gross),road_building_conflicts=conf,building_channel_buffer_overlap_m2=sum(g.intersection(screen).area for g,p in bld),claim='Distances are entrant compact-layout choices, not certified noise/fire/thermal buffers. No new housing, jobs, IT MW, panel line length or crop area is created.');(O/'design-changes.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
