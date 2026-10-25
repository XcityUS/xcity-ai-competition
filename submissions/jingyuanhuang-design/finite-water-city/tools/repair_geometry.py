"""Repair projection roundtrip topology without changing organiser scripts."""
import json
from pathlib import Path
from shapely import make_valid
from shapely.geometry import shape,mapping
from shapely.ops import transform
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
for f in (P/'geometry').glob('*.geojson'):
 d=json.loads(f.read_text());n=0
 for ft in d['features']:
  g=shape(ft['geometry'])
  if g.geom_type not in ['Polygon','MultiPolygon']:continue
  rt=transform(t,g)
  if g.is_valid and rt.is_valid:continue
  g=make_valid(rt).buffer(-.02).simplify(.005,preserve_topology=True)
  if g.geom_type=='GeometryCollection':
   from shapely.ops import unary_union
   g=unary_union([q for q in g.geoms if q.geom_type in ['Polygon','MultiPolygon']])
  out=transform(inv,g);assert out.is_valid and transform(t,out).is_valid,(f,g.geom_type)
  ft['geometry']=mapping(out);n+=1
 f.write_text(json.dumps(d));print(f.name,n)
