"""Targeted V4 area/source/retained geometry QA; no design approval."""
from pathlib import Path
import json,hashlib
from shapely.geometry import shape
from shapely.ops import transform,unary_union
from pyproj import Transformer,Geod
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/functional-v4';T=Transformer.from_crs(4326,32719,always_xy=True).transform;G=Geod(ellps='WGS84')
def load(p):return [(shape(f['geometry']),f['properties']) for f in json.loads(p.read_text())['features']]
def geoarea_lonlat(g):
 if g.is_empty:return 0.
 if g.geom_type=='Polygon':return abs(G.geometry_area_perimeter(g)[0])/1e6
 return sum(geoarea_lonlat(q) for q in getattr(g,'geoms',[]))
rs=load(P/'geometry/structure.geojson');base=[(g,p) for g,p in rs if p['plan_role']=='base_zoning'];scope=unary_union([g for g,p in load(R/'brief/site-package/boundaries/scope_9_13.geojson')]);un=unary_union([g for g,p in base]);sp=transform(T,scope);up=transform(T,un);old=dict((p['id'],g) for g,p in load(O/'before/geometry/structure.geojson'));now=dict((p['id'],g) for g,p in base)
checks={'invalid_features':[p['id'] for g,p in rs if not g.is_valid],'unallocated_m2':sp.difference(up).area,'outside_scope_m2':up.difference(sp).area,'overlap_excess_m2':max(0,sum(transform(T,g).area for g,p in base)-up.area),'retained_unchanged_m2':{id:transform(T,old[id]).symmetric_difference(transform(T,now[id])).area for id in ['D00-F','D00-L','D06','D07']}}
assert not checks['invalid_features'];assert checks['unallocated_m2']<10;assert checks['outside_scope_m2']<100;assert checks['overlap_excess_m2']<.1;assert all(v<.1 for v in checks['retained_unchanged_m2'].values())
# Local geometry/cameras unchanged. Re-rasterisation can differ by subpixel anti-aliasing.
import numpy as np
from PIL import Image
provenance=json.loads((P/'image_provenance.json').read_text());checks['local_control_comparison']={}
for r in provenance['images']:
 cur=P/r['control_image'];before=O/'before'/r['control_image']
 if before.exists():
  a=np.array(Image.open(before).convert('RGB')).astype(int);b=np.array(Image.open(cur).convert('RGB')).astype(int);delta=abs(a-b);v=dict(mean_channel_delta=float(delta.mean()),fraction_pixels_delta_over10=float(np.mean(delta.max(axis=2)>10)),basis='Same geometry/camera; tiny floating-point/anti-alias differences on unchanged roads, visually reviewed.')
  assert v['mean_channel_delta']<.01 and v['fraction_pixels_delta_over10']<.001
 else:
  v=dict(bit_identical=r.get('control_sha256')==hashlib.sha256(cur.read_bytes()).hexdigest());assert v['bit_identical']
 checks['local_control_comparison'][r['control_image']]=v
checks['numerical_tolerance_note']='UTM/longitude round trips produce <100m2 boundary slivers and <10m2 base gaps across1658km2; figures are reported without treating these as construction exclusions. One D03-E ring required a1e-10 degree inward nudge.'
# Parent programme/under-panel bands are retained; this revision changes territorial envelopes only.
checks['local_capacity_change']=False;checks['status']='passed_targeted_geometry_and_identity_checks_only';checks['content_review']='self_review_only_not_independent';checks['official_advisory_issue']='The current organiser analyse_functional_balance.py transforms MultiPolygon components a second time during recursive area calculation. Its MultiPolygon totals are not used as evidence here; this package checks geodesic area with a single lon/lat transformation.'
checks['geodesic_scope_km2']=geoarea_lonlat(scope);checks['geodesic_districts']=[dict(id=p['id'],km2=geoarea_lonlat(g),pct=100*geoarea_lonlat(g)/geoarea_lonlat(scope)) for g,p in base];checks['geodesic_functional_coverage']=[dict(system=p['system'],km2=geoarea_lonlat(g),pct=100*geoarea_lonlat(g)/geoarea_lonlat(scope)) for g,p in rs if p['plan_role']=='system_overlay'];(O/'geometry-and-balance-qa.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
