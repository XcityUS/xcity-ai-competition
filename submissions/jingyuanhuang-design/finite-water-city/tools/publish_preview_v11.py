"""Promote the authorised V11 review to public-facing entry paths, without claiming design approval."""
import json,shutil,sys,html,hashlib
from pathlib import Path
from shapely import make_valid
from shapely.geometry import shape,mapping,Point
from shapely.ops import unary_union,transform
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];V9=P/'reviews/complete-city-v9';V10=P/'reviews/presentation-v10';V11=P/'reviews/presentation-v11';sys.path.insert(0,str(R/'scripts'));import xcity_common as xc
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
read=lambda p:json.loads(p.read_text())
write=lambda p,d:p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def poly(g):
 if g.geom_type in ['Polygon','MultiPolygon']:return g
 return unary_union([poly(q) for q in getattr(g,'geoms',[]) if not poly(q).is_empty])
def line(g):
 if g.geom_type in ['LineString','MultiLineString','Point']:return g
 return unary_union([line(q) for q in getattr(g,'geoms',[]) if not line(q).is_empty])
for d in ['drawings','media','renders','geometry','figures','report','context','visual']:(P/d).mkdir(exist_ok=True)
for a,b in [('booklet','a3-booklet'),('a0','a0-board'),('technical-appendix','a3-technical-appendix')]:shutil.copy2(V11/'drawings'/f'agua-finita-v11-{a}.pdf',P/'drawings'/f'{b}.pdf')
shutil.copy2(V11/'drawings/presentation-index.json',P/'drawings/presentation-index.json')
# The already published old geometry is retained in Git history; current public paths now mean current geometry.
scope=unary_union([shape(f['geometry']) for f in read(R/'brief/site-package/boundaries/scope_9_13.geojson')['features']])
geo=V10/'scene/geometry'
for name in ['buildings','land_use','movement','phasing','nodes']:
 d=read(geo/(name+'.geojson'));fs=[]
 for f in d['features']:
  g=make_valid(shape(f['geometry']));q=f['properties']
  if name=='movement':
   g=line(g.intersection(scope))
   q['road_class']={'production':'secondary','primary':'primary','secondary':'secondary'}.get(q.get('hierarchy'),'local')
   if q.get('shaded'):q['shade_intent']=True;q['shaded']=False
  else:g=poly(g)
  if g.is_empty:continue
  f['geometry']=mapping(g)
  if name=='land_use':
   q['programme_use']=q['use'];q['use']={'school':'civic','daily_centre':'civic','public_commons':'civic','culture':'civic','arrival':'civic','dry_park':'open_space','dry_open_space':'open_space','terrain_review':'reserve','operational_reserve':'reserve','streets':'infrastructure'}.get(q['use'],q['use'])
  if name=='nodes':
   nid=q['node_id'];q['place_name']=q['name'];q['name']=q.get('official_topic',q['name']);q['why']={'A03':'Tests engineered shade and daily public life at the town-level centre','B03':'Tests controlled production, worker access, dry cooling and an honest uncredited heat-reuse claim','C03':'Tests dry-season visitor access without blocking seasonal conveyance'}[nid]
  fs.append(f)
 d['features']=fs;write(P/'geometry'/(name+'.geojson'),d)
shutil.copy2(V9/'geometry/master_area.geojson',P/'geometry/master_area.geojson')
# Full-site base zoning and overlapping fixed context are distinct accounts.
d=read(V9/'geometry/planning_regions.geojson');sysmap={'Z1':'living','Z2':'agri_production','Z3':'energy_compute','Z4':'industry','Z5':'port','Z6':'reserve'};primary={'Z1':'mixed_use','Z2':'agriculture','Z3':'solar_agriculture','Z4':'industry','Z5':'logistics','Z6':'ecology'}
for f in d['features']:
 q=f['properties'];rid=q['id'];q.update(plan_role='base_zoning',district_id=rid,system=sysmap[rid],primary_use=primary[rid],basis_ref='proposal.md#2-full-site-zoning',evidence='declared',boundary_status='Proposed planning demarcation, not an issued statutory boundary')
