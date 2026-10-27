"""Whitepaper-led territorial correction; preserves fixed pilots and detailed V3 works."""
from pathlib import Path
import json,shutil,hashlib
from collections import defaultdict
from shapely.geometry import shape,mapping,Polygon,LineString,box
from shapely.ops import transform,unary_union,substring
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/functional-v4';O.mkdir(exist_ok=True);A=O/'before';A.mkdir(exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:[(transform(T,shape(x['geometry'])),x['properties']) for x in json.loads(f.read_text())['features']]
for n in ['geometry/structure.geojson','geometry/movement.geojson','reviews/redesign-v2/design-account.json','proposal.md','drawings/a3-booklet.pdf','drawings/a0-board.pdf']:
 dest=A/n;dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():shutil.copy2(P/n,dest)
old={p['id']:g for g,p in load(A/'geometry/structure.geojson')};scope=unary_union([g for g,p in load(R/'brief/site-package/boundaries/scope_9_13.geojson')]);remaining=scope;records=[]
land=load(P/'geometry/land_use.geojson');master=unary_union([g for g,p in load(P/'geometry/master_area.geojson')]);roads=load(A/'geometry/movement.geojson');routes={p.get('id'):g for g,p in roads if g.geom_type=='LineString'}
def take(g,id,name,use,system,logic,role='base_zoning'):
 global remaining
 q=(g.intersection(remaining) if role=='base_zoning' else g.intersection(scope)).buffer(0)
 if role=='base_zoning':remaining=remaining.difference(q)
 if not q.is_empty:records.append((q,dict(id=id,district_id=id,name=name,primary_use=use,system=system,plan_role=role,basis_ref='proposal.md#territorial-districts',edge_logic=logic,area_km2=q.area/1e6,status='fixed_context' if id.startswith('D00') else 'declared_conditional_allocation_not_installed')))
 return q
for id,name,use,sys,why in [('D00-F','Fixed agrivoltaic pilot','fixed_context','agri_production','Exact issued boundary; forage and jojoba retained; no redesign or new capacity credited.'),('D00-L','Fixed living pilot','fixed_context','living','Exact issued living outline; no redesign.'),('D07','Mountain stewardship','ecology','reserve','Retained source-DEM steep/high terrain interpretation; not reclassified as energy to meet a target.'),('D06','Drainage and dry landscape links','reserve','reserve','Retained seasonal-drainage/landscape account; not a lake or statutory exclusion; detailed suitability remains unresolved.')]:take(old[id],id,name,use,sys,why)
# Gateways shrink from a 292km2 eastern region to two approach-based reservations.
west=take(Polygon([(567000,6553900),(569200,6553200),(573000,6556000),(572500,6559800),(570000,6559600),(567000,6556500)]),'D05-W','Western arrival and trade reserve','logistics','port','Western approach to retained SW public/regional spine; angular edge is an entrant service boundary, not cadastre. First gate is access-only; no customs or throughput entitlement.')
east=take(Polygon([(610200,6572500),(613500,6572200),(615000,6575500),(612000,6577800),(610200,6576500)]),'D05-E','Eastern domestic transfer reserve','logistics','port','Compact junction of regional east-west spine and south-east branch. Domestic consolidation only; does not claim a Chilean border port or approved highway connection.')
town=box(573400,6554300,575800,6556700)
living=old['D01'].intersection(Polygon([(560000,6540000),(580800,6540000),(578600,6558000),(572000,6560300),(560000,6559800)])).difference(master).union(town)
take(living,'D01','Southwest living and civic territory','mixed_use','living','Compact town plus future public-service catchment at SW arrival. Northeast service limit is pulled back from prior basin; excludes separate works/farm parcels. Only the existing 5.76km2 town carries population capacity.')
industry=substring(routes['REGIONAL-2'],0,15500).simplify(450).buffer(1600,cap_style=2,join_style=2).difference(master)
take(industry,'D04','Central processing and repair corridor','industry','energy_compute','A declared 3.2km-wide operating corridor along the first15.5km of the proposed central transfer route. Replaces 252km2 general industry. Width is a service-envelope choice, not a road ROW or buildable-area result; no new operating capacity credited.')
local_ag=unary_union([g for g,p in land if p.get('programme_use',p['use'])=='agriculture'])
ag=old['D02'].union(Polygon([(575000,6558500),(581500,6558000),(586800,6566500),(584000,6574500),(580000,6578000)])).union(local_ag).union(Polygon([(580000,6575000),(587500,6575000),(588000,6583000),(582000,6585000)]))
ag=take(ag,'D02','Western and central agricultural territory','agriculture','agri_production','Western alluvial-fan study expanded into the central valley/service catchment released from general industry. Edges follow declared field-service envelopes; soils, lawful irrigation and flood design must qualify actual fields. Not all land is irrigated.')
energy=remaining
south=take(energy.intersection(old['D01'].union(master)),'D03-S','Southern energy and compute works','energy','energy_compute','Separate existing proposed compute and solar parcels south of town; land released from the old living basin remains an energy/service study, not housing capacity.')
north=take(remaining.intersection(old['D03']),'D03-N','Northern solar-energy territory','energy','energy_compute','Retains northern shoulder allocation served by northern route study. No cultivation credit without a separate crop/water design.')
central=take(remaining,'D03-E','Central and eastern energy territory','energy','energy_compute','Released former oversized industrial/logistics regions now form the main conditional solar-energy/service territory, outside retained mountain/drainage units. Future field subdivisions follow access/drainage studies; polygon area is neither panel area nor power capacity.')
# Co-use candidate ends at the northern western-field service limit; geometry is NOT panel infill.
dual=ag.intersection(box(540000,6500000,640000,6588000));fixedag=old['D00-F'];fixedliving=old['D00-L']
functions={'energy_compute':energy.union(dual).union(fixedag),'agri_production':ag.union(fixedag),'living':living.intersection(scope).difference(west.union(east)).difference(old['D07'].union(old['D06'])).union(fixedliving),'industry':industry.intersection(scope).difference(unary_union([g for g,p in records if p['id'] not in ['D04','D03-S','D03-N','D03-E','D02']])),'port':west.union(east)}
# Use the exclusive records, not original candidates, to avoid double-counting in coverage.
by={p['id']:g for g,p in records};functions['living']=by['D01'].union(fixedliving);functions['industry']=by['D04'];functions['agri_production']=by['D02'].union(fixedag)
for sys,g in functions.items():take(g,'F-'+sys,'Functional coverage / '+sys,'functional_coverage',sys,'Overlapping strategic coverage, not added to exclusive base land. Energy includes fixed agrivoltaics and the declared southern/central shared field-service envelope.',role='system_overlay')
# Only these lines are new. They join exact existing route vertices; neither is an approved built road.
for id,line in [('V4-WEST-GATE',LineString([(570222.4,6556323.7),(569200,6556000)])),('V4-EAST-GATE',LineString([(611622.4,6574023.7),(612500,6575000)]))]:roads.append((line.intersection(scope),dict(id=id,name='Gateway service link study',road_class='secondary',network='shared',width_m=24,phase=3,study_only=True,secured=False,basis='Declared spur from actual retained route vertex to compact gateway reserve; rights, terrain and crossings unverified.')))
def write(f,rs):
 def encoded(g):
  q=transform(I,g)
  return mapping(q.buffer(0) if q.geom_type in ['Polygon','MultiPolygon'] and not q.is_valid else q)
 f.write_text(json.dumps(dict(type='FeatureCollection',features=[dict(type='Feature',geometry=encoded(g).copy() if p.get('id')!='D03-E' else mapping(transform(I,g).buffer(0).buffer(-1e-10)),properties=p) for g,p in rs]),ensure_ascii=False,separators=(',',':'))+'\n')
