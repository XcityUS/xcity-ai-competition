"""C02 V3: useful forecourts and rear servicing; crop area and programme unchanged."""
import json,sys
from pathlib import Path
from shapely.geometry import shape,mapping,box,LineString,Point
from shapely.ops import transform,unary_union
from shapely.affinity import translate
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];G=P/'geometry';O=P/'reviews/redesign-v3';O.mkdir(exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:[(transform(T,shape(v['geometry'])),v['properties']) for v in json.loads(f.read_text())['features']]
def write(f,items):f.write_text(json.dumps(dict(type='FeatureCollection',features=[dict(type='Feature',geometry=mapping(transform(I,g)),properties=p) for g,p in items]),separators=(',',':'))+'\n')
b=load(G/'buildings.geojson')
for i,(g,v) in enumerate(b):
 if v['id'].startswith('F-TRAINING'):
  j=int(v['id'].split('-')[-1]);b[i]=(box(573100+j*300,6551345,573300+j*300,6551375),dict(v,name='Farm workshop and learning hall '+str(j+1),frontage='Public forecourt south; rear delivery north',revision='V3'))
write(G/'buildings.geojson',b)
r=[(g,v) for g,v in load(G/'movement.geojson') if not v.get('id','').startswith('F-V3') and g.geom_type!='Point']
r.append((LineString([(573050,6551550),(573025,6551550),(573025,6551313),(573080,6551313)]),dict(id='F-V3-PUBLIC-APPROACH',name='Separated public arrival to shade promenade',network='people',road_class='local',phase=1,width_m=4,shaded=False)))
for x in [573150,573250,573450,573550]:r.append((LineString([(x,6551313),(x,6551344)]),dict(id='F-V3-ENTRY-'+str(x),name='Accessible visitor entry',network='people',road_class='local',phase=1,width_m=4,shaded=False)))
r.append((LineString([(573750,6551410),(573075,6551410)]),dict(id='F-V3-REAR-DELIVERY',name='Rear workshop delivery and maintenance',network='machine',road_class='local',phase=1,width_m=12,shaded=False)))
for x in [573200,573500]:r.append((LineString([(x,6551410),(x,6551386)]),dict(id='F-V3-DOCK-'+str(x),name='Rear loading approach',network='machine',road_class='local',phase=1,width_m=8,shaded=False)))
r=[(LineString([(573080,6551313),(573720,6551313)]),dict(v,shaded=True)) if v.get('id')=='F-VISITOR-PROMENADE' else (g,v) for g,v in r]
write(G/'movement.geojson',r)
d=[]
def surface(g,id,role,material):d.append((g,dict(id=id,role=role,material=material,phase=1,evidence='declared',basis='V3 node organisation; surface dimensions are entrant assumptions, not surveyed engineering standards')))
for x in [573100,573400]:
 surface(box(x,6551316,x+200,6551345),'COURT-'+str(x),'Public workshop forecourt / entry, seating and outdoor demonstrations','mineral_pavers')
 surface(box(x-10,6551375,x+210,6551445),'YARD-'+str(x),'Rear loading / cleaning / maintenance apron, no public through route','stabilised_gravel')
surface(box(573640,6551375,573720,6551445),'EQUIPMENT-STAGING','Equipment and pallet staging, outside visitor ground','stabilised_gravel')
surface(box(573300,6551316,573400,6551345),'CENTRAL-COURT','Public orientation / assembly court between halls','mineral_pavers')
surface(box(573000,6551110,573100,6551285),'WEST-HEADLAND','100m assumed machinery headland / turning and row maintenance','field_track')
surface(box(573700,6551110,573800,6551285),'EAST-HEADLAND','100m assumed machinery headland / turning and row maintenance','field_track')
write(G/'courtyard_details.geojson',d)
a=[(g,v) for g,v in load(G/'assets.geojson') if not v.get('id','').startswith('F-V3')]
a.append((LineString([(573080,6551293),(573720,6551293)]),dict(id='F-V3-FIELD-EDGE',type='farm_public_fence',height_m=.9,phase=1,material='open_wire_fence',basis='Assumed low permeable barrier; gates at field ends, not a flood defence')))
for x in [573130,573230,573430,573530]:a.append((LineString([(x,6551310.6),(x+8,6551310.6)]),dict(id='F-V3-BENCH-'+str(x),type='bench',height_m=.45,phase=1,material='timber',basis='Illustrative modelled seating, not occupancy capacity')))
a.append((Point(573705,6551428),dict(id='F-V3-METER',type='irrigation_meter',phase=1,height_m=1.2,basis='Proposed isolatable farm meter and valve interface, no water-right claim')))
write(G/'assets.geojson',a)
record=dict(revision='V3 / C02 courtyard and framing correction',building_shift_south_m=55,public_forecourt_depth_m=29,rear_apron_depth_m=70,programme_change='None: same2 halls,6000m2 each,70jobs total; same8 panel rows and crop bands; no additional irrigation',unbuilt_ground={'field_ends':'100m manoeuvring/service headlands, assumed','rear_edge':'Existing main arrival/service link retained; compact apron has actual loading purpose','outside_node':'Undeveloped terrain remains outside the close local frame'},separation='Public promenade and forecourts south of workshops; machinery deliveries north/rear. No new public/machine crossing.',proof='geometry/courtyard_details.geojson and current movement/buildings/assets; all source-based',limits='Detailed turning, accessibility, grading, fencing, drainage and agronomy require professional verification')
(O/'design-changes.json').write_text(json.dumps(record,indent=2));print(record)