for rel,system,n in [('pilot-area/pilot_area.geojson','agri_production','Fixed agrivoltaic fields'),('pilot-area/pilot_living_area.geojson','living','Fixed living-quarter outline')]:
 for f in read(R/'brief/site-package'/rel)['features']:
  f['properties'].update(plan_role='system_overlay',system=system,name=n,primary_use='fixed_context',basis_ref='brief/site-package/'+rel,status='fixed_unchanged');d['features'].append(f)
write(P/'geometry/structure.geojson',d)
# Regional corridors are proposals and remain distinct from secured access.
m=read(P/'geometry/movement.geojson');regional=read(P/'reviews/whole-site-v3/corridors.geojson')
for f in regional['features']:
 q=f['properties']
 if (q.get('from_id'),q.get('to_id')) not in [('A','K1'),('K1','K2'),('K2','C'),('K1','D'),('D','E')]:continue
 g=line(make_valid(shape(f['geometry'])).intersection(scope))
 if g.is_empty:continue
 q.update(id='regional-'+str(q.get('from_id'))+'-'+str(q.get('to_id')),road_class='secondary' if q.get('to_id')=='C' else 'primary',network='shared',status='proposed_corridor_study_not_secured',shaded=False,basis_ref='reviews/whole-site-v3/corridors.geojson');f['geometry']=mapping(g);m['features'].append(f)
people=unary_union([shape(f['geometry']) for f in m['features'] if f['properties'].get('network')=='people']);machine=unary_union([shape(f['geometry']) for f in m['features'] if f['properties'].get('network')=='machine'])
def points(g):
 if g.geom_type=='Point':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from points(q)
for i,g in enumerate(points(people.intersection(machine))):m['features'].append(dict(type='Feature',geometry=mapping(g),properties=dict(id='interface-v11-'+str(i),kind='interface',network='shared',control='Proposed pedestrian-priority interlock; operational and crossing detail remains unverified',phase=1)))
write(P/'geometry/movement.geojson',m);shutil.copy2(P/'reviews/district-structure-v8/access-studies.geojson',P/'context/access_studies.geojson')
# Current figures and registered source images at canonical website paths.
figmap={'diagram-whole-site-composite.png':'fig-01-structure.png','diagram-composite.png':'fig-02-master-plan.png','diagram-movement.png':'fig-04-movement.png','diagram-green.png':'fig-05-open-space-water.png','phase.png':'fig-06-phasing.png','locator.png':'fig-08-node-location.png'}
for a,b in figmap.items():shutil.copy2(V11/'drawings'/a,P/'figures'/b)
for a,b in [('07-land-use-and-accounts.png','fig-03-land-use-density.png'),('14-resource-and-delivery.png','fig-07-metrics.png')]:shutil.copy2(V9/a,P/'figures'/b)
pro=read(V11/'image_provenance.json')
for im in pro['images']:
 old=im['path'].split('/')[-1];view=old[:-4];im['path']='media/v11-'+old;im['control_image']='renders/v11-'+old;im['reference_images_note']='Own geometry-derived V10 control, registered absolute camera in reviews/presentation-v10/camera-registry.json; unchanged selected finish. No third-party design reference.'
 shutil.copy2(V11/'media'/old,P/im['path']);shutil.copy2(V11/'controls'/old,P/im['control_image'])
 if view!='city-overall':
  nid=view.split('-')[0];shutil.copy2(V11/'media'/old,P/'figures'/f"node-{nid}-{'eye' if 'eye' in view else 'aerial'}.png")
