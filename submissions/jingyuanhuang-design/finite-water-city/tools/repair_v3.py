"""Repair sub-centimetre projection round-trip topology, without changing design."""
import json,sys
from pathlib import Path
from shapely.geometry import shape,mapping
from shapely.ops import transform
from shapely import make_valid
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];sys.path.insert(0,str(R/'scripts'));import xcity_common as xc
t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
for path in (P/'geometry').glob('*.geojson'):
 d=json.loads(path.read_text());changed=False
 for f in d['features']:
  g=shape(f['geometry']);u=transform(t,g)
  if not u.is_valid:
   fixed=make_valid(u).buffer(-.02).simplify(.005,preserve_topology=True);f['geometry']=mapping(transform(inv,fixed));assert transform(t,shape(f['geometry'])).is_valid;changed=True;print('Repaired projection topology',path.name,f['properties'].get('name'))
 if changed:path.write_text(json.dumps(d,ensure_ascii=False))
d=json.loads((P/'metrics.json').read_text());c=xc.compute_metrics(str(P))
for m in d['metrics']:
 if m['key'] in c:m['value']=c[m['key']]
(P/'metrics.json').write_text(json.dumps(d,indent=2,ensure_ascii=False))
