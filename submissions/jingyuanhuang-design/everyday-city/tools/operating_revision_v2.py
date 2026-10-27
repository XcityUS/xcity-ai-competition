"""Apply the latest modular-campus and agrivoltaic operating brief without changing town capacity."""
import json,sys
from pathlib import Path
from shapely.geometry import shape,mapping,box,LineString
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];G=P/'geometry';O=P/'reviews/redesign-v2';T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:[(transform(T,shape(v['geometry'])),v['properties']) for v in json.loads(f.read_text())['features']]
def ft(g,p):return dict(type='Feature',geometry=mapping(transform(I,g)),properties=p)
def write(f,items):f.write_text(json.dumps(dict(type='FeatureCollection',features=[ft(g,p) for g,p in items]),separators=(',',':'))+'\n')
b=load(G/'buildings.geojson');land=load(G/'land_use.geojson');roads=load(G/'movement.geojson');assets=load(G/'assets.geojson');active=box(574100,6552150,574600,6552850);gross=box(574000,6551900,575200,6553200)
new=[];pods=[]
for g,p in b:
 id=p['id']
 if id.startswith('P-HALL'):
  j,i=map(int,id.split('-')[-2:]);xx=574170+i*130;yy=6552300+j*100;g=box(xx,yy,xx+80,yy+40);p.update(height_m=8,form='',modular_positions=8,operating_it_mw=2,rack_nameplate_mw=2.688,power_block_nameplate_mw=8,alternative_basis='Covered modular-service group; 8 conceptual dual-container positions at assumed250kW operating IT each. XPOD reference rack-nameplate sum336kW is not an operating guarantee; 1MW power-block rating is not IT.')
  for rr in range(2):
   for cc in range(4):
    q=box(xx+7+cc*18,yy+7+rr*18,xx+19.2+cc*18,yy+13+rr*18);pods.append((q,dict(id=id+f'-POS-{rr}-{cc}',type='conceptual_dual_container_position',phase=p['phase'],assumed_length_m=12.2,assumed_width_m=6,operating_it_kw=250,reference_rack_nameplate_kw=336,power_block_nameplate_kw=1000,reference='https://xcity.ai/computepod',status='conceptual_position_not_certified_vendor_layout')))
 elif id.startswith('P-REPAIR'):
  i=int(id.split('-')[-1]);g=box(574140+i*105,6552740,574220+i*105,6552765);p['height_m']=6
 elif id=='P-DRYING-TEST':g=box(574450,6552630,574550,6552660);p.update(height_m=6)
 elif id=='P-WORKER-SHADE':g=box(574135,6552370,574550,6552376);p.update(height_m=4.2)
 new.append((g,p))
# Small shared service structures and equipment pads, not duplicate XPOD integrated power rooms.
new=[(g,p) for g,p in new if not p['id'].startswith('P-SHARED-')]
for id,g,h in [('P-SHARED-FIBRE-SECURITY',box(574160,6552780,574200,6552800),4),('P-SHARED-MGRID',box(574470,6552200,574520,6552220),4),('P-SHARED-DRY-REJECTION',box(574470,6552300,574510,6552340).union(box(574470,6552400,574510,6552440)),3)]:new.append((g,dict(id=id,name=id,use='infrastructure',phase=1,floors=1,height_m=h,dwellings=0,jobs=0,equipment_only=True,capacity_basis='Site shared interface / no additional staffed jobs or approved equipment capacity')))
# Former oversize plot becomes explicitly unserviced future land, with no installed capacity credit.
ll=[]
for g,p in land:
 if p.get('id')=='P-WORKS':
  pp=dict(p);pp.update(name='Compact serviced modular campus',use='compute',programme_use='compute');ll.append((active,pp));pp=dict(p);pp.update(id='P-FUTURE-RESERVE',name='Unserviced productive estate reserve / no capacity',use='reserve',programme_use='reserve',phase=3,capacity_basis='No additional IT, homes or jobs credited');ll.append((gross.difference(active),pp))
 else:ll.append((g,p))
