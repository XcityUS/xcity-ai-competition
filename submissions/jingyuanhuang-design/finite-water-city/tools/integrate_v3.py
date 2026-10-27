"""Integrate the user's whole-site revision, preserving the previous submitted version."""
import json,sys,re,shutil
from pathlib import Path
from shapely.geometry import shape,mapping,Point,LineString
from shapely.ops import unary_union,transform,nearest_points
from shapely import make_valid
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];V=P/'reviews/whole-site-v3';B=V/'previous-submitted';sys.path.insert(0,str(R/'scripts'));import xcity_common as xc
B.mkdir(exist_ok=True)
for n in ['geometry','manifest.json','metrics.json','assumptions.json','proposal.md','changelog.md','README.md']:
 src=P/n;dst=B/n
 if dst.exists():continue
 if src.is_dir():shutil.copytree(src,dst)
 else:shutil.copy2(src,dst)
read=lambda p:json.loads(p.read_text())
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda n:read(B/'geometry'/f'{n}.geojson')['features']
vp=read(V/'structure.geojson')['features'];routefs=read(V/'corridors.geojson')['features'];centres=read(V/'centres.geojson')['features']
fixed=unary_union([shape(f['geometry']) for f in vp if f['properties']['system'].startswith('fixed')])
oldmaster=unary_union([shape(f['geometry']) for f in load('master_area')]);newmaster=unary_union([shape(f['geometry']) for f in read(V/'master_study.geojson')['features']]+[oldmaster]).difference(fixed)
# Preserve the complete original neighbourhood including all public node grounds; extend to a source-shaped planning envelope.
master=make_valid(newmaster)
def clean(g):
 q=make_valid(g)
 if q.geom_type=='GeometryCollection':q=unary_union([p for p in q.geoms if p.geom_type in ['Polygon','MultiPolygon']])
 return q
def ft(g,**p):return dict(type='Feature',geometry=mapping(clean(g)),properties=p)
fc=lambda fs:dict(type='FeatureCollection',features=fs)
write(P/'geometry/master_area.geojson',fc([ft(master,name='South-west city planning envelope; initial neighbourhood plus conditioned expansion',status='Full site-derived envelope; only the first neighbourhood has detailed building design')]))
# Crosswalk to competition vocabulary. Screening remains explicit in properties rather than masquerading as law.
keys={'fixed_agri':'agri_production','fixed_living':'living','protect':'reserve','wash':'reserve','floodstudy':'reserve','dry':'reserve','town':'living','compute':'energy_compute','gateway':'port','localindustry':'industry','energy':'energy_compute','agri':'agri_production'}
sf=[]
for f in vp:
 p=f['properties'];g=shape(f['geometry']);k=p['system'];new=dict(p,system=keys[k],screening_class=k,status='fixed organiser condition' if k.startswith('fixed') else 'proposed conditional reservation')
 if k=='floodstudy':new['restriction']='DEM sensitivity screening, not confirmed permanent no-build designation'
 if k=='gateway':
  # Shared gateway site: meaningful land account for port and export manufacturing without double counting.
  u=transform(t,g);x0,y0,x1,y1=u.bounds
  from shapely.geometry import box
  cut=u.intersection(box(x0-10,y0-10,x1+10,y0+(y1-y0)*.45));other=u.difference(cut)
  for piece,sysid in [(cut,'industry'),(other,'port')]:
   if not piece.is_empty:sf.append(ft(transform(inv,piece),**dict(new,system=sysid,name='Eastern shared gateway / '+sysid)))
 else:sf.append(ft(g,**new))
write(P/'geometry/structure.geojson',fc(sf))
# Local detailed land use retained, broader envelope explicitly counted as future reserve.
lf=[];covered=[]
for f in load('land_use'):
 g=shape(f['geometry']).intersection(master)
 if not g.is_empty:lf.append(ft(g,**f['properties']));covered.append(g)
remainder=master.difference(unary_union(covered));lf.append(ft(remainder,use='reserve',name='Conditional northward expansion / no buildings committed',phase=2))
write(P/'geometry/land_use.geojson',fc(lf))
# Existing neighbourhood remains the complete first build; wider urban envelope is not its construction footprint.
phase1=oldmaster.intersection(master)
phase2=master.difference(phase1)
for f in vp:
 if f['properties']['system']=='town' and not f['properties']['name'].startswith('D '):phase2=phase2.union(shape(f['geometry']))
