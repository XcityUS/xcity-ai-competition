#!/usr/bin/env python3
"""Create an isolated repository and a non-legacy integration fixture from credited design data.
Never edits submissions or represents a newly reviewed city. No fixed design form is prescribed.
"""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from shapely.geometry import mapping
from shapely.ops import unary_union
import xcity_common as xc
ROOT=Path(xc.ROOT)
def run(destination,source_fixture=None):
 isolated=Path(destination).resolve()
 if isolated.exists():raise SystemExit('Refusing to overwrite an existing isolated root: '+str(isolated))
 if isolated==ROOT or ROOT in isolated.parents:raise SystemExit('The isolated root must remain outside the real repository')
 source=Path(source_fixture).resolve() if source_fixture else ROOT/'submissions/jingyuanhuang-design/finite-water-city'
 if not (source/'manifest.json').is_file():raise SystemExit('Source fixture has no manifest.json')
 isolated.mkdir(parents=True)
 for directory in ['scripts','brief','schema','templates','docs','skills']:
  shutil.copytree(ROOT/directory,isolated/directory,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
 for filename in ['requirements.txt','AGENTS.md','README.md','LICENSE']:
  if (ROOT/filename).is_file():shutil.copyfile(ROOT/filename,isolated/filename)
 p=isolated/'submissions/qa-validation/v2-city'
 shutil.copytree(source,p,ignore=shutil.ignore_patterns('reviews','media','renders','visual','self_check.json','__pycache__'))
 def read(name):return json.loads((p/name).read_text())
 def write(name,d):(p/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 # Keep the actual design as a credited test input. Normalise the land-account partition only.
 geo=xc.load_geometry(str(p));master=unary_union([g for _,g in geo['master_area']]);living=xc.pilot_parts()['living'];used=master.difference(master);features=[]
 for props,g in geo['land_use']:
  g=g.intersection(master).difference(used)
  if g.is_empty:continue
  used=unary_union([used,g])
  for part,use in [(g.difference(living),props.get('use')),(g.intersection(living),'residential')]:
   part=xc.polygons_only(part)
   if not part.is_empty:features.append({'type':'Feature','properties':dict(props,use=use),'geometry':mapping(part)})
 remaining=xc.polygons_only(master.difference(used))
 if not remaining.is_empty:features.append({'type':'Feature','properties':{'use':'open_space','note':'QA-only unallocated-account remainder; not a design recommendation'},'geometry':mapping(remaining)})
 write('geometry/land_use.geojson',{'type':'FeatureCollection','features':features})
 # Synthetic base-zoning/road records exercise the new full-site contract only.
 # No original entry is modified, and these records are not an accepted design.
 structure=read('geometry/structure.geojson');whole=xc.to_utm(xc.site_boundary());occupied=whole.difference(whole);base=[]
 for i,feature in enumerate(structure['features']):
  part=xc.polygons_only(xc.to_utm(shape(feature['geometry'])).intersection(whole).difference(occupied))
  if part is None or part.is_empty:continue
  props=dict(feature['properties'],plan_role='base_zoning',district_id='QA-'+str(i),primary_use='test_area',name='Synthetic QA base area',basis_ref='proposal.md#qa-fixture-not-a-design')
  base.append({'type':'Feature','properties':props,'geometry':mapping(xc.to_lonlat(part))});occupied=unary_union([occupied,part])
 remainder=xc.polygons_only(whole.difference(occupied))
 if remainder is not None and not remainder.is_empty:base.append({'type':'Feature','properties':{'plan_role':'base_zoning','district_id':'QA-REMAINDER','primary_use':'reserve','system':'reserve','name':'Synthetic QA remainder','basis_ref':'proposal.md#qa-fixture-not-a-design'},'geometry':mapping(xc.to_lonlat(remainder))})
 write('geometry/structure.geojson',{'type':'FeatureCollection','features':base})
 movement=read('geometry/movement.geojson');route_features=[f for f in movement['features'] if f['geometry']['type'] in ['LineString','MultiLineString']]
 for level,feature in zip(['primary','secondary'],route_features):feature['properties']['road_class']=level
 write('geometry/movement.geojson',movement)
 man=read('manifest.json');man['booklet']={};man['design_depth']={'tier1_structure':{'evidence':['geometry/structure.geojson','figures/fig-01-structure.png']},'tier2_master':{'evidence':['geometry/master_area.geojson','figures/fig-02-master-plan.png']},'tier3_nodes':{n:{'plan':'figures/node-'+n+'-plan.png','aerial':'figures/node-'+n+'-aerial.png','eye_level':'figures/node-'+n+'-eye.png'} for n in man['nodes']}};man['slug']='v2-city';man['author']['github']='qa-validation';man['title']='QA only — rule integration fixture';man['thesis']='Technical integration fixture based on credited Finite Water City, not an approved or new competition entry.';man['autonomy']['human_role']='Organiser QA transformation only. No external image-generation tool used; massing fallback is labelled. Original design credit retained in proposal.';write('manifest.json',man)
 write('image_provenance.json',{'images':[]})
 template=json.loads((ROOT/'templates/design_depth_matrix.json').read_text());ids=['whole_site','overall_layout','urban_design','nodes']+['node:'+x for x in man['nodes']]
 for row,rid in zip(template['rows'],ids):
  row.update(id=rid,decision='Cross-reference existing spatial evidence for the '+rid+' test; quality remains unassessed',scope={'extent':'Fixed whole site' if rid=='whole_site' else 'Existing test master/node geometry','phase':'Existing capacity scenario; implementation not verified'},drawings=['figures/fig-01-structure.png' if rid=='whole_site' else 'figures/fig-02-master-plan.png' if not rid.startswith('node:') else 'figures/node-'+rid[5:]+'-plan.png'],metrics=['residents_phase1'],gaps=[{'kind':'professional_verification','missing':'Independent design quality, resource rights and engineering verification','next_step':'Review by an authorised independent design and technical reviewer','responsible':'Organiser reviewer and relevant specialists'}])
 write('design_depth_matrix.json',template)
 metrics=read('metrics.json');computed=xc.compute_metrics(str(p))
 for metric in metrics['metrics']:
  if metric.get('key') in xc.COMPUTED_KEYS:metric['value']=computed[metric['key']]
 write('metrics.json',metrics)
 programme=json.loads((ROOT/'templates/phasing_programme.json').read_text())
 phase_geometry=read('geometry/phasing.geojson')
 residents=next(m['value'] for m in metrics['metrics'] if m['key']=='residents_phase1')
 for phase in programme['phases']:
  n=phase['phase'];zid='qa-phase-'+str(n)
  phase.update(period='Relative test interval; not a delivery forecast',objective='QA fixture only; no design approval',works=['Synthetic programme structure for checker test'],sequence_dependencies=['Verify resources before occupied development'],trigger='Specialist verification and capacity confirmation')
  phase['zones']=[dict(zone_id=zid,name='QA test zone',basis='Synthetic zero-growth fixture; not a design forecast',new_residents=residents if n==1 else 0,cumulative_residents=residents if n==1 else 0,new_dwellings=0,cumulative_dwellings=0,new_jobs=0,cumulative_jobs=0)]
  for feature in phase_geometry['features']:
   if feature['properties']['phase']==n:feature['properties']['zone_id']=zid
 write('geometry/phasing.geojson',phase_geometry);write('phasing_programme.json',programme)
 prop=(p/'proposal.md').read_text();(p/'proposal.md').write_text('QA INTEGRATION ONLY. Derived from jingyuanhuang-design/finite-water-city; no participant source is modified. Account normalisation and missing-data declarations test the tools, not design adequacy.\n\n'+prop)
 (p/'changelog.md').write_text('Organiser isolated fixture: v2 matrix, clipped metrics and partition normalisation. Original design credited; not submitted or approved.\n')
 for script in ['make_scene.py','finalize_submission.py']:
  args=[sys.executable,str(isolated/'scripts'/script),str(p)]
  if script=='finalize_submission.py':args.append('--redraw')
  subprocess.run(args,check=True,cwd=isolated)
 result=read('self_check.json')
 if not result.get('pass') or result.get('gates_passed')!=12 or result.get('gates_total')!=12:raise SystemExit('The non-legacy isolated fixture did not pass all 12 automatic checks')
 if read('design_depth_matrix.json').get('schema_version')!=2:raise SystemExit('The integration fixture must use matrix version 2')
 print('Isolated non-legacy fixture ready for visual QA:',p)
 print('Automatic checks: PASS 12/12. Content review: not_assessed. This is a credited QA transformation, not an approved design.')
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('destination',help='New isolated repository root outside the real repository (must not exist)');ap.add_argument('--source-fixture',help='Optional prepared fixture; original source is never modified');a=ap.parse_args();run(a.destination,a.source_fixture)
