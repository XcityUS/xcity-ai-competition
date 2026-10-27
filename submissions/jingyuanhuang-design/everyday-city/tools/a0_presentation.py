"""Authored A0 presentation: finished concept views and source-derived diagrams only."""
from design_graphics import *
from matplotlib.patches import Patch
fig=plt.figure(figsize=(46.81,33.11),facecolor=BG)
fig.text(.032,.965,'THE EVERYDAY CITY',fontsize=80,weight='bold',color=TEAL)
fig.text(.034,.932,'HOMES, SHARED GROUND AND PUBLIC LIFE BEFORE PRODUCTION-LED EXPANSION',fontsize=25,color=INK)
fig.text(.968,.965,'XCITY / SAN JUAN',fontsize=27,ha='right',color=TEAL)
fig.text(.968,.935,'JINGYUAN HUANG / 27 OCTOBER 2026',fontsize=21,ha='right')
# Primary city image, preserving the entire geometry-derived concept composition.
a=fig.add_axes([.032,.415,.55,.495]);a.imshow(Image.open(P/'media/district-finished.png'));a.axis('off')
fig.text(.033,.402,'FIRST DISTRICT / Six neighbourhoods, 24 shared courts and a civic services spine',fontsize=24,weight='bold')
# Regional structure from the checked geometry; not a screenshot of GIS output.
fig.text(.615,.900,'01  WHOLE-SITE STRUCTURE',fontsize=29,weight='bold',color=TEAL)
a=fig.add_axes([.605,.625,.17,.258])
for g,v in geo['structure']:fill(a,g,COL[v['system']])
line(a,scope,INK,1.2);line(a,channels,'#94a9a5',.6)
for g,v in load(P/'report/regional-corridors.geojson'):line(a,g,TEAL,1.6,'--' if v['phase']>1 else '-')
for g,v in load(P/'report/centres.geojson'):
 a.scatter(g.x/1000,g.y/1000,s=35,color=TEAL);a.text(g.x/1000+.4,g.y/1000+.4,v['name'],fontsize=16,color=INK)
frame(a,scope.bounds)
for label in a.texts:label.set_fontsize(max(label.get_fontsize(),20))
# Complete phase-one plan and matching node identifiers.
fig.text(.802,.900,'02  COMPLETE FIRST DISTRICT',fontsize=29,weight='bold',color=TEAL)
a=fig.add_axes([.792,.625,.18,.258]);mastermap(a,master.bounds,movement=False)
for g,v in geo['nodes']:
 line(a,g,RED,2);q=g.representative_point();a.text(q.x/1000,q.y/1000,v['node_id'],fontsize=19,weight='bold',ha='center',bbox={'facecolor':BG,'edgecolor':'none','alpha':.95})
for label in a.texts:label.set_fontsize(max(label.get_fontsize(),20))
fig.legend(handles=[Patch(facecolor=COL[k],label=title) for k,title in [('living','Living'),('energy_compute','Energy + compute'),('agri_production','Agriculture'),('port','Gateway'),('reserve','Reserve')]],loc='upper left',bbox_to_anchor=(.61,.607),ncol=3,frameon=False,fontsize=18)
# A readable programme and spatial proposition, rather than dense technical data.
for x,big,label in [(.615,'1,440','HOMES'),(.705,'3,600','RESIDENTS'),(.795,'24','SHARED COURTS'),(.885,'3','DETAILED NODES')]:
 fig.text(x,.551,big,fontsize=49,weight='bold',color=TEAL);fig.text(x,.526,label,fontsize=19)
fig.text(.615,.489,'ONE CITY FIRST. SERVICES BEFORE EXPANSION.',fontsize=31,weight='bold')
fig.text(.615,.463,'Homes and public services organise daily life. Compute, repair and farm services',fontsize=22)
fig.text(.615,.440,'work at its edges. Two later service towns and an eastern gateway grow only',fontsize=22)
fig.text(.615,.417,'when access, resource contracts and independent services can be delivered.',fontsize=22)
# Three final node images: each is an authored aerial + eye-level pair.
for i,(key,title,caption) in enumerate([
 ('A01','COURTYARD HOMES','Four open-corner courts. Shared laundry, care, shade and public ground.'),
 ('B03','USEFUL COMPUTE','Two halls, cooperative workshops and a named waste-heat receiver.'),
 ('C02','WORKING FARM EDGE','Teaching, repair and a productive trail to the real protected pilot edge.')]):
 x=.032+i*.32
 fig.text(x,.354,key+' / '+title,fontsize=31,weight='bold',color=TEAL)
 a=fig.add_axes([x,.130,.296,.207]);a.imshow(Image.open(P/f'media/{key}-finished.png'));a.axis('off')
 fig.text(x,.109,'AERIAL CONCEPT + EYE-LEVEL EXPERIENCE',fontsize=20,weight='bold',color=TEAL)
 for j,ln in enumerate(textwrap.wrap(caption,67)):fig.text(x,.085-j*.018,ln,fontsize=22)
fig.text(.032,.026,'CONCEPT ILLUSTRATIONS + FORMAL DIAGRAMS / Capacities are scenarios; engineering and rights require verification.',fontsize=19)
fig.text(.968,.026,'Sources: XCITY issued boundary, fixed pilots and DEM / Original entrant design and registered generated imagery',fontsize=16,ha='right')
out=P/'pages/a0-presentation.jpg';fig.savefig(out,dpi=140,facecolor=BG,pil_kwargs={'quality':94});plt.close(fig)
print(out,round(out.stat().st_size/1e6,2),'MB')
