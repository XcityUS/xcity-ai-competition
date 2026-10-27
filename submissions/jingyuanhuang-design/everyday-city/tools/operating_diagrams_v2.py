"""Operating plans and phased construction diagrams from the same V2 coordinates."""
from diagrams_v2 import *
from matplotlib.patches import Rectangle,Circle

def run_operating():
 # Compact campus, including shared interfaces and rationalised access.
 bb=(574070,6553170,574630,6553940);f,a=canvas(bb,(9,10));base(a,bb)
 for g,p in load(O/'module-positions.geojson'):fill(a,g,'#CFB97F',edge=BG,lw=.6)
 for g,p in bld:
  if g.intersects(box(*bb)):
   if p['id'].startswith('P-HALL'):label(a,g,'8 positions\n2 MW IT scenario\nP'+str(p['phase']),7)
   elif p['id'].startswith('P-SHARED'):label(a,g,{'P-SHARED-MGRID':'MV / mGrid','P-SHARED-FIBRE-SECURITY':'Fibre / control','P-SHARED-DRY-REJECTION':'Dry heat\nrejection'}.get(p['id'],''),6)
 for g,p in assets:
  if p['type'].startswith('campus_'):
   line(a,g,{'campus_power':'#C18B3A','campus_cooling':'#4A9CA6','campus_fibre':'#8E70A4','campus_thermal':'#BD7655'}[p['type']],1.5,'--' if p['type']=='campus_thermal' else '-')
 label(a,Point(574320,6553408),'60 m between-row service zone\nplant / maintenance / worker shade',6)
 label(a,Point(574350,6553755),'REPAIR / PHASED WORKS\ncrane and replacement circulation on perimeter',7)
 save(f,'B03-operating-plan')
 # One group's eight module positions; no equation between power-block label and IT load.
 group=box(574170,6553350,574250,6553390);f,a=canvas(group.buffer(8).bounds,(10,6));fill(a,group,'#DCE2DF',edge=INK,lw=1)
 for g,p in load(O/'module-positions.geojson'):
  if g.intersects(group):fill(a,g,'#D4C28F',edge=INK,lw=.4);label(a,g,'250 kW\nIT assumed',7)
 label(a,Point(574210,6553370),'12 m central service aisle / assumed',8)
 save(f,'B03-module-group')
 # Hall architecture: assumed repeatable 10m structural bays and enclosed 8m envelope.
 f,a=plt.subplots(figsize=(12,4),facecolor=BG);a.axis('off');a.set(xlim=(-3,83),ylim=(-3,14));a.set_aspect('equal')
 a.add_patch(Rectangle((0,0),80,8,facecolor='#DDD6C7',edgecolor=INK,lw=1))
 for x in range(0,81,10):a.plot([x,x],[0,8],color='#737F7A',lw=1)
 for x in [8,28,48,68]:a.add_patch(Rectangle((x,0),4,4.5,facecolor='#A7B6B8',edgecolor=INK,lw=.6))
 a.text(40,11,'80m x40m enclosed industrial hall / 8m assumed height / 10m repeatable frame bays',ha='center',color=INK,fontsize=10)
 a.text(40,-2,'Four delivery doors shown diagrammatically; equipment modules and shared services inside / supplier and fire engineering pending',ha='center',color=INK,fontsize=8)
 save(f,'B03-hall-elevation')

 # Trial plot envelopes, showing service headlands and segregated visitor ground, not green planting.
 bb=(573000,6552140,573800,6552600);f,a=canvas(bb,(11,7));fill(a,box(*bb),'#D8CAB1')
 for g,p in load(P/'geometry/courtyard_details.geojson'):fill(a,g,'#E6D9BD' if p['material']=='mineral_pavers' else '#BDB09B',edge=BG,lw=.4)
 for g,p in bld:
  if g.intersects(box(*bb)):fill(a,g,'#727B76')
 for g,p in roads:
  if g.geom_type.endswith('LineString') and g.intersects(box(*bb)):line(a,g.intersection(box(*bb)),RUST if p.get('network')=='people' else BLUE,.8)

 for g,p in assets:
  if p.get('id','').startswith('F-PV'):
   fill(a,g.buffer(2,cap_style=2),'#768E9D',alpha=.65)
  if p.get('id','').startswith('F-PV'):
   y=g.centroid.y;a.plot([573000/1000,573100/1000],[y/1000,y/1000],color=RUST,lw=.4,ls=':')
 # Crop bands are the actual declared cultivation polygons, not decorative landscaping.
 for g,p in load(P/'geometry/crops.geojson'):
  if p['field']=='C02':
   fill(a,g,'#809553' if p['species']=='forage' else '#A59370',edge='none')
   if p['species']=='jojoba':
    for x in range(int(g.bounds[0])+5,int(g.bounds[2])-4,5):
     a.add_patch(Circle((x/1000,g.centroid.y/1000),.001,facecolor=GREEN,edgecolor='none'))
 label(a,Point(573400,6552155),'Alternating 2m forage / jojoba bands under panels; metered drip',7)
 label(a,Point(573050,6552270),'100 m\nheadland',7);label(a,Point(573750,6552270),'100 m\nheadland',7)
 label(a,Point(573400,6552345),'14 m clear lanes / 18 m pitch / fixed-tilt rows',7)
 label(a,Point(573350,6552381),'29m PUBLIC FORECOURT / connected entries',7)
 label(a,Point(573350,6552363),'CONTINUOUS SHADED PROMENADE',6)
 label(a,Point(573350,6552460),'REAR LOADING + MAINTENANCE / public access separate',7)
 label(a,Point(573350,6552545),'EXISTING ARRIVAL LINK / reserve outside working apron',6)
 save(f,'C02-operating-plan')
 import shutil
 shutil.copy2(D/'C02-operating-plan.png',D/'C02-plan.png')
 f,a=plt.subplots(figsize=(12,5),facecolor=BG);a.set_facecolor(BG);a.axis('off');a.set(xlim=(-3,35),ylim=(-1.5,8));a.axhline(0,color=INK,lw=1)
 for x in [0,18]:
  a.plot([x,x+3.76],[3.12,4.48],color=BLUE,lw=5);a.plot([x+1.88,x+1.88],[0,3.8],color=INK,lw=1)
  a.add_patch(Rectangle((x+.8,0),2,1.2,facecolor='none',edgecolor=GREEN,ls='--',lw=1.4))
 a.add_patch(Rectangle((8,0),2.5,2.6,facecolor='none',edgecolor=RUST,lw=1.4));a.text(9.25,2.9,'Assumed service vehicle\n2.5 m W / 2.6 m H',ha='center',fontsize=10,color=INK)
 a.text(3,5.0,'4 m fixed-tilt panel / centre 3.8 m\nminimum edge clearance about 3.1 m',ha='center',fontsize=10,color=INK)
 a.text(21,1.6,'Proposed 1.2 m pruned crop envelope\nproposed cultivated stage',ha='center',fontsize=10,color=INK)
 a.annotate('',xy=(18,-.6),xytext=(0,-.6),arrowprops=dict(arrowstyle='<->',color=INK));a.text(9,-1.1,'18 m row pitch / 14 m clear lane (assumed)',ha='center',fontsize=10,color=INK)
 a.text(16,7,'Proposed cultivated stage: planting gated by lawful water, soil, wind and electrical safety',ha='center',fontsize=11,color=INK);save(f,'C02-operating-section')
 import shutil
 shutil.copy2(D/'C02-operating-section.png',D/'C02-section.png')
 # Spatial commissioning/construction sequence, not a list of dates.
 for ph in [1,2,3]:
  f,a=canvas(SYSTEM,(7,10));w=box(*SYSTEM)
  for g,p in land:
   if g.intersects(w):fill(a,g.intersection(w),COL.get(p['use'],GREY) if p['phase']<=ph else '#E4E1D8',edge=BG,lw=.4)
  for g,p in bld:
   if g.intersects(w):fill(a,g,'#687976' if p['phase']<=ph else '#DDD9CF',edge=BG,lw=.2)
  for g,p in roads:
   if g.geom_type.endswith('LineString') and g.intersects(w) and p.get('phase',1)<=ph and not p.get('study_only'):line(a,g.intersection(w),BLUE if p.get('network')!='machine' else '#8A6A68',.9)
  if ph<3:
   line(a,LineString([(574600,6554300),(574600,6555500),(575800,6555500)]),'#B7775B',2,'--')
   line(a,LineString([(575800,6552750),(575800,6556700),(573400,6556700)]),'#AD8662',2,'--')
   label(a,Point(575650,6555950),'CONSTRUCTION\nEAST / NORTH BYPASS',7)
  label(a,Point(574400,6554750),f'P{ph}: commissioned only after supply,\naccess, staffing and emergency tests',8)
  label(a,Point(574350,6553600),f'{[16,24,32][ph-1]} operating module positions\n{[4,6,8][ph-1]} MW IT scenario',7)
  save(f,'commissioning-P'+str(ph))
if __name__=='__main__':run_operating();print('Operating campus, trial envelopes and commissioning diagrams generated')