write(P/'geometry/structure.geojson',records);write(P/'geometry/movement.geojson',roads)
base=[(g,p) for g,p in records if p['plan_role']=='base_zoning'];un=unary_union([g for g,p in base]);assert scope.difference(un).area<.1;assert sum(g.area for g,p in base)-un.area<.1
account=json.loads((P/'reviews/redesign-v2/design-account.json').read_text());account.update(regions=[p for g,p in base],whole_site_km2=scope.area/1e6,base_gap_m2=scope.difference(un).area,base_overlap_m2=max(0,sum(g.area for g,p in base)-un.area));(P/'reviews/redesign-v2/design-account.json').write_text(json.dumps(account,indent=2))
basegroups=defaultdict(float)
for g,p in base:
 group={'D00-F':'agri_production','D00-L':'living','D07':'retained','D06':'retained','D01':'living','D02':'agri_production','D04':'industry','D05-W':'port','D05-E':'port'}.get(p['id'],'energy_compute');basegroups[group]+=g.area/1e6
coverage={s:dict(km2=g.area/1e6,pct=g.area/scope.area*100) for s,g in functions.items()}
audit=dict(version='V4',scope_km2=scope.area/1e6,reference_pct=dict(energy_compute=60,agri_production=30,living=5,industry=3,port=2),exclusive_including_fixed={s:dict(km2=v,pct=v/(scope.area/1e6)*100) for s,v in basegroups.items()},functional_coverage=coverage,solar_agriculture_overlap_km2=functions['energy_compute'].intersection(functions['agri_production']).area/1e6,retained_km2=basegroups['retained'],new_works_scope_km2=account['master_km2'],net_new_crop_ha=7.656,new_crop_irrigation_m3y=22968,local_capacity_change=False,method='UTM19S planar geometry; official advisory tool additionally computes geodesic figures. Strategic coverage overlaps; gross allocations are not installed fields or capacity.',resource_gate='The new shared-field candidate excludes the fixed pilot and is not planted or commissioned. At a declared35% crop-net/gross ratio and3000m3/ha/year blended trial allowance, fully cultivating it would need roughly'+str(round(dual.area/1e6*.35*100*3000/1e6,1))+' million m3/year additional indicative water, not included in current town demand and not secured.',fixed_pilots_unchanged=True)
(O/'functional-account.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
# Register the actual source without uploading the entire supplied whitepaper.
src=json.loads((P/'sources.json').read_text());src['sources']=[s for s in src['sources'] if s['id']!='SRC-WHITEPAPER-V7'];src['sources'].append(dict(id='SRC-WHITEPAPER-V7',title='XCITY Whitepaper V7, page5',publisher='XCITY',url='https://github.com/XcityUS/xcity-ai-competition/blob/main/brief/functional-balance-reference.json',accessed='2026-10-27',used_for='Five-function approximate60/30/5/3/2 programme; supplied PDF directly inspected. Older absolute areas are not transferred.',licence='User-supplied source; only short factual programme paraphrase, no reproduced artwork.'));(P/'sources.json').write_text(json.dumps(src,indent=2)+'\n')
a=json.loads((P/'assumptions.json').read_text());a['assumptions']=[x for x in a['assumptions'] if x['id']!='V4-FUNCTIONAL'];a['assumptions'].append(dict(id='V4-FUNCTIONAL',topic='Territorial allocation and resource gates',value='Five functions compared with whitepaper;21% terrain/drainage retained; overlapping agrivoltaic coverage not installed.',basis='Explicit V4 envelope design, functional-account.json; northern shared-field boundary follows declared6588km UTM service limit, not measured suitability or an installation schedule. No new population, MW or yield capacity.'));(P/'assumptions.json').write_text(json.dumps(a,indent=2))