phase2=phase2.difference(phase1)
phase3=unary_union([shape(f['geometry']) for f in vp if f['properties']['system']=='gateway' or (f['properties']['system']=='town' and f['properties']['name'].startswith('D '))]).difference(phase1)
write(P/'geometry/phasing.geojson',fc([ft(phase1,phase=1,name='Independent first neighbourhood and regional access works'),ft(phase2,phase=2,name='Conditioned urban and productive expansion',trigger='Twelve months audited 20% reliable-water headroom; 80% occupancy; each extension has funded services, processing and safe access'),ft(phase3,phase=3,name='Eastern gateway and industry',trigger='Hydraulic and road engineering accepted; binding trade demand; lawful reliable water and power; own services and emergency access funded')]))
# Proposed regional corridors are drawn as machine/emergency connections, not shaded pedestrian streets.
mov=load('movement');mov +=[ft(shape(f['geometry']),**dict(f['properties'],network='machine',shaded=False,kind='regional_corridor',width_m=8)) for f in routefs]
# Connect the original neighbourhood service edge to A: its geometry is part of the same regional graph.
a=next(shape(f['geometry']) for f in centres if f['properties']['id']=='A');target=Point(*t(a.x,a.y));start=Point(574750,6554900)
link=LineString([start,target]);scope=transform(t,xc.site_boundary())
assert scope.covers(link)
# Already present in routefs; do not duplicate.
# Reconcile any new crossings with existing public paths, preserving existing points.
public=unary_union([shape(f['geometry']) for f in mov if f['properties'].get('network') in ['people','shared']]);machine=unary_union([shape(f['geometry']) for f in mov if f['properties'].get('network')=='machine']);inter=public.intersection(machine)
existing=[shape(f['geometry']) for f in mov if f['properties'].get('kind')=='interface']
def points(g):
 if g.geom_type=='Point':yield g
 elif hasattr(g,'geoms'):
  for z in g.geoms:yield from points(z)
for p in points(inter):
 if all(transform(t,p).distance(transform(t,q))>.1 for q in existing):
  mov.append(ft(p,kind='interface',name='New regional route crossing / pedestrian priority',control='Stop-gated crossing; detail and accessibility before construction'));existing.append(p)
write(P/'geometry/movement.geojson',fc(mov))
# Correct the energy definition to the brief's share of completely matched hours.
er=read(P/'tools/energy_result.json');metrics=read(B/'metrics.json');computed=xc.compute_metrics(str(P))
for m in metrics['metrics']:
 if m['key'] in computed:m['value']=computed[m['key']]
 if m['key']=='hourly_cfe_match_pct':m.update(value=er['hourly_cfe_match_pct'],evidence='computed',computed_from='tools/hourly_dispatch.csv',note='Fraction of 8760 hours with zero unmatched grid import; synthetic scenario, not measured performance')
 if m['key']=='machine_traffic_rule':m['note']=f"Separate public paths and regional/service corridors; {computed['human_machine_interfaces']} registered gated interfaces"
write(P/'metrics.json',metrics)
manifest=read(B/'manifest.json');manifest.update(updated='2026-10-26',package_state='draft',summary='A whole-site network of four conditional towns, productive energy/compute corridors and an eastern gateway grows only with verified water. Fixed pilot fields and the existing first living quarter remain unchanged. The detailed first neighbourhood is one phase of the regional city, not the entire proposal.')
manifest['autonomy']['human_role']+=' On 2026-10-26 the human requested a whole-site redesign under the updated brief, questioned the excessive flood reserve depiction and directed Codex to revise only this entry while other agents handle repository rules. V3 distinguishes flood screening from permanent restrictions. The human has not yet reviewed the integrated V3 package.'
manifest['design_depth']['tier1_structure']['evidence'] +=['reviews/whole-site-v3/01_whole_site_plan.png','reviews/whole-site-v3/02_corridors_and_phases.png','reviews/whole-site-v3/corridors.geojson']
manifest['booklet']['cover']='reviews/whole-site-v3/01_whole_site_plan.png'
manifest['booklet']['pages']=[dict(path='reviews/whole-site-v3/'+n+'.png',after='idea',title=l) for n,l in [('01_whole_site_plan','Whole-site structure: fixed conditions and conditional growth'),('02_corridors_and_phases','Regional links and hydraulic study sections'),('03_source_geometry','Source boundary and southwest study envelope')]]+[p for p in manifest['booklet']['pages'] if p['path']=='pages/water-covenant.png']
write(P/'manifest.json',manifest)
ass=read(B/'assumptions.json')
for r in ass.get('assumptions',[]):
 if r['id']=='A-FLOOD':r['value']='Existing permanent buildings retain conservative exclusion of mapped flood band plus 30 m and channels plus 150 m. Whole-site flood-sensitive screening is shown separately from mountain/flow corridors; it is not a confirmed legal no-build boundary.'
 if r['id']=='A-ACCESS':r['value']='Retire the arbitrary 80 km external road allowance. Regional RN40 approach shown as unverified directional context; internal candidate corridors are measured in the V3 GeoJSON. Actual external route, easements and cost remain phase-one prerequisites.'
 if r['id']=='A-GROWTH':r['value']='Four conditional town reservations A/B/C/D plus the fixed first living quarter; only the detailed first neighbourhood has 960 proposed dwellings / 2400 residents. No 7200-person whole-site ceiling or final regional population is asserted.'
