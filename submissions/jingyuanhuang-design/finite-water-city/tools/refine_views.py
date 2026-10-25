import json
from pathlib import Path
from shapely.geometry import shape,mapping,LineString
from shapely.ops import transform
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];inv=Transformer.from_crs(32719,4326,always_xy=True).transform
ll=lambda p:list(inv(*p))
p=P/'geometry/nodes.geojson';d=json.loads(p.read_text())
for f in d['features']:
 q=f['properties']
 if q['node_id']=='N05':q.update(eye_from=ll((573620,6552340)),eye_to=ll((573720,6552250)))
 if q['node_id']=='N07':q.update(eye_from=ll((573190,6554520)),eye_to=ll((573150,6554450)))
p.write_text(json.dumps(d))
p=P/'geometry/movement.geojson';d=json.loads(p.read_text());line=LineString([(573620,6552600),(573620,6552340)])
if not any(f['properties'].get('name')=='Drying workshop public approach' for f in d['features']):d['features'].append(dict(type='Feature',geometry=mapping(transform(inv,line)),properties=dict(network='people',shaded=True,name='Drying workshop public approach')))
p.write_text(json.dumps(d))
p=P/'geometry/buildings.geojson';d=json.loads(p.read_text())
if not any(f['properties'].get('name')=='Workshop approach shade' for f in d['features']):d['features'].append(dict(type='Feature',geometry=mapping(transform(inv,line.buffer(2,cap_style=2))),properties=dict(use='civic',floors=1,form='canopy',height_m=4.5,name='Workshop approach shade')))
p.write_text(json.dumps(d))
