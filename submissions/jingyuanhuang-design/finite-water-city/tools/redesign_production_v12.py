"""V12 production revision. Preserve hall sizes/capacity scenarios; revise spatial fit."""
import json,runpy,math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
from shapely.geometry import box,LineString,mapping
from shapely.ops import transform,unary_union
P=Path(__file__).resolve().parents[1];v=runpy.run_path(str(P/'tools/concept_diagrams_v11.py'));O=P/'reviews/production-v12';G=O/'geometry';G.mkdir(exist_ok=True)
BG=v['BG'];INK=v['INK'];load=v['load'];I=v['I'];fill=v['fill'];line=v['line'];label=v['label']
B=[];M=[]
for g,p in v['build']:
 if p['id'].startswith('P-IT-'):
  k=int(p['id'].split('-')[-1]);x=573270+(k%4)*132;y=6552130+(k//4)*120;g=box(x,y,x+96,y+48);p=dict(p,revision='V12 compact serviced hall campus',dimensional_basis='Existing declared 96 x 48 m hall footprint retained; servicing clearances are concept assumptions')
 B.append((g,p))
for g,p in v['roads']:
 if p['id']=='S':
  pts=[xy for xy in g.coords if xy[1]>=6554823]
  pts += [(573220,6554824),(573220,6553100),(573220,6552550),(573300,6552500)]
  g=LineString(pts);p=dict(p,revision='V12 solar-edge shuttle study',basis='Rerouted outside proposed panel fields; terrain, drainage and right of way require fresh verification',length_km=round(g.length/1000,3))
  p.pop('channel_intersection_empty',None);p.pop('channel_overlap_m',None);p.pop('flood_screen_km',None)
 if not p['id'].startswith('P-yard-'):M.append((g,p))
for points,n in [([(573220,6552100),(573830,6552100),(573830,6552550)],'east-loop'),([(573220,6552100),(573220,6552550)],'west-loop'),([(573220,6552220),(573830,6552220)],'shared-service'),([(573220,6552320),(573830,6552320)],'plant-access')]:
 M.append((LineString(points),dict(id='P-v12-'+n,network='machine',hierarchy='production',road_class='secondary',width_m=12,phase=1,design_status='Proposed concept; swept paths/fire and road engineering unverified')))
plants=[(box(573270,6552350,573490,6552400),dict(id='P-v12-power',use='infrastructure',name='Shared power / backup',phase=1)),(box(573520,6552350,573760,6552400),dict(id='P-v12-cooling',use='infrastructure',name='Shared dry-cooling / fibre',phase=1))]
def write(name,items):
 (G/(name+'.geojson')).write_text(json.dumps(dict(type='FeatureCollection',features=[dict(type='Feature',geometry=mapping(transform(I,g)),properties=p) for g,p in items]),separators=(',',':'))+'\n')
write('buildings',B);write('movement',M);write('shared-plant',plants)
halls=[(g,p) for g,p in B if p['id'].startswith('P-IT-')];scope=v['scope'];fixed=unary_union([g for g,p in v['fixed']]);old=[g for g,p in v['build'] if p['id'].startswith('P-IT-')];serv=unary_union([g.buffer(p['width_m']/2,cap_style=2) for g,p in M if p['id'].startswith('P-v12')])
audit=dict(hall_count=len(halls),hall_footprint_m2=sum(g.area for g,p in halls),previous_hall_footprint_m2=sum(g.area for g in old),declared_it_mw=sum(p['it_mw'] for g,p in halls),capacity_status='Retained declared scenario, not manufacturer-verified rack or resource entitlement',outside_scope_m2=sum(g.difference(scope).area for g,p in halls),fixed_pilot_overlap_m2=sum(g.intersection(fixed).area for g,p in halls),new_service_road_overlap_m2=sum(g.intersection(serv).area for g,p in halls),hall_overlap_m2=sum(g.intersection(h).area for i,(g,p) in enumerate(halls) for h,q in halls[i+1:]),old_hall_envelope_m2=unary_union(old).envelope.area,new_hall_envelope_m2=unary_union([g for g,p in halls]).envelope.area)
assert all(audit[k]<.01 for k in ['outside_scope_m2','fixed_pilot_overlap_m2','new_service_road_overlap_m2','hall_overlap_m2'])
pv=unary_union([g for g,p in load(P/'reviews/complete-city-v9/geometry/assets.geojson') if p['type']=='pv_field'])
shuttle=next(g for g,p in M if p['id']=='S')
audit.update(shuttle_panel_field_overlap_m=shuttle.intersection(pv).length,shuttle_fixed_pilot_overlap_m=shuttle.intersection(fixed).length,shuttle_source_channel_screen_overlap_m=shuttle.intersection(v['channels'].buffer(150)).length)
assert audit['shuttle_panel_field_overlap_m']<.01 and audit['shuttle_fixed_pilot_overlap_m']<.01
(O/'geometry-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
def page(title,sub,size=(17,11)):
 f=plt.figure(figsize=size,facecolor=BG);f.text(.035,.947,'AGUA FINITA / V12',fontsize=12,color='#9C803A',weight='bold');f.text(.035,.905,title,fontsize=23,color=INK,weight='bold');f.text(.035,.865,sub,fontsize=10,color=INK);return f
def save(f,n):f.savefig(O/(n+'.png'),dpi=150,facecolor=BG);plt.close(f)
# Compact halls and retained productive precinct connections.
f=page('Compute halls: compact work, shared infrastructure','Eight existing hall footprints and the declared 2 / 4 / 8 MW IT scenario retained. No new installed capacity is claimed.')
a=f.add_axes([.035,.20,.66,.61]);
for g,p in v['land']:
 if g.intersects(box(573100,6552000,574650,6553100)):fill(a,g,'#E3E0D2')
for g,p in M:
 if g.intersects(box(573100,6552000,574650,6553100)):line(a,g,'#A2ABA5',3 if p.get('network')!='people' else .7)
for g,p in B:
 if g.intersects(box(573100,6552000,574650,6553100)):
  fill(a,g,'#426D79' if p.get('use')=='compute' else '#B8A884',INK,.3)
  if p['id'].startswith('P-IT-'):label(a,g,'P'+str(p['phase']),9)
for g,p in plants:fill(a,g,'#A0B5A0',INK,.5);label(a,g,p['name'],8)
v['frame'](a,(573170,6552040,573900,6552450))
f.text(.72,.76,'SPATIAL DECISIONS',fontsize=13,color=INK,weight='bold');f.text(.72,.70,'Separate halls; shared services.\n\nShort internal service loop.\n\nRepair lies north on the freight spine. See overall plan.\n\nUtility plots are protected from\nbuilding encroachment.\n\nNo residential heat demand\nis invented to justify proximity.',fontsize=11,color=INK,va='top',linespacing=1.4)
f.text(.035,.10,'Concept dimensions: 96 x 48 m halls; 36 m lateral gaps and 72 m between rows. These are design assumptions, not fire or vendor standards.\nPlant footprints reserve space, not equipment sizing. Verify cooling, electrical separation, lifting, turning and terrain before fixing the layout.',fontsize=10,color=INK,linespacing=1.7)
save(f,'compute-plan')
f=page('Construction phases: operate before expanding','One coordinated layout. Colour shows active halls; outlines show later works. Plant and access must be commissioned before IT starts.')
for i,ph in enumerate([1,2,3]):
 a=f.add_axes([.035+i*.322,.28,.30,.51]);
 for g,p in M:
  if p['id'].startswith('P-v12'):line(a,g,'#75877D',2)
 for g,p in halls:fill(a,g,'#426D79' if p['phase']<=ph else BG,INK,.8)
 for g,p in plants:fill(a,g,'#A0B5A0',INK,.4)
 v['frame'](a,(573170,6552040,573900,6552450));a.set_title('PHASE '+str(ph)+' / '+str([2,4,8][i])+' MW IT scenario',loc='left',fontsize=12,color=INK)
 f.text(.04+i*.322,.20,['Commission access, power, cooling\nand two isolated halls.','Add two halls after utility headroom,\ncustomer demand and resources.','Add the second four-hall row;\nretain construction separation.'][i],fontsize=11,color=INK,linespacing=1.7)
f.text(.035,.08,'Retained IT values are declared design scenarios, not power-block ratings. Equipment configuration, peak site demand, interconnection and water rights remain unresolved.',fontsize=10,color=INK)
save(f,'compute-phases')
# Explicit agrivoltaic prototype, separate from the protected fixed pilot.
f=page('Agrivoltaics: panels, crops and working space together','Proposed-extension prototype only. Existing pilot interiors remain unchanged. Dimensions below are declared design assumptions.')
a=f.add_axes([.05,.24,.52,.56]);a.set_aspect('equal')
for k,x in enumerate([0,18,36]):
 a.add_patch(Rectangle((x,0),4,100,facecolor='#436A74',alpha=.75));a.add_patch(Rectangle((x+4,0),8,100,facecolor='#C7CF94'));a.add_patch(Rectangle((x+12,0),6,100,facecolor='#D6C9AC'))
 for y in range(8,98,8):
  if k%2==0:a.add_patch(plt.Circle((x+2,y),1.1,facecolor='#819665',edgecolor=BG,lw=.5))
 a.plot([x+5]*2,[0,100],color='#708C9B',lw=1,ls='--')
a.add_patch(Rectangle((-3,-10),61,10,facecolor='#D6C9AC'));a.add_patch(Rectangle((-3,100),61,10,facecolor='#D6C9AC'))
a.text(1,114,'WORKING HEADLAND / turning to be verified',fontsize=9,color=INK)
a.annotate('',xy=(0,-17),xytext=(18,-17),arrowprops=dict(arrowstyle='<->'));a.text(9,-22,'18 m repeat',ha='center',fontsize=9);a.set(xlim=(-10,66),ylim=(-23,121));a.axis('off')
f.text(.60,.77,'CULTIVATION + OPERATIONS',fontsize=13,color=INK,weight='bold');f.text(.60,.71,'Blue bands: photovoltaic row envelopes.\nGreen ground: forage strips.\nCircles: pruned jojoba scenario below\nalternate panel rows.\nSand: separate working lanes / headlands.\nDashed: zoned irrigation service.\n\nFinal crop mix, male/female layout,\nclearances and irrigation follow\nagronomy and equipment verification.\nDrought tolerance is not zero demand.',fontsize=11,color=INK,va='top',linespacing=1.6)
f.text(.035,.09,'Assumed 4 m panel envelope + 8 m forage/worked ground + 6 m service lane. Under-panel forage and jojoba both remain production uses.\nPlanting circles illustrate mature/pruned working envelopes; they are not a verified yield, plant-density or pollination design.',fontsize=10,color=INK,linespacing=1.7)
save(f,'agrivoltaic-plan')
f=page('Section: keep cultivation and maintenance possible','Extension study, not an approved mounting system. The fixed pilot is not redesigned by this section.')
a=f.add_axes([.05,.32,.88,.45]);a.plot([-2,39],[0,0],c='#877C57',lw=2)
for x in [0,18]:
 a.plot([x,x],[0,4.5],c=INK,lw=3);a.plot([x-1,x+3],[4.1,5.0],c='#426D79',lw=9)
 a.add_patch(Polygon([(x+.2,0),(x+.2,1.3),(x+1,2.2),(x+2,1.5),(x+2,0)],facecolor='#829966'))
 a.add_patch(Rectangle((x+12,0),5,2.8,facecolor='#D8B16B',alpha=.65));a.text(x+13,.8,'work\nenvelope',fontsize=10,color=INK)
 a.plot([x+4,x+11],[.1,.1],c='#8DAB65',lw=5)
a.text(3,6,'Assumed 4.1 m low panel edge / 2.2 m pruned crop envelope',fontsize=12,color=INK);a.set(xlim=(-2,39),ylim=(-1,7));a.set_aspect('equal');a.axis('off')
f.text(.05,.22,'Test before fixing dimensions',fontsize=14,color=INK,weight='bold');f.text(.05,.17,'Panel motion / structural depth; mature plant height and wind pollination; maintenance vehicles, safe working clearances, pruning and harvest;\nirrigation and drainage; electrical isolation. Do not infer an engineering clearance from the illustrated gap.',fontsize=12,color=INK,linespacing=1.7)
save(f,'agrivoltaic-section')
print(json.dumps(audit,indent=2))