ass['assumptions'].append(dict(id='A-V3',topic='Whole-site planning screen',value='300m block-mean DEM; mountain/steep screen slope >=5% or elevation >=850m; channel research corridor 150m each side; four towns and two compute reservations clipped by conservative flood and terrain screens.',basis='Regional design choices, not statutory restrictions; the source flood band is a sensitivity screen. Eastern gateway strict-screen candidate about 2.64 km2 remains below the brief\'s about 7km2 intent. Regional capacity, fixed living-quarter demand, water sources, road engineering and resources remain unverified.'))
write(P/'assumptions.json',ass)
sources=read(P/'sources.json')
for r in sources['sources']:
 if r['id']=='SRC-PILOT':r.update(title='Fixed agrivoltaic fields and first living quarter',accessed='2026-10-26',used_in=['pilot-area/pilot_area.geojson','pilot-area/pilot_living_area.geojson'])
write(P/'sources.json',sources)
proposal=(B/'proposal.md').read_text()
proposal=proposal.replace('Cuenca Uno, Dos and Tres for its three conditional settlements','A–D for four conditional town reservations and K1/K2 for two productive compute clusters')
old=next(x for x in proposal.split('\n\n') if x.startswith('The master area is a declared'))
proposal=proposal.replace(old,f'''The current scheme covers the whole owner-defined site through a connected settlement and production structure. It preserves both the three fixed agrivoltaic fields and the newly published 2.48 km2 fixed first living quarter; the latter is a separate southern location, not our proposed housing. No layouts inside either fixed component are redesigned [SRC-PILOT]. The southwest master-planning envelope has a recomputed geodesic area of {computed['master_area_km2']:.2f} km2. It joins the original detailed neighbourhood and wash park to a source-shaped northern expansion study, clipped by site, pilot, terrain and channel conditions. The old 4 by 3 km rectangle is retained only as a historical phase-one study footprint, not the overall master boundary. Existing detailed building footprints are retained; added master land is explicitly future reserve, not a claim of completed block design or present construction.

The DEM-derived flood-sensitive band is a screening layer, not a lake and not a verified permanent no-build boundary. The regional diagram separates mountain/steep-ground study, channel-flow research corridors and sensitivity screening. Regional slope >=5% or elevation >=850m and 150m channel offsets are declared conservative design assumptions [A-V3], not statutory limits. Our existing permanent buildings retain the stricter flood-band-plus-30m and channel-plus-150m screening [A-FLOOD]. Smaller washes and upstream catchments require survey and hydraulic study. Conditional uses in the wider sensitivity band must be justified before any permanent development.''')
old=next(x for x in proposal.split('\n\n') if x.startswith('Our reproducible 8,760-hour model'))
proposal=proposal.replace(old,f'''Our reproducible 8,760-hour model uses synthetic solar output, annual 25% capacity factor, seasonal variation and recurring dust events. M1 is now correctly reported as {er['hourly_cfe_match_pct']:.3f}%: the share of all 8760 hours whose entire load is covered in that same hour without unmatched grid imports. The battery starts at its protected reserve, so unverified initial energy cannot support the claim. The separate energy-weighted supply share is {er['cfe_energy_share_pct']:.3f}%; it is not M1. Unmatched imports receive no carbon-free credit. This is a synthetic scenario, not measured performance or certification [A-ENERGY; S-CFE].''')
start=proposal.index('Phase one includes the whole detailed master area');end=proposal.index('Four irreversible commitments',start)
proposal=proposal[:start]+'''Phase one comprises the existing detailed first neighbourhood: 960 proposed dwellings, a school, clinic, daily shops, shaded public routes, local compute/repair/drying, water treatment and first access works. The broader master envelope is not all phase-one construction. The fixed southern first living quarter remains unchanged and separate: its proposed approximately 15.8 km regional connection is a transport link, not a walking service radius. Its existing population and demand have not been supplied and are not invented or counted inside our 2400 new-resident target. Its own services and resource balance must be confirmed independently before any integrated expansion commitment.

The first access links the western boundary to A and the initial neighbourhood; the southern connection ties in the fixed living quarter. The old arbitrary 80 km external road allowance is retired. The RN40 dotted approach is directional context only, with no assertion of road rights, construction alignment or cost. Internal regional candidate routes use 300m minimum-cost terrain screening; they identify study corridors, not designed roads. Flood-sensitive segments are marked for hydraulic and bridge/route comparison. Every phase requires lawful reliable water, engineered access, power, emergency provision and service escrow before occupation [A-ACCESS; A-V3].

Phase two opens the southwest urban reserve and the western/northern production branches progressively, followed by B and C only when twelve months of audited reliable-water headroom exceed contracted demand by 20%, prior occupancy reaches 80%, local services and maintenance are funded, and safe access is verified. K1/K2 are conditional compute and maintenance clusters linked to energy-priority composite production land. Regional power, telecom and water co-location is a reservation strategy, not a confirmed water source or pressure design. Each town has its own repair, processing and delivery provision; none relies on the eastern export gateway for everyday operation.

Phase three opens D and E via the northern foot-of-mountain corridor only after accepted hydraulic/road studies, binding trade demand, verified water/power headroom and funded local services. The eastern port and export-industry study shares one reservation; the strict regional screen currently yields only about 2.64 km2, below the brief's approximately 7 km2 intent. This is a declared design issue requiring an eastern-wing terrace and flood-screen reassessment, not a claim that the requirement has been fully resolved. Four conditional towns and the fixed first living quarter form the whole-site structure. The earlier three-town / 7200-resident ceiling is withdrawn: no regional build-out population is inferred from coloured land reservations [A-GROWTH].

'''+proposal[end:]
# Replace obsolete V2 addendum rather than leaving competing current diagrams in the narrative.
idx=proposal.find('### Layout clarification')
if idx<0:idx=proposal.find('## Layout clarification')
if idx>=0:proposal=proposal[:idx]
proposal+='''\n\n### Current regional revision · 2026-10-26\n\nThe V3 diagrams supersede V2 regional layouts and the previous reserve depiction. A is the southwest main town; B the northwest production settlement; C the northern farm-service town; D the eastern service town; E the eastern trade/industry gateway; K1/K2 the productive compute clusters. Fixed fields and the fixed southern living quarter are separate organiser conditions. Coloured areas express functional priority and conditional land reservations, not installed solar, irrigated land or built-up city. The wider urban envelope still requires street/block and resource capacity development; the node illustrations show the retained initial neighbourhood rather than the entire 1656 km2 city.\n\n![Whole-site V3 structure](reviews/whole-site-v3/01_whole_site_plan.png)\n\n![V3 regional corridors and phasing](reviews/whole-site-v3/02_corridors_and_phases.png)\n'''
(P/'proposal.md').write_text(proposal)
(P/'changelog.md').write_text((B/'changelog.md').read_text()+'''\n\n## 2026-10-26 — V3 whole-site revision\nHuman requested our scheme be revised while other agents amend repository rules. Adopted connected whole-site structure, separate fixed living quarter, conditional four-town/two-compute/gateway system; distinguished flood sensitivity from permanent protection; replaced rectangular master boundary with wider source-shaped planning envelope, retaining initial buildings and declaring future-reserve depth. Regional routes/phasing and computed metrics reconciled. Corrected M1 to fully matched hours with reserve-only initial battery. Retired arbitrary 80km access and 7200-resident regional ceiling. Previous submitted inputs archived under reviews/whole-site-v3/previous-submitted. No public push in this revision.\n''')
print(json.dumps(computed,indent=2));print('Integrated V3, interfaces',len(existing))
