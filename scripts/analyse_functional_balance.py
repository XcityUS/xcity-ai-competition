#!/usr/bin/env python3
"""Advisory spatial land account and programme thought-starter, never an approval/optimizer.
python scripts/analyse_functional_balance.py submissions/<login>/<slug> --out <directory>
Optional --programme scenario.json: explicit sourced/assumed inputs, no guessed defaults.
"""
import argparse,json,math
from pathlib import Path
from collections import defaultdict
from shapely.geometry import shape,mapping
from shapely import make_valid
from shapely.geometry.polygon import orient
from shapely.ops import transform,unary_union
from pyproj import Transformer,Geod
ROOT=Path(__file__).resolve().parents[1]
T=Transformer.from_crs(4326,32719,always_xy=True).transform
I=Transformer.from_crs(32719,4326,always_xy=True).transform
GEOD=Geod(ellps='WGS84')
GROUP={'solar_agriculture':'energy_compute','energy':'energy_compute','energy_compute':'energy_compute','compute':'energy_compute','agriculture':'agri_production','agri_production':'agri_production','housing':'living','residential':'living','mixed_use':'living','living':'living','industry':'industry','logistics':'trade_port','trade_port':'trade_port','ecology':'retained','reserve':'retained','fixed_context':'fixed_context'}
REPAIRS=[]
def load(p,repair=False):
 if not p.exists():return []
 result=[]
 for f in json.loads(p.read_text())['features']:
  g=shape(f['geometry'])
  if not g.is_valid:
   if not repair:raise ValueError(str(p)+': invalid geometry; use --repair-for-analysis for a disclosed in-memory diagnostic; source remains unchanged')
   REPAIRS.append({'file':str(p),'feature':f.get('properties',{}).get('id'),'action':'make_valid in memory only; diagnostic account, source not changed'});g=make_valid(g)
  result.append((transform(T,g),f.get('properties',{})))
 return result
def area(g):
 if g.is_empty:return 0.
 if g.geom_type=='Polygon':return abs(GEOD.geometry_area_perimeter(orient(transform(I,g),sign=1))[0])/1e6
 if hasattr(g,'geoms'):return sum(area(x) for x in g.geoms)
 return 0.
def analyse(scope,records):
 base=[(g,p) for g,p in records if p.get('plan_role')=='base_zoning'];over=[(g,p) for g,p in records if p.get('plan_role')=='system_overlay']
 groups=defaultdict(list);districts=[]
 for g,p in base:
  q=g.intersection(scope);use=p.get('primary_use','unmapped');grp=GROUP.get(use,'unmapped')
  groups[grp].append(q);districts.append({'id':p.get('district_id',p.get('id')),'name':p.get('name'),'primary_use':use,'comparison_group':grp,'area_km2':area(q),'whole_site_pct':100*area(q)/area(scope),'basis_ref':p.get('basis_ref')})
 union=unary_union([g for g,p in base]);fixed=unary_union(groups.get('fixed_context',[]));retained=unary_union(groups.get('retained',[]));alloc=scope.difference(fixed.union(retained))
 groupout={k:{'area_km2':area(unary_union(gs)),'whole_site_pct':100*area(unary_union(gs))/area(scope),'share_of_nonfixed_nonretained_pct':100*area(unary_union(gs).intersection(alloc))/area(alloc) if area(alloc) and k not in ['fixed_context','retained'] else None} for k,gs in groups.items()}
 overlays=defaultdict(list)
 for g,p in over:overlays[p.get('system','unmapped')].append(g.intersection(scope))
 return {'scope_km2':area(scope),'denominators':{'whole_site_km2':area(scope),'nonfixed_nonretained_km2':area(alloc),'note':'The second denominator is an accounting comparison only, not a buildable-land assessment.'},'districts':districts,'base_groups':groupout,'system_overlay_coverage':{k:{'area_km2':area(unary_union(gs)),'whole_site_pct':100*area(unary_union(gs))/area(scope)} for k,gs in overlays.items()},'geometry_findings':{'missing_base_zoning':not bool(base),'unallocated_km2':area(scope.difference(union)),'outside_scope_km2':area(union.difference(scope)),'overlap_excess_km2':max(0,sum(area(g) for g,p in base)-area(union))},'status':'advisory_not_design_approval'}
