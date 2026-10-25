"""Only count route centreline covered by proposed shade structures."""
import json
from pathlib import Path
from shapely.geometry import shape,mapping
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
b=json.loads((P/'geometry/buildings.geojson').read_text());roof=unary_union([transform(t,shape(f['geometry'])) for f in b['features'] if f['properties'].get('form')=='canopy']).buffer(.05)
p=P/'geometry/movement.geojson';d=json.loads(p.read_text());out=[]
for f in d['features']:
 if not f['properties'].get('shaded') or f['geometry']['type']!='LineString':out.append(f);continue
 line=transform(t,shape(f['geometry']))
 for geom,shaded in [(line.intersection(roof),True),(line.difference(roof),False)]:
  for g in list(geom.geoms) if hasattr(geom,'geoms') else [geom]:
   if g.is_empty or g.geom_type!='LineString' or g.length<.001:continue
   props=dict(f['properties']);props['shaded']=shaded
   out.append(dict(type='Feature',geometry=mapping(transform(inv,g)),properties=props))
d['features']=out;p.write_text(json.dumps(d));print('Route pieces',len(out))
