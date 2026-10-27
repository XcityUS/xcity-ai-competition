"""Resource-conditional territorial agrivoltaic field layout; not installed capacity."""
import json,runpy,math
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import box,LineString,mapping
from shapely.ops import unary_union,transform
from shapely import contains_xy
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];v=runpy.run_path(str(P/'tools/concept_diagrams_v11.py'));O=P/'reviews/production-v12';G=O/'geometry';S=v['R']/'brief/site-package';dem=np.asarray(Image.open(S/'terrain/dem_9_13_utm19s_60m.png'),dtype=float);dy,dx=np.gradient(dem,60);slope=np.hypot(dx,dy)*100
xs=559572.4+(np.arange(dem.shape[1])+.5)*60;ys=6608973.7-(np.arange(dem.shape[0])+.5)*60
fixed=unary_union([g for g,p in v['fixed']]);regions=unary_union([g for g,p in v['regions'] if p['id'] in ['Z3','Z4']]);roads=unary_union([g for g,p in v['regional']]);districts=unary_union([g for g,p in v['districts']]);avoid=v['channels'].buffer(150).union(fixed).union(districts).union(roads.buffer(24));base=regions.difference(avoid);fields=[]
x0,y0,x1,y1=base.bounds
for x in np.arange(math.floor(x0/1200)*1200,x1,1200):
 for y in np.arange(math.floor(y0/600)*600,y1,600):
  g=box(x+12,y+12,x+1188,y+588).intersection(base)
  if g.area<100000:continue
  r=(ys>=y)&(ys<=y+600);c=(xs>=x)&(xs<=x+1200);X,Y=np.meshgrid(xs[c],ys[r]);sl=slope[np.ix_(r,c)];mask=contains_xy(g,X,Y)
  if not mask.any() or np.percentile(sl[mask],95)>5:continue
  fields.append((g,dict(id='AF-'+str(len(fields)+1).zfill(4),role='conditional_agrivoltaic_extension',status='long_term_planning_opportunity_not_installed',slope_p95_pct=round(float(np.percentile(sl[mask],95)),2),area_m2=round(g.area,1),basis='Z3/Z4 productive programme; assumed 5% p95 slope screen, 150m channel study buffer, 24m regional-route study buffer; not legal setbacks or engineering approval',crop_programme='forage grass and jojoba; irrigation and agronomy gate before planting',phase='resource_gated_future_no_fixed_date')))
union=unary_union([g for g,p in fields]);audit=dict(field_count=len(fields),conditional_area_km2=round(union.area/1e6,3),outside_scope_m2=union.difference(v['scope']).area,fixed_overlap_m2=union.intersection(fixed).area,channel_study_buffer_overlap_m2=union.intersection(v['channels'].buffer(150)).area,capacity_status='No installed MW, plant yield or water entitlement inferred',limits='60m DEM screening; route buffers and slopes are proposal assumptions; geotechnical, hydrological, ecology, title, irrigation, equipment and power verification remain open')
assert max(audit[k] for k in ['outside_scope_m2','fixed_overlap_m2','channel_study_buffer_overlap_m2'])<.01
(G/'territorial-fields.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=[dict(type='Feature',geometry=mapping(transform(v['I'],g)),properties=p) for g,p in fields]),separators=(',',':'))+'\n');(O/'territorial-field-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
f=plt.figure(figsize=(17,13),facecolor=v['BG']);f.text(.035,.95,'AGUA FINITA / FIELDS FOLLOW THE GROUND',fontsize=24,color=v['INK'],weight='bold');f.text(.035,.914,'V12 whole-territory design study / conditional agrivoltaic extension, source channels and issued site boundary',fontsize=11,color=v['INK']);a=f.add_axes([.025,.13,.69,.72])
for g,p in v['regions']:v['fill'](a,g,'#E5E1CF','#A7A48D',.3)
for g,p in fields:v['fill'](a,g,'#B9BF7A','#E7E7D4',.2)
for g,p in v['fixed']:v['fill'](a,g,'#CBA34F','#796B32',.7)
for g,p in v['regional']:v['line'](a,g,'#5B6559',.7,'--')
v['line'](a,v['channels'].intersection(v['scope']), '#5D94AA',.7)
for g,p in v['regions']:
 if p['id'] in ['Z2','Z5','Z6']:v['label'](a,g,{'Z2':'Agricultural research','Z5':'Gateway / logistics','Z6':'Mountain stewardship'}[p['id']],9)
for g,p in v['districts']:v['fill'](a,g,{'R':'#D4A289','C':'#B7755B','P':'#497784','S':'#7C957C'}.get(p['id'],'#AEAC98'),v['INK'],.4)
v['line'](a,v['scope'],v['INK'],1.5);v['frame'](a,v['WHOLE'])
f.text(.74,.81,'CONTINUITY WITH REASONS',fontsize=13,color=v['INK'],weight='bold');f.text(.74,.76,'Olive / future field footprints\nGold / protected fixed pilots\nBlue / source seasonal channels\nDashed / proposed regional roads\nDark outline / issued site boundary\n\nChannels break the field pattern.\nSteeper ground stays outside\nthis production layout.\nService lanes separate work blocks.\n\nFuture fields are not installed PV.\nWater, power and market gates\ncontrol actual construction.',fontsize=11,color=v['INK'],va='top',linespacing=1.7)
f.text(.035,.055,'Design assumptions: 1,200 x 600 m working blocks, 12 m edge strips, p95 slope <= 5%, 150 m channel screening corridor. These are not statutory standards.\nField footprints are clipped to the current issued boundary and avoid protected pilots. Existing pilot interiors are neither inferred nor replaced.',fontsize=10,color=v['INK'],linespacing=1.7)
f.savefig(O/'territorial-fields-plan.png',dpi=150,facecolor=v['BG']);plt.close(f)
print(json.dumps(audit,indent=2))
