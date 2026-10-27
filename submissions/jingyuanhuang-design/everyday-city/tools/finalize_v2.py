"""Final spatial corrections, current-source audit, honest custom-drawing provenance and review checks."""
import json,sys,shutil,hashlib,subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import shape,mapping,Point,LineString,box
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/redesign-v2';G=P/'geometry';T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
sys.path.insert(0,str(R/'scripts'));import xcity_common as xc
load=lambda p:[(transform(T,shape(f['geometry'])),f['properties']) for f in json.loads(p.read_text())['features']]
def feature(g,p):return dict(type='Feature',properties=p,geometry=mapping(transform(I,g)))
# Correct service spurs to STOP before facades and approach the northern halls through gaps between repair sheds.
roads=[(g,p) for g,p in load(G/'movement.geojson') if g.geom_type in ['LineString','MultiLineString'] and p.get('id')!='REGIONAL-TOWN-JOIN']
updated=[]
for g,p in roads:
 id=p.get('id','')
 if id=='P-FREIGHT-LOOP':g=LineString([(574050,6551950),(575180,6551950),(575180,6553150),(574050,6553150),(574050,6551950)])
 if id.startswith('P-SPUR'):
  xx=float(id.split('-')[2]);yy=float(id.split('-')[3]);xx=xx if yy==6552050 else 574315 if xx==574250 else 574815
  g=LineString([(xx,6551950),(xx,6552030)]) if yy==6552050 else LineString([(xx,6553150),(xx,6552650)])
 if id=='REGIONAL-0':
  coords=list(g.coords);keep=next(i for i,v in enumerate(coords) if v[1]>=6554000);g=LineString([(573200,6553600),(573200,6554000)]+coords[keep:]);p['basis']='Retained original terrain-route study; southwest approach revised around new solar/compute parcels and joined to the public spine.'
 updated.append((g,p))
scope=unary_union([g for g,p in load(R/'brief/site-package/boundaries/scope_9_13.geojson')]);fixed=unary_union([g for f in ['pilot_area.geojson','pilot_living_area.geojson'] for g,p in load(R/'brief/site-package/pilot-area'/f)])
external=load(P/'context/external-access-study.geojson')[0][0];end=Point(list(external.coords)[0]);arrival=LineString([end.coords[0],(572500,6551100),(573050,6551550)]).intersection(scope).difference(fixed)
updated=[(g,p) for g,p in updated if p.get('id') not in ['SW-ARRIVAL-LINK','REGIONAL-WEST-RESEARCH']]
updated.append((arrival,dict(id='SW-ARRIVAL-LINK',name='Main southwest arrival / unsecured study',network='shared',road_class='primary',width_m=26,phase=1,shaded=False,study_only=True,secured=False,basis='Connect the retained external RN40 corridor-study boundary endpoint to the new public arrival; actual rights, flood crossings and gradients unverified.')))
west=LineString([(580122.4,6574623.7),(577000,6578000),(574000,6582000),(570000,6588000)]).intersection(scope).difference(fixed)
updated.append((west,dict(id='REGIONAL-WEST-RESEARCH',name='Western field-service study',network='shared',road_class='secondary',width_m=24,phase=3,shaded=False,study_only=True,secured=False,basis='Entrant access study serving the western dry-agriculture district; channel crossings/terrain/right-of-way unresolved, no built road claim.')))
# Count both people/shared to machine contacts, with each unique coordinate once.
cross=[]
for a,pa in updated:
 if pa['network'] not in ['people','shared']:continue
 for b,pb in updated:
  if pb['network']!='machine':continue
  q=a.intersection(b)
  if q.geom_type in ['LineString','MultiLineString'] and not q.is_empty:
   # Shared alignments have an interface at each end.
   parts=[q] if q.geom_type=='LineString' else list(q.geoms);qs=[Point(v) for z in parts for v in [z.coords[0],z.coords[-1]]]
  else:qs=[q] if q.geom_type=='Point' else list(getattr(q,'geoms',[]))
  for v in qs:
   if v.geom_type=='Point' and all(v.distance(w)>1 for w in cross):cross.append(v)
