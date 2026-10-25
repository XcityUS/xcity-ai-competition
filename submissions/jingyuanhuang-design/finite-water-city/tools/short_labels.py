import json
from pathlib import Path
P=Path(__file__).resolve().parents[1];p=P/'geometry/land_use.geojson';d=json.loads(p.read_text());labels={'compute':'Compute','industry':'Repair','residential':'Hard patios','civic':'Hard civic','agriculture':'Nursery','energy':'PV + storage'}
for i,f in enumerate(d['features']):
 u=f['properties']['use'];f['properties']['name']=labels.get(u,'Hard wash' if i==0 else 'Hard desert')
p.write_text(json.dumps(d))
