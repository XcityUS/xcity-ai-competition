"""Coordinated local interface, actual field subdivision and compact works positions."""
from diagrams_v2 import *
O5=P/'reviews/compact-v5'
bb=(573000,6552600,576050,6554800);f,a=canvas(bb,(12,9));base(a,bb)
for g,p in load(P/'geometry/interface_landscape.geojson'):fill(a,g,'#C6B98E',edge=BG,lw=.5)
for g,p in assets:
 if p.get('type')=='pv_row' and g.intersects(box(*bb)):fill(a,g.buffer(2,cap_style=2),'#426C82',edge='none')
for g,p in load(P/'geometry/crops.geojson'):
 if g.intersects(box(*bb)):fill(a,g,'#788C4D' if p['species']=='forage' else '#8D7B54')
label(a,Point(574500,6554600),'TOWN / schools, homes and daily services\nlocal southern edge; full town shown separately',9)
label(a,Point(574480,6554140),'NORTH AGRIVOLTAIC INTERFACE\n52 redistributed rows / four field blocks',9)
label(a,Point(573640,6553100),'WEST FIELD\n10 rows',8)
label(a,Point(574365,6553600),'COMPACT WORKS\n0.35 km² active',9)
label(a,Point(574920,6553420),'UTILITY\n0.130 km²',8)
label(a,Point(574030,6553380),'0.25 km²\nunserviced reserve',7)
a.annotate('',xy=(575.15,6554.3),xytext=(575.15,6553.95),arrowprops=dict(arrowstyle='<->',color=RUST,lw=1.3));a.text(575.2,6554.11,'350 m gross edge\n400 m active edge',fontsize=8,color=RUST)
label(a,Point(575150,6553965),'30m shared field/service corridor\nno building or heat-network credit',7)
legend(a,[('Housing/public services',COL['residential']),('Agrivoltaic rows + crop bands','#9BAC75'),('Compact campus','#889DB0'),('Dry inspection/service ground','#C6B98E'),('Conditional reserve',GREY),('Primary/service streets',BLUE)])
save(f,'compact-interface-v5')
# Source-based changes diagram: actual before/after campus and solar extents at the same scale.
oldland=load(O5/'before/geometry/land_use.geojson')
f,aa=plt.subplots(1,2,figsize=(13,10),facecolor=BG)
for a,items,title in zip(aa,[oldland,land],['BEFORE / 1.1 km unresolved estate gap','V5 / productive interface + compact campus']):
 a.axis('off');a.set_aspect('equal');a.set(xlim=(572.8,576.1),ylim=(6551.9,6556.9))
 for g,p in items:
  use=p.get('programme_use',p['use']);fill(a,g,COL.get(use,GREY),edge=BG,lw=.3)
 a.set_title(title,fontsize=11,color=INK,fontweight='bold')
 a.plot([573,573.5],[6552,6552],color=INK,lw=2);a.text(573,6552.08,'0.5 km',fontsize=8,color=INK)
f.text(.04,.04,'Same housing, jobs, IT load,62 main solar rows and crop-net area. Production/farm move1,050m north. Gross works estate1.56 →0.60km².\nNeither the old1.1km nor new350m gross separation is an engineered noise/fire/thermal buffer; specialist review is required.',fontsize=10,color=INK,linespacing=1.6);f.subplots_adjust(.03,.10,.97,.95,wspace=.02);f.savefig(D/'before-after-v5.png',dpi=190,facecolor=BG);plt.close(f)
print('V5 compact-interface and before/after maps exported')