# Public approach and construction/freight routes meet distinct campus gates.
rr=[(g,p) for g,p in roads if not (p.get('id','').startswith('P-SPUR') or p.get('id') in ['P-FREIGHT-LOOP','P-WORKER-ROUTE','P-WORKER-BUS-LINK'] or p.get('id','').startswith('P-COMPACT') or p.get('id','').startswith('P-DELIVERY') or g.geom_type=='Point')]
def road(g,id,net,hier='local',width=12,phase=1):rr.append((g,dict(id=id,name=id,network=net,road_class=hier,width_m=width,phase=phase,shaded=False,compact_revision=True)))
road(LineString([(574120,6552170),(574580,6552170),(574580,6552820),(574120,6552820),(574120,6552170)]),'P-COMPACT-SERVICE-LOOP','machine','secondary',18)
road(LineString([(575150,6551950),(575150,6552100),(574580,6552100),(574580,6552170)]),'P-COMPACT-FREIGHT-APPROACH','machine','secondary',20)
road(LineString([(573200,6553200),(574050,6553200),(574050,6552800),(574120,6552800)]),'P-WORKER-BUS-LINK','shared','secondary',20)
road(LineString([(574120,6552373),(574550,6552373)]),'P-WORKER-ROUTE','people',width=4)
road(LineString([(574120,6552800),(574105,6552800),(574105,6552373),(574120,6552373)]),'P-COMPACT-STAFF-ENTRY','people',width=4)
# Shared plant corridor between two rows: dry-plant/fibre/thermal routes are assets, not new capacity.
for yy in [6552250,6552480]:road(LineString([(574120,yy),(574580,yy)]),f'P-COMPACT-DELIVERY-{yy}','machine',width=12)
for xx in [574210,574340]:
 road(LineString([(xx,6552250),(xx,6552288)]),f'P-DELIVERY-SOUTH-{xx}','machine',width=8)
 road(LineString([(xx,6552480),(xx,6552452)]),f'P-DELIVERY-NORTH-{xx}','machine',width=8,phase=2)
for k,(g,p) in enumerate(assets):
 if p['id'].startswith('F-PV'):p.update(panel_width_m=4,centre_height_m=3.8,fixed_tilt_degrees=20,minimum_edge_clearance_m=3.1,trial_status='Unplanted until water/soil approval')
 elif p['type']=='pv_row':p.update(panel_width_m=4,centre_height_m=1.7,fixed_tilt_degrees=20)
assets=[(g,p) for g,p in assets if p['type'] not in ['campus_power','campus_fibre','campus_cooling','campus_thermal']]
for typ,xy in [('campus_power',[(574495,6552220),(574495,6552355),(574210,6552355)]),('campus_fibre',[(574130,6552800),(574130,6552350),(574380,6552350)]),('campus_cooling',[(574490,6552400),(574490,6552358),(574210,6552358)]),('campus_thermal',[(574490,6552450),(574520,6552450),(574520,6552630)])]:assets.append((LineString(xy),dict(id=typ,type=typ,status='Conceptual segregated service trench / thermal demand unverified',phase=1)))
write(G/'buildings.geojson',new);write(G/'land_use.geojson',ll);write(G/'movement.geojson',rr);write(G/'assets.geojson',assets);write(O/'module-positions.geojson',pods)
# All-phase source account changes GFA/land allocations, not population or the four2MW group scenario.
qa=json.loads((O/'design-account.json').read_text());qa.update(active_compute_campus_km2=active.area/1e6,productive_gross_estate_km2=gross.area/1e6,unserviced_productive_reserve_km2=gross.difference(active).area/1e6,module_positions=32,module_operating_it_kw_assumed=250,module_rack_nameplate_kw_reference=336,power_block_nameplate_kw_reference=1000,plant_gap_logic='50m horizontal group gap and60m between-row zone reserve delivery, plant/fibre/thermal service and separated worker shade. Dimensions are entrant assumptions pending supplier/fire/thermal review.',land_use_km2={u:sum(g.area for g,p in ll if p['use']==u)/1e6 for u in set(p['use'] for g,p in ll)})
(O/'design-account.json').write_text(json.dumps(qa,indent=2));(O/'operational-conditions.json').write_text(json.dumps(dict(campus=dict(active_area_km2=active.area/1e6,positions_per_group=8,group_count=4,installed_positions_by_phase=[16,24,32],operating_it_mw=[4,6,8],reference_rack_nameplate_mw=10.752,power_block_ratings_total_mw=32,assumed_grid_connection_mw=12,source='https://xcity.ai/computepod',limits='Alternative covered equipment grouping, not a certified XPOD vendor layout. Nameplate power is not IT or operating draw. Cooling/fire/crane/utility layouts require vendor engineering.'),farm=dict(panel_width_m=4,centre_height_m=3.8,edge_clearance_m=3.1,row_pitch_m=18,clear_between_rows_m=14,headlands_m=100,fixed_tilt_degrees=20,pruned_jojoba_envelope_height_m=1.2,plant_envelope_diameter_m=2,assumed_machine_height_m=2.6,assumed_machine_width_m=2.5,planting_status='Unplanted until lawful water and soil trial evidence; no yield/irrigation credit',pollination='Trial male plants at both ends of selected female jojoba segments pending measured seasonal wind; species is wind-pollinated. Not a fixed-pilot internal layout.'),phasing=dict(commissioning='Installed works count as operating only after utility, emergency, resource and staffing tests.',construction_access='Eastern perimeter/northern bypass outside occupied West; fence active construction cells and keep public Main Street continuous.')),indent=2))
print('Compact operating campus',active.area/1e6,'km2;32 conceptual positions; protected fixed pilots unchanged')