for nid in ['A03','B03','C03']:shutil.copy2(V11/'drawings'/f'{nid}-detail-plan.png',P/'figures'/f'node-{nid}-plan.png')
write(P/'image_provenance.json',pro)
# Serve the current model, rather than the withdrawn old scene.
s=(V10/'scene/visual/index.html').read_text().replace('AGUA FINITA / V10 camera controls','AGUA FINITA / V11 preview model');(P/'visual/index.html').write_text(s)
# Typed phase programme; detailed figures remain available off the A0 board.
raw=read(V9/'metrics.json');ph=raw['phases']
for row in ph:
 row['objective']={1:'Independently operable first release',2:'Connected demand-led expansion',3:'Complete northern precinct and conditional eastern gateway'}[row['phase']]
 row['works']=['Verified access and utility supply; the zone-specific buildings and public services listed below']
 row['sequence_dependencies']=['Access rights and combined existing/new water balance before occupancy','Funded public service operation and household livelihoods before housing release','Independent trade, access, utility and roster welfare case before gateway works']
write(P/'phasing_programme.json',dict(schema_version=1,map='figures/fig-06-phasing.png',a0_board='drawings/a0-board.pdf',status='conditional_design_scenario_not_approved_calendar',phases=ph))
# All evidence links now refer to the displayed revision, not a superseded four-town model.
mf=read(P/'manifest.json');mf.update(summary='A six-region whole-site planning proposal combines a continuous residential district, a compact public centre, independent compute/repair and solar facilities, conditional agricultural services and an eastern gateway. V11 restores explicit zoning, road hierarchy, public anchors and dry-landscape links. Public preview; resource rights and professional design verification remain open.',thesis='Continuous living districts and independent production grow through verified water, access and funded public services.',updated='2026-10-27',package_state='draft',presentation_revision='V11',public_display_status='authorised_preview_not_design_approval')
mf['autonomy']['human_role']+=' On 2026-10-27 the human reviewed the V10 images, explicitly authorised direct website updating, then required V11 spatial composite diagrams and no spreadsheet-style A0 table. Codex retained full numeric accounts in the booklet/technical records and kept the display as a public design preview, not an approval.'
mf['booklet']=dict(cover='media/v11-A03-aerial.png',pages=[],section_pages={});write(P/'manifest.json',mf)
# Explicitly partial modern matrix: no passing badge is manufactured for publication.
mat=read(R/'templates/design_depth_matrix.json');mat['schema_version']=2
for row in mat['rows']:
 row['status']='partial';row['drawings']=['drawings/a3-booklet.pdf','drawings/a0-board.pdf'];row['metrics']=[];row['decision']='Continuous living districts, independent production and a whole-site regional structure with explicit road/landscape diagrams';row['scope']={'extent':'Issued whole site and registered local enlargements/views','phase':'Conditional phases 1-3'};row['explanation']={'path':'proposal.md','heading':'## 2.'};row['gaps']=[dict(missing='Independent engineering, water/access rights, livelihoods and detailed crossing validation remain outstanding',next_step='Verify with source operators and licensed specialists before implementation',responsible='Jingyuan Huang and named specialist team to be appointed',kind='organiser_data')]
