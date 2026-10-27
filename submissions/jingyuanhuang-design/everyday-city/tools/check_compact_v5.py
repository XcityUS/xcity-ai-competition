"""Targeted geometry, capacity and crop conservation checks for V5. Not engineering approval."""
from pathlib import Path
import json,sys
from shapely.geometry import shape,LineString
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/compact-v5';A=O/'before';T=Transformer.from_crs(4326,32719,always_xy=True).transform
load=lambda f:[(transform(T,shape(x['geometry'])),x['properties']) for x in json.loads(f.read_text())['features']]
scope=unary_union([g for g,p in load(R/'brief/site-package/boundaries/scope_9_13.geojson')]);oldb=load(A/'geometry/buildings.geojson');newb=load(P/'geometry/buildings.geojson');rs=load(P/'geometry/structure.geojson');base=[(g,p) for g,p in rs if p['plan_role']=='base_zoning'];un=unary_union([g for g,p in base]);oldr={p['id']:g for g,p in load(A/'geometry/structure.geojson')};newr={p['id']:g for g,p in base}
record=dict(status='targeted_self_review_not_engineering_approval',base_gap_m2=scope.difference(un).area,base_outside_m2=un.difference(scope).area,base_overlap_excess_m2=max(0,sum(g.area for g,p in base)-un.area),retained_difference_m2={k:oldr[k].symmetric_difference(newr[k]).area for k in ['D00-F','D00-L','D06','D07']})
assert record['base_gap_m2']<100;assert record['base_outside_m2']<100;assert record['base_overlap_excess_m2']<100
assert all(v<.1 for v in record['retained_difference_m2'].values())
for key in ['dwellings','jobs','operating_it_mw']:
 old=sum(p.get(key,0) for g,p in oldb);new=sum(p.get(key,0) for g,p in newb);record[key]=dict(before=old,after=new);assert old==new
oldtown={p['id']:g for g,p in oldb if p['id'].startswith(('WEST-','EAST-','NORTH-'))};newtown={p['id']:g for g,p in newb if p['id'] in oldtown};record['town_buildings_unchanged_m2']=sum(oldtown[k].symmetric_difference(newtown[k]).area for k in oldtown);assert record['town_buildings_unchanged_m2']<.1
for typ in ['pv_row']:
 old=[g for g,p in load(A/'geometry/assets.geojson') if p.get('type')==typ];new=[g for g,p in load(P/'geometry/assets.geojson') if p.get('type')==typ];record['pv_rows']=dict(before=len(old),after=len(new),length_before_m=sum(g.length for g in old),length_after_m=sum(g.length for g in new));assert len(old)==len(new);assert abs(sum(g.length for g in old)-sum(g.length for g in new))<.1
oldc=load(A/'geometry/crops.geojson');newc=load(P/'geometry/crops.geojson');record['crop_ha']=dict(before=sum(g.area for g,p in oldc)/1e4,after=sum(g.area for g,p in newc)/1e4);assert abs(record['crop_ha']['before']-record['crop_ha']['after'])<.0001
field=unary_union([g for g,p in load(P/'geometry/land_use.geojson') if p['id'] in ['P-SOLAR','F-LEARNING']]);record['crop_outside_fields_m2']=sum(g.difference(field).area for g,p in newc);assert record['crop_outside_fields_m2']<.1
# No building enters the sourced150m channel screening test; crop panels also remain outside that declared test.
channels=unary_union([g for g,p in load(R/'brief/site-package/water/channels_dem.geojson')]);record['building_channel_screen_overlap_m2']=sum(g.intersection(channels.buffer(150)).area for g,p in newb);assert record['building_channel_screen_overlap_m2']<.1
land=load(P/'geometry/land_use.geojson');master=unary_union([g for g,p in load(P/'geometry/master_area.geojson')]);lu=unary_union([g for g,p in land]);record['master_area_km2']=master.area/1e6;record['land_partition_gap_m2']=master.difference(lu).area;record['land_partition_overlap_m2']=max(0,sum(g.area for g,p in land)-lu.area);assert record['land_partition_gap_m2']<.1;assert record['land_partition_overlap_m2']<.1
record['remaining_checks']='Noise/thermal/fire buffers, civil grading, drainage crossings, utility isolation, vehicle swept paths and operating rights are unresolved.350/400m are layout assumptions, not approved standards.'
(O/'geometry-qa.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