def programme_checks(data):
 """Demand-to-area arithmetic only, all drivers and their evidence are supplied."""
 out=[]
 specs=[('housing',['population','people_per_dwelling','floor_area_m2_per_dwelling','gross_far'],lambda v:v[0]/v[1]*v[2]/v[3]/1e6),('solar',['solar_mwp','gross_mwp_per_km2'],lambda v:v[0]/v[1]),('compute',['it_mw','it_mw_per_hall','hall_footprint_m2','campus_building_coverage'],lambda v:math.ceil(v[0]/v[1])*v[2]/v[3]/1e6)]
 for key,keys,calc in specs:
  missing=[k for k in keys if k not in data];vals=[]
  if not missing:
   for k in keys:
    d=data[k]
    if not isinstance(d,dict) or d.get('evidence') not in ['sourced','assumed','declared'] or not d.get('basis'):raise ValueError(k+': require value, evidence and basis')
    x=float(d['value'])
    if not math.isfinite(x) or x<=0:raise ValueError(k+': must be finite and positive')
    if k=='campus_building_coverage' and x>1:raise ValueError('coverage must be a fraction in (0,1]')
    vals.append(x)
  out.append({'function':key,'status':'missing_inputs' if missing else 'scenario_estimate_not_entitlement','missing':missing,'gross_area_estimate_km2':None if missing else calc(vals),'basis':'Supplied scenario arithmetic; education/health, operating yards, roads, water, grid, terrain and engineering require separate reconciliation.'})
 return out
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('package',type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--programme',type=Path);ap.add_argument('--repair-for-analysis',action='store_true');a=ap.parse_args()
 if a.out.resolve()==a.package.resolve() or a.package.resolve() in a.out.resolve().parents:raise ValueError('Write analysis outside the submission package to avoid changing its publication fingerprint.')
 scope=unary_union([g for g,p in load(ROOT/'brief/site-package/boundaries/scope_9_13.geojson')]);records=load(a.package/'geometry/structure.geojson',a.repair_for_analysis);r=analyse(scope,records);ref=json.loads((ROOT/'brief/functional-balance-reference.json').read_text());r['reference']=ref;r['analysis_only_repairs']=REPAIRS
 r['reference_comparison']=[{'system':k,'reference_pct':v,'base_land_pct':r['base_groups'].get(k,{}).get('whole_site_pct',0),'interpretation':'Diagnostic juxtaposition only: exclusive land and overlapping system weight are different measures. No pass/fail tolerance.'} for k,v in ref['reference_pct'].items()]
 r['programme_checks']=programme_checks(json.loads(a.programme.read_text()) if a.programme else {})
 r['agent_questions']=['Which areas are strategic allocations, serviced plots, actual footprints, or expansion reserve? Map each separately.','How do solar generation and forage/jojoba share the same ground without double-counting the base account?','Why do production/logistics districts need their allocated scale? Show facility throughput, land intensity, access and phase, or identify conditional reserve.','Does population follow credible jobs and resources, with schools, health, shops and transport before occupancy?','Which candidate distribution changes a real spatial/resource trade-off? Compare it with the reference without treating a percentage as a layout.','Where do primary/secondary routes serve centres and cross source channels? Do not infer engineering from this account.']
 a.out.mkdir(parents=True,exist_ok=True);(a.out/'functional-balance.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 md='# Functional balance / advisory review\n\nWhitepaper V7 page 5 reference: 60 / 30 / 5 / 3 / 2. Not five compulsory land quotas. Current issued boundary controls; older absolute quantities do not transfer.\n\n| Base-land group | Area km2 | Whole-site share | Nonfixed/nonretained share |\n|---|---:|---:|---:|\n'
 for k,d in r['base_groups'].items():md+=f"| {k} | {d['area_km2']:.3f} | {d['whole_site_pct']:.2f}% | "+('n/a' if d['share_of_nonfixed_nonretained_pct'] is None else f"{d['share_of_nonfixed_nonretained_pct']:.2f}%")+' |\n'
 md+='\nAnalysis-only geometry repairs (source files unchanged): '+json.dumps(r['analysis_only_repairs'])+'\n\nThe second denominator does not establish buildability. Overlapping system coverage is reported separately in JSON and must not be summed with base land.\n\n## Geometry findings\n\n'+json.dumps(r['geometry_findings'],indent=2)+'\n\n## Decisions the agent must explain\n\n'+'\n'.join('- '+q for q in r['agent_questions'])+'\n\n## Programme scenarios\n\n'+json.dumps(r['programme_checks'],indent=2)+'\n'
 (a.out/'functional-balance.md').write_text(md)
 print(json.dumps({'output':str(a.out),'scope_km2':r['scope_km2'],'findings':r['geometry_findings'],'status':r['status']}))
if __name__=='__main__':main()