write(P/'design_depth_matrix.json',mat)
c=xc.compute_metrics(str(P));units={'master_area_km2':'km2','site_coverage_pct':'%','gfa_m2':'m2','far':'ratio','open_space_pct':'%','human_machine_interfaces':'count','shaded_pedestrian_pct':'%','structure_km2':'km2'}
metrics=[dict(key=k,value=c[k],unit=units[k],evidence='computed',computed_from='Current canonical geometry; system overlays overlap and are not summed as a base land account') for k in xc.COMPUTED_KEYS]
for key,val,unit,note in [('residents_phase1',ph[0]['total_residents'],'people','2.5 people per designed dwelling; conditional occupancy, not observed demand'),('dwellings_phase1',ph[0]['total_dwellings'],'dwellings','Geometry-linked dwelling design capacity'),('jobs_phase1',ph[0]['total_jobs'],'jobs','Uncontracted job-space design scenario'),('annual_water_demand_m3',raw['resources'][0]['water_gross_m3_y'],'m3/year','New programme gross demand scenario; existing fixed demand is additional and unverified'),('annual_fresh_requirement_m3',raw['resources'][0]['fresh_requirement_m3_y'],'m3/year','Scenario after reuse substitution and assumed losses; not a secured water right'),('residents_all_phases',ph[-1]['total_residents'],'people','Full-build-out scenario'),('dwellings_all_phases',ph[-1]['total_dwellings'],'dwellings','Full-build-out capacity'),('jobs_all_phases',ph[-1]['total_jobs'],'jobs','Design capacity, not signed jobs')]:metrics.append(dict(key=key,value=val,unit=unit,evidence='declared',note=note))
write(P/'metrics.json',dict(metrics=metrics,status='public_design_preview',phase_accounts='phasing_programme.json',resource_scenarios=raw['resources']))
ass=read(V9/'assumptions.json');write(P/'assumptions.json',dict(assumptions=[dict(id=f'V11-{i:02}',topic='Design scenario and verification',value=s,basis='Declared design scenario; not an organiser-confirmed parameter') for i,s in enumerate(ass['items'],1)]+[dict(id='V11-green',topic='Landscape graphics',value='Green lines indicate proposed walking/shade and dry-landscape roles, not existing planted forest or a new irrigation commitment',basis='Current geometry plus reviews/presentation-v11/concept-layers.geojson')]))
# Readable public statement, with current diagrams and current images only.
sections=[('1. Design thesis','Housing forms continuous precincts with daily services. A compact town centre supports shared public life. Computing, repair and utilities occupy a separate productive estate; proximity alone is not a benefit.'),('2. Full-site zoning','Six proposed regions cover the issued boundary: Z1 southwest urban/services; Z2 northwest agricultural research; Z3 northern energy research; Z4 central production/transfer; Z5 eastern gateway/logistics; Z6 southeast mountain stewardship. Gross regions are not construction land. Fixed pilot outlines remain unchanged. Base zoning and overlapping system context are separate accounts.'),('3. Regional movement','Primary and secondary corridor studies connect the southwest, northern service hub, conditional transfer sites and eastern gateway. Arrival and freight approaches remain unacquired studies. Terrain, channel crossings, rights and emergency operation require specialist design.'),('4. Complete urban layout','All three construction phases share continuous R precincts and C town centre. Designed full-build-out capacity is 10,240 dwellings and a 25,600 resident scenario at 2.5 people per dwelling; release is conditional on demand and resources. The separate P/S system is not moved beside housing to compose an image.'),('5. Streets and public transport','Primary/secondary distributors, local streets, a proposed passenger spine, public anchors and court routes are shown distinctly. The productive worker path parallels the service spine; yard-spur crossing control remains a design hold-point.'),('6. Landscape and shade','Dry parks, a source seasonal wash and proposed walking/engineered-shade links form the landscape diagram. Green symbols are not evidence of irrigated forest, lawns or permanent water. Targeted planting requires a verified reuse allocation.'),('7. Public space and services','Four education plots and phased daily-service anchors support the living district. The assumed full-build-out education need is 3,840 places and the design provides 4,320 places. Block-gate network walking tests do not establish safe door-to-door access.'),('8. A03 market commons','Public space in heat and Zonda wind is tested at the town centre: two long market/refuge halls, an 80 x 80 m commons and two open shade bands. Aerial and eye-level images share registered source cameras.'),('9. B03 compute and repair','Eight staged compute halls and four repair workshops occupy their own productive estate. IT expands through 2, 4 and 8 MW scenarios only after resource and demand gates. No unverified residential heat network is credited.'),('10. C03 seasonal wash edge','Dry-season visitor access uses an edge path and a removable shade point. Access closes on warnings. The image is a local visitor-edge crop of the larger seasonal-wash study, not a lake or a surveyed flood design.'),('11. Construction phases','Phase 1 independently operates housing, essential services and production. Phase 2 extends connected precincts only with demand and audited resource headroom. Phase 3 completes northern housing and activates the gateway only after its independent access, trade, utility and worker-welfare case.'),('12. Resources and livelihoods','The new Phase 1 programme has a declared fresh requirement of 409,590 m3/year. Fixed-pilot and existing living-quarter demand remain additional and unverified. Employment figures describe programme capacity, not contracted jobs or a demonstrated household income base.'),('13. Presentation and trade-off','The A0 uses spatial diagrams and concise phase cards, with no spreadsheet-style account. Detailed figures remain in the booklet and technical records. The scheme gives up maximum uninterrupted IT throughput and the shortest productive route to protect continuous public life and honest resource limits.'),('14. Review and disclosure','Jingyuan Huang authorised this public preview. Codex created the geometry, calculations, diagrams and layout; built-in image_gen.imagegen finished the selected source-controlled images, with exact model version unavailable. Images illustrate design, not measurements or approval. Original controls, prompts, cameras and rejected trials remain traceable. Automatic gates and independent design assessment are distinct; this draft is not submitted as approved.')]
md='# AGUA FINITA / V11 public design preview\n\n'+'\n\n'.join('## '+title+'\n\n'+body for title,body in sections)+'\n';(P/'proposal.md').write_text(md)
style='body{font:16px/1.7 Arial,sans-serif;color:#263c43;background:#faf8f2;margin:0}main{max-width:1160px;margin:auto;padding:32px}h1{font-size:40px;line-height:1.2}h2{margin-top:40px}img{max-width:100%;height:auto;display:block}figure{margin:28px 0}figcaption{font-size:13px;color:#68766f}.links{display:flex;gap:16px;flex-wrap:wrap}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}a{color:#805334}.note{border-left:4px solid #b57e5e;padding:12px 18px;background:#eee7d8}@media(max-width:700px){.pair{grid-template-columns:1fr}main{padding:18px}}'
body='<h1>AGUA FINITA</h1><p>V11 / Continuous living districts and independent production</p><p class="note">Authorised public design preview. The images and plans show a proposal; independent engineering, rights and design review remain open.</p><div class="links"><a href="../drawings/a3-booklet.pdf">23-page design booklet</a><a href="../drawings/a0-board.pdf">A0 spatial board</a><a href="../drawings/a3-technical-appendix.pdf">Technical appendix</a></div><figure><img src="../media/v11-A03-aerial.png" alt="Centre district local aerial"><figcaption>Centre district / local aerial. This camera frame does not define the whole-site design scope.</figcaption></figure>'
for i,(title,text) in enumerate(sections,1):
 body+='<section id="s'+str(i)+'"><h2>'+html.escape(title)+'</h2><p>'+html.escape(text)+'</p>'
 if i in [2,4,5,6]:
  name={2:'fig-01-structure.png',4:'fig-02-master-plan.png',5:'fig-04-movement.png',6:'fig-05-open-space-water.png'}[i];body+='<figure><img src="../figures/'+name+'" alt="'+html.escape(title)+'"><figcaption>Current geometry-based spatial diagram / symbols and widths are explanatory.</figcaption></figure>'
 if i in [8,9,10]:
  nid={8:'A03',9:'B03',10:'C03'}[i];body+='<div class="pair">'+''.join('<figure><img src="../media/v11-'+nid+'-'+v+'.png" alt="'+nid+' '+v+'"><figcaption>'+nid+' / '+v+' / AI-finished concept image from a geometry-derived control.</figcaption></figure>' for v in ['aerial','eye'])+'</div>'
 body+='</section>'
(P/'report/proposal.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AGUA FINITA / V11</title><style>'+style+'</style><main>'+body+'</main></html>')
with (P/'changelog.md').open('a') as f:f.write('\n## 2026-10-27 / V11 authorised public preview\n\nHuman explicitly authorised website updating after reviewing the finished views, then required no spreadsheet-style A0 table and restored spatial diagrams. V11 publishes the current PDFs, registered images, current canonical geometry/phase scenarios and a current English statement. Whole-site zoning, road hierarchy, public centres and dry-landscape/shade links remain coordinated. Numeric accounts remain in the booklet/technical records. No design approval or manufactured automatic pass is claimed.\n')
print('Public paths updated; compute metrics',c['master_area_km2'],ph[0]['total_residents'])