flags=[(q,dict(kind='interface',name='Proposed pedestrian priority interface',rule='Machine stop and interlocked/manual release; accessible junction design required')) for q in cross]
(G/'movement.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=[feature(g,p) for g,p in updated+flags]),separators=(',',':'))+'\n');(G/'interfaces.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=[feature(g,p) for g,p in flags]),separators=(',',':'))+'\n')
build=load(G/'buildings.geojson');conflicts=[]
for g,p in updated:
 for b,pb in build:
  if pb.get('form')!='canopy' and g.intersection(b).length>1:conflicts.append([p.get('id'),pb['id'],g.intersection(b).length])
assert not conflicts,conflicts
qa=json.loads((O/'design-account.json').read_text());qa['interfaces']=len(cross);qa['road_building_centerline_conflicts']=conflicts;qa['qa_note']='Road centreline tests only; swept paths, widths, accessible route junctions and emergency engineering need professional review.';(O/'design-account.json').write_text(json.dumps(qa,indent=2))
# Current source checksums; retain every licence statement from the issued registry.
src=json.loads((P/'sources.json').read_text());commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();src['sources'][0]['url']='https://github.com/XcityUS/xcity-ai-competition/tree/'+commit+'/brief/site-package'
for f in src.get('file_checksums',[]):f['sha256']=xc.sha256_file(str(R/f['path']))
issued=json.loads((R/'brief/site-package/sources.json').read_text())['sources']
for d in issued:
 if d['id'] in ['SRC-KML','SRC-PILOT','SRC-DEM','SRC-OSM'] and d['id'] not in [v['id'] for v in src['sources']]:src['sources'].append(dict(id=d['id'],title=d['title'],publisher=d['publisher'],url=d.get('licence_url',src['sources'][0]['url']),accessed='2026-10-27',used_for='Issued '+', '.join(d['used_in']),licence=d['licence']))
(P/'sources.json').write_text(json.dumps(src,indent=2)+'\n')
# Update current metrics after the complete crossing audit; avoid stale V1 statements.
metrics=json.loads((P/'metrics.json').read_text());comp=xc.compute_metrics(str(P))
for v in metrics['metrics']:
 if v['key'] in comp:v['value']=comp[v['key']]
(P/'metrics.json').write_text(json.dumps(metrics,indent=2))
reportarchive=P/'reviews/withdrawn-v1/report';reportarchive.mkdir(exist_ok=True)
for n in ['energy-results.json','geometry-qa.json','hourly-energy.csv','independent-qa.json','page-index.json']:
 f=P/'report'/n
 if f.exists():shutil.move(str(f),str(reportarchive/n))
(P/'report/geometry-qa-v2.json').write_text(json.dumps(qa,indent=2))
# Accurate requirement-reference map: keep unresolved content partial, not simply 'answered'.
cm=json.loads((P/'compliance_matrix.json').read_text());sections={'agent.1':1,'agent.2':8,'agent.3':8,'agent.4':6,'agent.5':9,'agent.6':4,'agent.7':14,'agent.8':9,'M1':8,'M2':8,'M3':8,'M4':8,'M5':14,'M6':6,'M7':6,'M8':14,'M9':14,'M10':9,'M11':14,'M12':9}
for v in cm['items']:v.update(status='partial',section='## '+str(sections[v['id']])+'.',note='V2 scenario/design response is documented. Survey, rights, demand/employment, engineering and operating-budget evidence remain explicit verification needs, not resolved by an automatic check.')
(P/'compliance_matrix.json').write_text(json.dumps(cm,indent=2))
# Replace the old total in public prose after recounting interfaces, without calling them proved-safe crossings.
for f in [P/'proposal.md',P/'report/proposal.html']:
 s=f.read_text().replace('The36 computed','The '+str(len(cross))+' computed').replace('The 36 computed','The '+str(len(cross))+' computed').replace('The 6 computed','The '+str(len(cross))+' computed');f.write_text(s)
f=P/'report/proposal.html';s=f.read_text();import re
s=re.sub(r'name="xcity-source-sha256" content="[0-9a-f]+"','name="xcity-source-sha256" content="'+xc.sha256_file(str(P/'proposal.md'))+'"',s);f.write_text(s)
print('Final spatial review:',len(cross),'people/shared-machine contacts; zero road centreline/building conflicts. Rebuild diagrams, scene and presentation before stamping.')
