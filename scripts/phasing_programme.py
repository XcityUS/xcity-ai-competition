"""Construction programme data checks; never assess design quality."""
import json,math
from pathlib import Path

def assess(package):
 p=Path(package);errors=[]
 try:d=json.loads((p/'phasing_programme.json').read_text())
 except (OSError,ValueError):return ['Missing/invalid phasing_programme.json; use the template and provide actual phase/zone capacity and sequence data']
 if not isinstance(d,dict):return ['Programme must be a JSON object']
 if d.get('schema_version')!=1:errors.append('Programme schema_version must be 1')
 phases=d.get('phases',[])
 if not isinstance(phases,list) or not all(isinstance(x,dict) for x in phases):return ['Programme phases must be objects']
 if len(phases)!=3 or {x.get('phase') for x in phases}!={1,2,3}:return ['Programme must contain phases 1, 2 and 3 exactly once']
 for key in ['map','a0_board']:
  rel=d.get(key,'')
  if not rel or Path(rel).is_absolute() or '..' in Path(rel).parts or not (p/rel).is_file():errors.append('Programme '+key+' must reference an existing safe package file')
 try:geometry=json.loads((p/'geometry/phasing.geojson').read_text())['features']
 except (OSError,ValueError,KeyError):return errors+['Missing phasing geometry']
 cumulative={};first_low=0;first_high=0;programme_pairs=set()
 for phase in sorted(phases,key=lambda x:x['phase']):
  n=phase['phase']
  for k in ['period','objective','trigger']:
   v=phase.get(k)
   if not isinstance(v,str) or len(v.strip())<5 or '{{' in v:errors.append('Phase %s needs actual %s'%(n,k))
  for k in ['works','sequence_dependencies']:
   if not isinstance(phase.get(k),list) or not phase[k] or any(not isinstance(v,str) or '{{' in v for v in phase[k]):errors.append('Phase %s needs actual %s'%(n,k))
  zones=phase.get('zones',[]);seen=set()
  if not isinstance(zones,list) or not all(isinstance(x,dict) for x in zones):errors.append('Phase %s zones must be objects'%n);continue
  if not zones:errors.append('Phase %s has no zone programme'%n)
  for z in zones:
   zid=z.get('zone_id');label='Phase %s zone %s'%(n,zid)
   if not isinstance(zid,str):errors.append(label+': zone ID must be a string');continue
   if not zid or zid in seen:errors.append(label+': missing/duplicate ID')
   seen.add(zid);programme_pairs.add((n,zid))
   if not any(f.get('properties',{}).get('zone_id')==zid and f['properties'].get('phase')==n for f in geometry):errors.append(label+': no matching phasing geometry zone_id/phase')
   if not isinstance(z.get('basis'),str) or len(z['basis'])<10 or '{{' in z['basis']:errors.append(label+': provide capacity basis')
   for item in ['residents','dwellings','jobs']:
    add=z.get('new_'+item);total=z.get('cumulative_'+item);prior=cumulative.get((zid,item),0)
    def bounds(v):
     if isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0:return (v,v)
     if isinstance(v,dict) and set(v)=={'min','max'} and all(isinstance(v[k],(int,float)) and not isinstance(v[k],bool) and math.isfinite(v[k]) for k in v) and 0<=v['min']<=v['max']:return (v['min'],v['max'])
    a,b=bounds(add),bounds(total)
    if a is None or b is None:errors.append(label+': '+item+' needs non-negative new/cumulative numbers or min/max ranges');continue
    old=bounds(prior)
    if any(abs(old[i]+a[i]-b[i])>0.01 for i in [0,1]):errors.append(label+': '+item+' additions do not reconcile to cumulative values')
    cumulative[zid,item]=total
    if n==1 and item=='residents':
     first_low+=b[0];first_high+=b[1]
 try:
  metrics=json.loads((p/'metrics.json').read_text())['metrics']
  residents=next(m['value'] for m in metrics if m['key']=='residents_phase1')
  if not isinstance(residents,(int,float)) or not first_low<=residents<=first_high:errors.append('Phase-one residents do not reconcile with metrics.json residents_phase1')
 except (OSError,ValueError,KeyError,StopIteration):errors.append('Missing residents_phase1 metric for programme reconciliation')
 for feature in geometry:
  props=feature.get('properties',{})
  if props.get('status')=='fixed_context':continue
  if (props.get('phase'),props.get('zone_id')) not in programme_pairs:errors.append('A mapped phase zone is absent from the programme: '+str(props.get('zone_id')))
 # Feasibility, A0 layout and scenario assumptions require independent review.
 return errors
