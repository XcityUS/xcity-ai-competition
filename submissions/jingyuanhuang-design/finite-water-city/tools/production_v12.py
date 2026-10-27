"""Read-only V11 geometry audit; production hierarchy review, not a final redesign."""
import runpy,json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Patch
P=Path(__file__).resolve().parents[1]
v=runpy.run_path(str(P/'tools/concept_diagrams_v11.py'))
O=P/'reviews/production-v12';O.mkdir(exist_ok=True)
f=plt.figure(figsize=(20,12),facecolor=v['BG'])
f.text(.035,.95,'AGUA FINITA / PRODUCTION-LED REVIEW V12',fontsize=24,color=v['INK'],weight='bold')
f.text(.035,.913,'Existing geometry audit: whole territory and the productive / living interface. Not a new approved installation plan.',fontsize=12,color=v['INK'])
a=f.add_axes([.03,.14,.45,.72]);b=f.add_axes([.52,.28,.45,.58])
for ax in [a,b]:
 for g,p in v['regions']:v['fill'](ax,g,p['color'],'#888879',.4, .65)
 for g,p in v['fixed']:v['fill'](ax,g,'#C6A750','#796B32',.5)
 for g,p in v['land']:v['fill'](ax,g,v['C'].get(p.get('use'),'#DDDCD2'))
 for g,p in v['roads']:v['line'](ax,g,'#FDFCF5',1.2)
 for g,p in v['regional']:v['line'](ax,g,'#686C65',.7,'--')
 v['line'](ax,v['scope'],'#213C47',1.3)
assets=v['load'](P/'reviews/complete-city-v9/geometry/assets.geojson')
for ax in [a,b]:
 for g,p in assets:
  if p['type']=='pv_field':v['fill'](ax,g,'#D2B656','#8C742A',.6)
  elif p['type']=='pv_row':v['line'](ax,g,'#3C626A',.45)
 for g,p in v['build']:
  if p.get('use')=='compute':v['fill'](ax,g,'#426C7A','#244B57',.4)
 v['frame'](ax,v['WHOLE'] if ax is a else (571500,6551500,577000,6559700))
for g,p in v['regions']:v['label'](a,g,p['id'],11)
for g,p in v['districts']:
 if p['id'] in ['R','C','P','S','A']:v['label'](b,g,p['id']+' / '+p['name'],10)
a.set_title('01 / ALL ISSUED LAND',loc='left',fontsize=13,color=v['INK'],pad=12)
b.set_title('02 / EXISTING SOUTHWEST DESIGN ENLARGEMENT',loc='left',fontsize=13,color=v['INK'],pad=12)
f.text(.52,.205,'REVISE BEFORE THE NEXT FINISHED OVERVIEW',fontsize=13,color=v['INK'],weight='bold',va='top')
f.text(.52,.175,'Solar: add panel / crop / service plans and sections for proposed extensions.\nCompute: test compact hall layout, shared plant and justified servicing gaps.\nOverall image: show this energy-led system; keep housing images architectural.',fontsize=11,color=v['INK'],linespacing=1.6,va='top')
f.text(.035,.055,'Gold / fixed pilot or explicit proposed PV fields     Blue / compute halls     Dashed / proposed regional links\nLarge coloured regions express planning roles, not installed facilities. Fixed-pilot internal geometry remains protected.',fontsize=11,color=v['INK'],linespacing=1.6)
f.savefig(O/'production-structure-review.png',dpi=140,facecolor=v['BG']);plt.close(f)
(O/'STATUS.txt').write_text('V12 WORKING REVIEW\nSource: V9/V10 geometry as retained in V11. No geometry, capacity or public preview is changed by this audit.\nNext: whole-territory production-led spatial control; new-extension agrivoltaic operating plan/section; compute servicing and phasing; substantive seasonal-wash park design.\nHousing-only aerial is not an overall view. Existing V11 images are retained as history pending replacement.\n')
print(O/'production-structure-review.png')
