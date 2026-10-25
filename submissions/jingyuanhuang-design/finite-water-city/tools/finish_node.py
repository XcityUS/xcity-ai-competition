import json
from pathlib import Path
from shapely.geometry import mapping,box,LineString
from shapely.ops import transform
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];inv=Transformer.from_crs(32719,4326,always_xy=True).transform;ll=lambda x,y:list(inv(x,y))
p=P/'geometry/nodes.geojson';d=json.loads(p.read_text())
for f in d['features']:
 if f['properties']['node_id']=='N05':f['properties'].update(eye_from=ll(573620,6552520),eye_to=ll(573540,6552490))
p.write_text(json.dumps(d))
p=P/'geometry/buildings.geojson';d=json.loads(p.read_text())
if not any(f['properties'].get('name')=='Cooperative drying and heat exchange pavilion' for f in d['features']):d['features'].append(dict(type='Feature',geometry=mapping(transform(inv,box(573500,6552470,573570,6552505))),properties=dict(use='industry',floors=1,height_m=5,name='Cooperative drying and heat exchange pavilion')))
p.write_text(json.dumps(d))
