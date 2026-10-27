import importlib.util,json,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
# Shared drawing helpers are loaded after the base sheets are regenerated.
spec=importlib.util.spec_from_file_location('draw',p/'draw_design.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
plt=d.plt;Poly=d.Poly;P=d.P;O=d.O;x0=d.x0;y0=d.y0
f=d.new(17,'Five homes per floor. Shared ground below.','A01 architectural concept / 48 x 12 m wing / dimensioned typical floor and section')
a=f.add_axes([.06,.47,.60,.30]);a.set_xlim(-2,50);a.set_ylim(-2,15);a.set_aspect('equal');a.axis('off');widths=[9.6,7.2,14.4,7.2,9.6];x=0
for i,w in enumerate(widths):
 a.add_patch(Poly([(x,1.8),(x+w,1.8),(x+w,12),(x,12)],facecolor=['#dcc1a5','#ead9bc','#c6d1bc','#ead9bc','#dcc1a5'][i],edgecolor=d.INK,lw=.7));a.text(x+w/2,8,['Family','Compact','Shared home','Compact','Family'][i],ha='center',fontsize=9);a.text(x+w/2,6.5,f'{w*10.2:.1f} m2\nconcept unit',ha='center',fontsize=8);a.plot([x,x+w*.45],[4.8,4.8],color=d.INK,lw=.4);a.plot([x+w*.45,x+w*.45],[1.8,4.8],color=d.INK,lw=.4);x+=w
a.add_patch(Poly([(0,0),(48,0),(48,1.8),(0,1.8)],facecolor=d.GOLD,edgecolor=d.INK,lw=.7));a.text(24,.9,'1.8 m access gallery / shade / entries',ha='center',va='center',fontsize=8)
a.annotate('',xy=(0,13),xytext=(48,13),arrowprops={'arrowstyle':'|-|','color':d.INK});a.text(24,13.4,'48 m',ha='center',size=9);a.text(-1,6,'12 m',rotation=90,ha='center',size=9)
a=f.add_axes([.07,.15,.58,.21]);a.set_xlim(-3,64);a.set_ylim(-1,13);a.axis('off')
for xx in [0,50]:
 a.add_patch(Poly([(xx,0),(xx+12,0),(xx+12,9.9),(xx,9.9)],facecolor=d.RED,edgecolor=d.INK,lw=.7))
 for y in [3.3,6.6]:a.plot([xx,xx+12],[y,y],color=d.BG,lw=1)
a.plot([0,62],[0,0],color=d.INK);a.plot([18,40],[4.5,4.5],color=d.GOLD,lw=3);a.plot([18,18],[0,4.5],color=d.GOLD);a.plot([40,40],[0,4.5],color=d.GOLD);a.text(31,1.5,'Courtyard / common room access\nDry shared ground + small shade',ha='center',size=9)
d.note(f,.72,.77,'Capacity, not a sales plan','Five dwellings per floor x three floors = 15 per wing. Four wings = 60 per court. Four courts = 240 per neighbourhood. Gallery area is excluded from the concept unit area labels.',38)
d.note(f,.72,.48,'A range of households','The floor tests family, compact and shared-home widths within one consistent footprint. Indicative wet-core and living/quiet zones require actual room layouts, services and daylight checks.',38)
d.note(f,.72,.20,'Access and safety','1.8 m gallery is a design assumption. Stair/lift cores, accessible entrances, fire egress and seismic separation are unresolved architectural work; this sheet does not claim code compliance.',38)
d.finish(f,17,'a01-floor-and-section')
f=d.new(18,'One service spine, several public thresholds','Civic enlargement / real model locations / phase-one programme allowances')
a=f.add_axes([.05,.12,.55,.68]);d.mastermap(a,(x0+1180,y0+470,x0+1640,y0+1260),movement=False)
for g,v in d.geo['buildings']:
 if v['use'] not in ['residential','energy','compute','industry','infrastructure'] and g.centroid.x>x0+1250:
  label=v['name'].replace(' / ','\n');a.text(g.centroid.x/1000,g.centroid.y/1000+.035,label,ha='center',fontsize=8)
d.note(f,.66,.78,'School and care','360 primary and 240 secondary/vocational places; 120 childcare places. These are capacity assumptions linked to the resident scenario, not established facilities.',46)
d.note(f,.66,.50,'The right to remain','Market, kitchen, library, arts/assembly and an indoor heat refuge support several generations. No purchase or employer badge is required to enter public ground.',46)
d.note(f,.66,.23,'Servicing behind public life','Civic vehicle access uses the eastern emergency spine. Loading, kitchen waste, care drop-off and emergency turning must be resolved at each actual door before implementation.',46);d.finish(f,18,'civic-spine')
f=d.new(19,'Infrastructure has a route, a capacity and a limit','Resource diagram / proposed links; no existing supply or utility rights asserted')
a=f.add_axes([.05,.15,.9,.62]);a.axis('off');nodes=[(.02,.68,'Rooftop + yard PV\n20 MW scenario'),(.35,.68,'Battery / grid\n180 MWh / 20 MW'),(.70,.68,'Homes + services\n1 MW critical reserve'),(.02,.25,'Fresh supply\n751,748.4 m3/yr'),(.35,.25,'Treatment + reuse\n180,000 m3/yr reuse'),(.70,.25,'Farms + processing\nFixed pilot separate')]
for x,y,s in nodes:
 a.add_patch(Poly([(x,y),(x+.26,y),(x+.26,y+.19),(x,y+.19)],transform=a.transAxes,facecolor='#dfd7c5',edgecolor=d.TEAL));a.text(x+.13,y+.095,s,transform=a.transAxes,ha='center',va='center',fontsize=12)
for x1,y1,x2,y2 in [(.28,.775,.35,.775),(.61,.775,.70,.775),(.28,.345,.35,.345),(.61,.345,.70,.345),(.83,.68,.48,.44),(.48,.68,.48,.44)]:a.annotate('',xy=(x2,y2),xytext=(x1,y1),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':d.TEAL,'lw':2})
f.text(.07,.115,'Grid, water and communications alignments are research assumptions. Waste, treatment, pressure, cable routes and utility approvals require specialist design.',size=10);d.finish(f,19,'resource-network')
(P/'report/page-index.json').write_text(json.dumps(d.index,indent=2));print('19 formal English sheets')
