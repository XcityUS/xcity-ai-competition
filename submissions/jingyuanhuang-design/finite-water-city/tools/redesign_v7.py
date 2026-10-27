"""V7 source-based planning review. Does not overwrite the published entry geometry."""
import json, hashlib, textwrap, heapq, shutil, warnings
from pathlib import Path
warnings.filterwarnings('ignore', category=DeprecationWarning)
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch, Rectangle, PathPatch
from matplotlib.path import Path as MPath
from shapely.geometry import shape, mapping, box, Point, LineString
from shapely.geometry.polygon import orient
from shapely.ops import transform, unary_union, nearest_points
from pyproj import Transformer

P=Path(__file__).resolve().parents[1]; R=P.parents[2]; S=R/'brief/site-package'
O=P/'reviews/redesign-v7'; O.mkdir(exist_ok=True)
OUT=R.parents[1]/'outputs/agua-finita-v7'; OUT.mkdir(parents=True,exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform
I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:[(transform(T,shape(x['geometry'])),x['properties']) for x in json.loads(f.read_text())['features']]
union=lambda f:unary_union([g for g,p in load(f)])
scope=union(S/'boundaries/scope_9_13.geojson'); fields=union(S/'pilot-area/pilot_area.geojson'); living=union(S/'pilot-area/pilot_living_area.geojson')
fixed=fields.union(living); channels=union(S/'water/channels_dem.geojson'); flood=union(S/'water/flood_sensitive_dem.geojson')
boundary=json.loads((S/'boundaries/boundary-revision.json').read_text())
oldbuild=load(P/'geometry/buildings.geojson'); oldnodes={p['node_id']:g for g,p in load(P/'geometry/nodes.geojson')}
oldmaster=union(P/'geometry/master_area.geojson')
dem=np.asarray(Image.open(S/'terrain/dem_9_13_utm19s_60m.png'),dtype=float)
dy,dx=np.gradient(dem,60); slope=np.hypot(dx,dy)*100
def sample(g):
 x,y=g.centroid.coords[0];r=int((6608973.7-y)/60);c=int((x-559572.4)/60)
 return {'elevation_m':float(dem[r,c]),'centre_cell_slope_pct':round(float(slope[r,c]),2)}
def ft(g,**props):return {'type':'Feature','geometry':mapping(transform(I,g)),'properties':props}
def write_geo(name,items):
 (O/name).write_text(json.dumps({'type':'FeatureCollection','features':[ft(g,**p) for g,p in items]},indent=2))

# The first town is a complete small town; production is a separate facility, not a node collage.
town=box(573700,6553500,574600,6554400)
campus=box(575400,6551300,576100,6551900)
study=box(572800,6550800,576500,6556000)
commons=box(574060,6553870,574240,6554030)
park=box(571850,6554200,573050,6555100)
blocks=[]; buildings=[]
for j,y in enumerate([6553600,6553770,6554130,6554300]):
 for i,x in enumerate([573800,573970,574330,574500]):
  b=box(x-70,y-70,x+70,y+70); bid=f'H{j*4+i+1:02}'
  blocks.append((b,{'kind':'housing_block','id':bid,'dwellings':60,'phase':1}))
  for k,(ox,oy,w,h) in enumerate([(-20,-45,40,15),(-20,30,40,15),(-45,-20,15,40),(30,-20,15,40)]):
   g=box(x+ox,y+oy,x+ox+w,y+oy+h)
   buildings.append((g,{'kind':'building','use':'residential','floors':3,'height_m':10.5,'dwellings':15,'block':bid,'id':f'{bid}-{k+1}'}))
facilities=[
 (box(574060,6554110,574240,6554330),{'kind':'service_plot','use':'school','name':'School + shared sport','places_scenario':360}),
 (box(574280,6553890,574360,6553990),{'kind':'service_plot','use':'clinic','name':'Primary care + emergency transfer'}),
 (box(574060,6554050,574240,6554090),{'kind':'service_plot','use':'market','name':'Market + library + audit room'}),
 (box(573760,6553890,574020,6554010),{'kind':'service_plot','use':'sport','name':'Shared sport + dry garden'}),
 (box(574650,6554250,574770,6554350),{'kind':'service_plot','use':'utilities','name':'Covered water + reuse plant'}),
 (box(574440,6554390,574570,6554470),{'kind':'service_plot','use':'arrival','name':'Passenger arrival + daily services'}),
]
for k,(x,y) in enumerate([(573880,6553460),(574420,6553460),(573880,6554480),(574420,6554480)]):
 facilities.append((box(x-35,y-20,x+35,y+20),{'kind':'service_plot','use':'care','name':f'Neighbourhood care {k+1}'}))
for k in range(3):
 buildings.append((box(575500+k*170,6551450,575612+k*170,6551510),{'kind':'building','use':'compute','floors':1,'height_m':8,'id':f'IT-{k+1}','it_mw_scenario':2}))
for k in range(3):
 buildings.append((box(575500+k*170,6551700,575600+k*170,6551750),{'kind':'building','use':'industry','floors':1,'height_m':7,'id':f'REPAIR-{k+1}'}))
routes=[]
xs=[573700,573885,574055,574245,574415,574600]
ys=[6553500,6553685,6553855,6554045,6554215,6554400]
for x in xs:routes.append((LineString([(x,ys[0]),(x,ys[-1])]),{'kind':'local_street','network':'shared','name':'Town street'}))
for y in ys:routes.append((LineString([(xs[0],y),(xs[-1],y)]),{'kind':'local_street','network':'shared','name':'Town street'}))
routes += [
 (LineString([(574040,6553500),(574040,6554400)]),{'kind':'public_spine','network':'people','name':'Shaded civic walk'}),
 (LineString([(573700,6553950),(574600,6553950)]),{'kind':'public_spine','network':'people','name':'Neighbourhood cross-walk'}),
 (LineString([(575100,6555500),(575100,6551600),(575700,6551600)]),{'kind':'production_access','network':'machine','name':'Freight / service approach'}),
 (LineString([(574500,6554440),(574650,6554440),(574650,6555500),(575100,6555500)]),{'kind':'passenger_link','network':'shared','name':'Passenger turn-off before freight route'}),
 (LineString([(573700,6553950),(573150,6553950),(573150,6554700),(573000,6554700)]),{'kind':'park_access','network':'people','name':'Park high-ground access; closes on warning'}),
]
routes.append((LineString([(574600,6553500),(575100,6553500)]),{'kind':'worker_shuttle','network':'shared','name':'Controlled worker shuttle link'}))
for g,p in facilities:
 if p['use'] in ['care','arrival']:
  q=nearest_points(g.centroid,town.boundary)[1];routes.append((LineString([g.centroid,q]),{'kind':'care_access','network':'people','name':'Local care / arrival connector'}))
# Keep public streets out of the school and care/service grounds.
protected_plots=unary_union([g.buffer(5) for g,p in facilities])
routes=[(g.difference(protected_plots) if p['kind']=='local_street' else g,p) for g,p in routes]
future_south=box(573200,6555600,576200,6559200).intersection(scope).difference(fixed)
centres={p['id']:g for g,p in load(P/'reviews/whole-site-v3/centres.geojson')}
north=centres['C'].buffer(1300).intersection(scope).difference(fixed)
gateway_old=unary_union([g for g,p in load(P/'geometry/structure.geojson') if p.get('system') in ['port'] or 'Eastern shared gateway' in p.get('name','')])
regional=[]
for g,p in load(P/'reviews/whole-site-v3/corridors.geojson'):
 if p.get('to_id') in ['B','D'] or (p.get('from_id')=='D'):continue
 pp=dict(p);pp.update(kind='regional_study',status='study_only',authority='not_secured',name=f"{p.get('from_id')} - {p.get('to_id')}")
 regional.append((g,pp))
# Eastern corridor is retained as one conditional surveyed-corridor study via the old D waypoint.
for g,p in load(P/'reviews/whole-site-v3/corridors.geojson'):
 if (p.get('from_id'),p.get('to_id')) in [('K1','D'),('D','E')]:
  regional.append((g,dict(kind='regional_study',name='Conditional eastern corridor',status='study_only',authority='not_secured',phase='P3',length_km=p['length_km'])))
extents=[(study,{'kind':'study_extent','name':'South-west design study; not a construction boundary'}),(town,{'kind':'town','name':'S: first complete town','phase':1}),(campus,{'kind':'production','name':'P: separate compute + repair campus','phase':1}),(future_south,{'kind':'future_town','name':'S: conditional town expansion','phase':2}),(north,{'kind':'future_town','name':'N: northern service town','phase':3}),(gateway_old,{'kind':'gateway','name':'E: gateway and its service settlement','phase':3})]
nodes=[(commons,{'node_id':'A03','kind':'node','name':'Climate commons','phase':1}),(campus,{'node_id':'B03','kind':'node','name':'Compute with a water stop-rule','phase':1}),(park,{'node_id':'C03','kind':'node','name':'Seasonal wash park','phase':1})]
for name,items in [('candidate-extents.geojson',extents),('candidate-blocks.geojson',blocks+facilities),('candidate-buildings.geojson',buildings),('candidate-movement.geojson',routes),('candidate-nodes.geojson',nodes),('regional-corridors.geojson',regional)]:write_geo(name,items)

# Exact source-frozen diagnostics. Grid slope and screening are not civil engineering evidence.
permanent=[g for g,p in buildings]
bad=[p['id'] for g,p in buildings if not scope.covers(g) or g.intersects(fixed) or g.intersects(channels.buffer(150))]
flood_buildings=[p['id'] for g,p in buildings if g.intersects(flood)]
node_routes={'A03_to_B03':LineString([(574150,6553950),(574600,6553950),(574600,6553500),(575100,6553500),(575100,6551600),(575700,6551600)]),
 'A03_to_C03':LineString([(574150,6553950),(573700,6553950),(573150,6553950),(573150,6554700),(573000,6554700)])}
canopies=[(box(xx,6553885,xx+12,6554015),{'kind':'canopy','form':'canopy','height_m':4.5}) for xx in [574075,574205]]+[(box(574075,yy,574217,yy+12),{'kind':'canopy','form':'canopy','height_m':4.5}) for yy in [6553885,6554003]]
write_geo('candidate-canopies.geojson',canopies)
write_geo('node-links.geojson',[(g,{'name':k,'kind':'proposed_network_trace','length_m':round(g.length)}) for k,g in node_routes.items()])
metrics={'status':'planning_review_not_final_submission','source_commit':'307eca1','boundary_revision':boundary['revision'],'nominal_site_km2':1656,'current_source_geodesic_km2':boundary['revised_scope_geodesic_km2'],'old_master_projected_km2':round(oldmaster.area/1e6,3),'new_study_projected_km2':round(study.area/1e6,3),'first_town_gross_projected_km2':round(town.area/1e6,3),'production_plot_projected_km2':round(campus.area/1e6,3),'new_dwellings':sum(p.get('dwellings',0) for g,p in buildings),'new_residents_scenario':2400,'household_size_assumed':2.5,'residential_buildings':sum(p['use']=='residential' for g,p in buildings),'residential_gfa_m2':sum(g.area*p['floors'] for g,p in buildings if p['use']=='residential'),'geometry_failures':bad,'buildings_intersecting_flood_screen':flood_buildings,'housing_to_compute_nearest_footprints_m':round(unary_union([g for g,p in buildings if p['use']=='residential']).distance(unary_union([g for g,p in buildings if p['use']=='compute']))),'node_route_m':{k:round(g.length) for k,g in node_routes.items()},'site_slope_sample':sample(town),'campus_slope_sample':sample(campus),'channel_intersection_in_C03_m':round(park.intersection(channels).length),'phase_one_it_mw_assumed':6,'heat_reuse_credited_pct':0}
metrics['buildings_on_service_plots']=[p['id'] for g,p in buildings if any(g.intersection(h).area>1 for h,q in facilities)]
metrics['buildings_on_routes']=[p['id'] for g,p in buildings if any(g.intersects(h) for h,q in routes)]
metrics['permanent_building_overlap_m2']=round(sum(g.area for g in permanent)-unary_union(permanent).area,4)
# Water is an incremental new-development scenario, not a fabricated balance for the fixed pilot.
water={'domestic':2400*.12*365,'public_services':30000,'industry':50000,'new_crop_trials':20*4000,'landscape':5000,'compute_cooling':6*1000*.6*8760*.02/1000,'panel_cleaning':3000}
gross=sum(water.values());reuse=75000;fresh=(gross-reuse)/.9
metrics['water']={'gross_end_use_m3_y':round(gross,2),'reclaimed_substitution_m3_y':reuse,'fresh_source_with_10pct_loss_m3_y':round(fresh,2),'components':water,'fixed_pilot_and_existing_quarter_demand':'unknown; must be reconciled before occupancy; never assumed zero'}
(O/'candidate-metrics.json').write_text(json.dumps(metrics,indent=2))
assert not bad and metrics['permanent_building_overlap_m2']<.01
assert metrics['new_dwellings']==960
assert not metrics['buildings_on_service_plots'] and not metrics['buildings_on_routes']
assert metrics['residential_gfa_m2']==115200

program=[
 {'phase':1,'period':'Scenario years 0-4 after enabling conditions','objective':'One operable town plus separate production','works':['Survey, lawful source and external access before occupancy','First housing, care, school, clinic, storage, reuse and public transport','Separate production gates; trial crops only outside fixed pilots'],'sequence_dependencies':['Access and resource tests -> utilities -> public services -> housing occupancy -> interruptible compute'],'trigger':'Lawful source passes quantity/quality tests; full pilot demand audited; access and service operations funded','zones':[('S',2400,960,900),('P',0,0,300)]},
 {'phase':2,'period':'Scenario years 4-8; may never start','objective':'Expand the existing town before another settlement','works':['Expand school and health capacity with housing','Extend source/renewables only with permits and demand','Conditional central compute campus has its own services'],'sequence_dependencies':['Maintain 12 months verified source headroom -> fund services -> release contiguous blocks'],'trigger':'80% occupancy and 12 months of audited source headroom after all fixed and new uses; committed jobs and public services','zones':[('S',4800,1920,2000),('P',0,0,400),('K',0,0,400)]},
 {'phase':3,'period':'Scenario years 8-15+; separate go/no-go decisions','objective':'Conditional northern town and eastern gateway','works':['Independent services at each settlement','Surveyed regional corridor and emergency alternatives','Gateway supply/receiving works and customs status before terminal construction'],'sequence_dependencies':['North source/access/services -> north town; independent east source/trade/access -> gateway settlement'],'trigger':'Each remote location passes its own water, power, access, demand and service tests; gateway has lawful trade status','zones':[('S',4800,1920,1800),('N',4800,1920,1800),('E',2400,960,1200),('K',0,0,800)]}
]
cumulative={};rows=[]
for phase in program:
 zs=[]
 for zid,r,d,j in phase['zones']:
  old=cumulative.get(zid,(0,0,0));tot=tuple(a+b for a,b in zip(old,(r,d,j)));cumulative[zid]=tot
  zs.append(dict(zone_id=zid,name={'S':'South-west town','P':'Local production','K':'Central compute','N':'North town','E':'Eastern gateway settlement'}[zid],new_residents=r,cumulative_residents=tot[0],new_dwellings=d,cumulative_dwellings=tot[1],new_jobs=j,cumulative_jobs=tot[2],basis='Declared capacity scenario; 2.5 residents/dwelling. Jobs are programme targets, not existing or secured employment. Remote town capacities are not detailed housing designs.'))
 phase['zones']=zs
 rows.append([phase['phase'],sum(z['new_residents'] for z in zs),sum(t[0] for t in cumulative.values()),sum(z['new_dwellings'] for z in zs),sum(t[1] for t in cumulative.values()),sum(z['new_jobs'] for z in zs),sum(t[2] for t in cumulative.values())])
(O/'phasing-programme-draft.json').write_text(json.dumps({'status':'review_draft_not_machine_submission','phases':program,'totals':rows},indent=2))
source_files=['AGENTS.md','brief/design-depth.json','brief/requirements.json','docs/design-depth-guide.md','skills/xcity-agent-submission/SKILL.md','brief/site-package/boundaries/scope_9_13.geojson','brief/site-package/boundaries/boundary-revision.json','brief/site-package/terrain/terrain_summary_9_13.json']
freeze={s:hashlib.sha256((R/s).read_bytes()).hexdigest() for s in source_files}
(O/'source-freeze.json').write_text(json.dumps({'git_commit':'307eca1','date':'2026-10-27','files':freeze},indent=2))

# Formal planning diagrams: flat source geometry, no decorative rendering or fake water.
BG='#F8F6F0'; INK='#263D44'; MUT='#66736D'; C={'town':'#C58B72','future_town':'#E3C6B5','production':'#9AAFB8','gateway':'#B9A4B5','study_extent':'none','agri':'#C3CAA9','reserve':'#E8E5DC','school':'#A7BCC8','clinic':'#C58B72','market':'#D1AE74','sport':'#AEBB99','care':'#CDBDA9','utilities':'#A7B7AF','arrival':'#B7C1C4'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK,'axes.labelcolor':INK})
pages=[]
def wrap(s,n=56):return '\n'.join(textwrap.wrap(s,n))
def text(f,x,y,s,size=11,**kw):return f.text(x,y,s,fontsize=size,color=kw.pop('color',INK),**kw)
def panel(f,x,y,title,body,width=54):
 text(f,x,y,title,13,weight='bold');text(f,x,y-.035,wrap(body,width),10.7,va='top',linespacing=1.55)
def page(num,title,sub):
 f=plt.figure(figsize=(16.54,11.69),facecolor=BG)
 text(f,.045,.954,'AGUA FINITA / V7 PLANNING REVIEW',10,weight='bold',color='#8D614D')
 text(f,.045,.902,title,25,weight='bold');text(f,.045,.864,sub,10.7)
 text(f,.045,.028,f'{num:02} / Jingyuan Huang / 27 October 2026 / Source freeze 307eca1 / Candidate design, not approved construction',8,color=MUT)
 return f
def polys(g):
 if g.is_empty:return
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for z in g.geoms:yield from polys(z)
def fill(ax,g,color,edge='none',lw=.6,hatch=None,alpha=1):
 for q in polys(g):
  q=orient(q,sign=1);v=[];codes=[]
  for ring in [q.exterior,*q.interiors]:
   xy=np.asarray(ring.coords)/1000;v.extend(xy);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(xy)-2)+[MPath.CLOSEPOLY])
  ax.add_patch(PathPatch(MPath(v,codes),facecolor=color,edgecolor=edge,lw=lw,hatch=hatch,alpha=alpha))
def line(ax,g,c=INK,lw=1,ls='-'):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  xy=np.asarray(g.coords)/1000;ax.plot(xy[:,0],xy[:,1],c=c,lw=lw,ls=ls)
 elif g.geom_type in ['Polygon','MultiPolygon']:line(ax,g.boundary,c,lw,ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(ax,q,c,lw,ls)
def label(ax,g,s,size=10,dx=0,dy=0):
 p=g if g.geom_type=='Point' else g.centroid;ax.text(p.x/1000+dx,p.y/1000+dy,s,fontsize=size,color=INK,ha='center',va='center',bbox=dict(facecolor=BG,edgecolor='none',alpha=.86,pad=2))
def frame(ax,bounds,scale):
 x0,y0,x1,y1=np.array(bounds)/1000;pad=(x1-x0)*.045;ax.set(xlim=(x0-pad,x1+pad),ylim=(y0-pad,y1+pad));ax.set_aspect('equal');ax.axis('off')
 x=x0+.02*(x1-x0);y=y0+.035*(y1-y0);ax.plot([x,x+scale/1000],[y,y],color=INK,lw=2);ax.text(x,y+.012*(y1-y0),f'{scale/1000:g} km',fontsize=9)
 ax.annotate('N',xy=(x1-.02*(x1-x0),y1-.02*(y1-y0)),xytext=(x1-.02*(x1-x0),y1-.12*(y1-y0)),arrowprops={'arrowstyle':'->','color':INK},ha='center',fontsize=10)
def base(ax,bounds):
 win=box(*bounds);fill(ax,scope.intersection(win),C['reserve']);fill(ax,flood.intersection(win),'none',edge='#CACFC3',lw=.2,hatch='///');line(ax,channels.intersection(win),'#9BAEB0',.55)
 fill(ax,fields.intersection(win),'#C3B785',edge='#8E875F');fill(ax,living.intersection(win),'#B9AA8B',edge='#8E875F');line(ax,scope.intersection(win),INK,.9)
def save(f,name):
 f.savefig(O/(name+'.png'),dpi=150,facecolor=BG);pages.append((f,name))

f=page(1,'Three towns within one whole-site structure','Three conditional settlements; separate production; fixed pilots preserved; the whole issued boundary remains the planning extent.')
a=f.add_axes([.035,.125,.61,.69]);base(a,scope.bounds)
# Five systems are roles, not percentages of paved or irrigated land.
for g,p in load(P/'geometry/structure.geojson'):
 if p.get('system') in ['energy_compute','agri_production'] and not g.intersects(fixed):
  fill(a,g,'#D9D0AB' if p['system']=='energy_compute' else '#D3D8C1',alpha=.65)
for g,p in regional:line(a,g,'#6D8791',1.15,'--')
for g,p in load(P/'geometry/structure.geojson'):
 if 'K1 Compute' in p.get('name',''):fill(a,g,C['production'],edge=INK,lw=.6)
label(a,Point(607000,6559000),'PIE DE PALO',10)
label(a,Point(572622,6557824),'MAIN ACCESS / STUDY',8,-3,0)
for g,p in extents:
 if p['kind']=='study_extent':continue
 fill(a,g,C.get(p['kind'],'none'),edge=INK,lw=.7)
for name,g,off in [('S / 12,000',town,(2,-1)),('N / 4,800',north,(3,1)),('E / 2,400',gateway_old,(3,-1)),('K / compute',centres['K1'],(3,1))]:label(a,g,name,10,*off)
label(a,fields,'FIXED FIELDS',8,1,-2);label(a,living,'FIXED LIVING',8,2,-2)
line(a,study,'#A86C50',1.8);frame(a,scope.bounds,10000)
panel(f,.68,.78,'S / first town, then contiguous growth','960 dwellings / 2,400 new residents in Phase 1. Grow this town before launching remote settlements. Ultimate 12,000 is a conditional programme, not existing stock.')
panel(f,.68,.59,'N / northern service town','Phase 3 only: up to 4,800 residents with its own water, school, care and local production. No dependence on daily travel to the first town.')
panel(f,.68,.42,'E / gateway settlement','Phase 3 only: up to 2,400 residents serving logistics and gateway industry. Regional corridor, water and trade status are separate go/no-go tests.')
panel(f,.68,.25,'The land between towns has a role','Conditional energy and crop research, channel conveyance and mountain/open-ground stewardship. Hatching is flood screening, not a lake or a blanket permanent no-build zone.')
f.legend(handles=[Patch(facecolor=c,label=n) for c,n in [(C['town'],'Town'),(C['production'],'Compute / repair'),('#D9D0AB','Energy role'),('#D3D8C1','Crop research'),(C['reserve'],'Unbuilt / stewardship')]],loc='upper left',bbox_to_anchor=(.045,.124),ncol=5,frameon=False,fontsize=8.5)
text(f,.05,.077,'Dashed corridors are studies. RN40 approach and external rights remain unresolved enabling works; no secured water is inferred.',9,color=MUT)
save(f,'01-whole-site')

f=page(2,'Five boundaries with five different jobs','Whole site / design study / actual Phase 1 / urban-design enlargement / three nodes and their camera crops are separate.')
a=f.add_axes([.045,.16,.59,.65]);base(a,study.buffer(700).bounds)
line(a,study,'#8D614D',1.8,'--');fill(a,town,C['town'],edge=INK);fill(a,campus,C['production'],edge=INK)
for g,p in routes:line(a,g,'#6C8187',.8)
for g,p in nodes:line(a,g,'#AA634C',2);label(a,g,p['node_id'],11,0,.16)
for k,g in node_routes.items():line(a,g,'#865E45',1.8,'--')
label(a,town,'S / COMPLETE FIRST TOWN',10,0,.55);label(a,campus,'P / SEPARATE PRODUCTION',9,0,-.25)
frame(a,study.buffer(700).bounds,1000)
panel(f,.68,.78,'Study is not construction',f'{study.area/1e6:.2f} km2 design-study rectangle. First-town gross extent {town.area/1e6:.2f} km2; production plot {campus.area/1e6:.2f} km2. Corridors and park works are separate quantities.')
panel(f,.68,.59,'B03 moves away from housing',f"Nearest proposed home-to-compute footprint gap: {metrics['housing_to_compute_nearest_footprints_m']:,} m. Commons-to-campus route: {metrics['node_route_m']['A03_to_B03']/1000:.2f} km. These are geometry distances, not acoustic or traffic compliance.")
panel(f,.68,.38,'C03 is genuinely elsewhere',f"Park access from the commons follows a {metrics['node_route_m']['A03_to_C03']/1000:.2f} km proposed route. High-ground entry, no permanent building in the channel; access closes on warning.")
panel(f,.68,.20,'Retired shortcut','No long heat pipe is proposed to the town. Heat reuse receives zero credit until a real nearby receiver, temperatures, seasonal demand and economics are verified.')
save(f,'02-extents-and-nodes')

f=page(3,'The first town is a complete spatial unit','Sixteen blocks / 960 dwellings / 2,400 residents at 2.5 people per dwelling / three storeys. All are design scenarios.')
a=f.add_axes([.045,.15,.61,.68]);fill(a,town,'#EEE9DC',edge=INK,lw=1.5)
for g,p in blocks:fill(a,g,'#E3D5BC',edge='#A99C84',lw=.7)
for g,p in buildings:
 if p['use']=='residential':fill(a,g,'#917766')
for g,p in facilities:fill(a,g,C[p['use']],edge=INK,lw=.6)
fill(a,commons,'#C5947E',edge=INK)
for g,p in routes:
 if g.intersects(town):line(a,g.intersection(town),'#607E80' if p['network']=='people' else '#B7C1C4',2.4 if p['network']=='people' else 1.3)
label(a,commons,'A03',10)
for g,p in facilities[:6]:
 label(a,g,{'school':'School','clinic':'Clinic','market':'Market/library','sport':'Sport','utilities':'Water/reuse','arrival':'Arrival'}[p['use']],8,0,.02)
for g,p in blocks:label(a,g,p['id'],8,0,.078)
frame(a,town.buffer(200).bounds,250)
panel(f,.70,.79,'Homes form four neighbourhoods','Each neighbourhood has four 60-dwelling blocks and local care. Four 15-dwelling buildings define each shared court; 64 buildings total. Housing GFA 115,200 m2; average 120 m2 per dwelling includes common circulation.')
panel(f,.70,.59,'The civic cross comes first','One central school/shared-sport plot, primary care, market/library, water/reuse, passenger arrival and four local care plots. School capacity scenario: 360 places, from 15% of 2,400 residents; demographic model to verify.')
panel(f,.70,.36,'Walking is a network','Continuous street grid plus civic and cross-town walking routes. Farther homes need measured safe routes and accessible shuttle service; no untested five-minute-city claim.')
panel(f,.70,.18,'Land outside the blocks is explicit','Public streets, care/service plots, the dry civic cross and unbuilt desert ground. The latter is neither irrigated landscape nor an excuse to count empty land as designed housing.')
save(f,'03-first-town')

f=page(4,'Three nodes test three city promises','Each node has its own place, users, access, operating rule and design question. Local images will be labelled with their actual extent.')
for i,(g,p) in enumerate(nodes):
 x=.045+i*.315;a=f.add_axes([x,.44,.285,.34]);bounds=g.buffer(120 if i==0 else 180).bounds;base(a,bounds)
 if i==0:
  for z,q in facilities:fill(a,z.intersection(box(*bounds)),C[q['use']],edge=INK)
  fill(a,g,'#C5947E',edge=INK)
  for xx in [574075,574205]:fill(a,box(xx,6553885,xx+12,6554015),'#806F5F')
  for yy in [6553885,6554003]:fill(a,box(574075,yy,574217,yy+12),'#806F5F')
 elif i==1:
  fill(a,g,C['production'],edge=INK)
  for z,q in buildings:
   if q['use']!='residential':fill(a,z,'#657984' if q['use']=='compute' else '#A3977F')
  line(a,LineString([(575420,6551600),(576080,6551600)]),'#566C75',2)
 else:
  fill(a,g,'none',edge='#6F8C77',lw=1.5);line(a,channels.intersection(box(*bounds)),'#8DA7AC',1.5)
  line(a,LineString([(573000,6554700),(572900,6554700),(572900,6554500)]),'#8D614D',2)
 frame(a,bounds,100 if i==0 else 250)
 text(f,x,.805,f"{p['node_id']} / {p['name']}",12.2,weight='bold')
 bodies=[('People before the heat','180 x 160 m climate commons, with deep perimeter shade, public drinking water and a nearby cooled refuge. Children, older people and shift workers have step-free entry. Shade geometry and structural/seismic design still require seasonal checks.'),('Production accepts limits','Three 2 MW hall scenarios, service spine and repair plots. Dry cooling, noise/dust monitoring and independent emergency access. No residential heat-network claim; local pilot receiver only after measured demand tests.'),('The channel stays a channel','Seasonal wash plus a removable, high-ground visiting route. No ornamental lake, no occupied pavilion on the flow line and no invented retention dam. Storm warning closes the lower route; a hydraulic study defines the actual safe edge.')]
 title,body=bodies[i];panel(f,x,.38,title,body,width=43)
 text(f,x,.13,'STATUS / Proposed geometry and operating intent.\nFinished views must be regenerated from this changed geometry.',9,color=MUT)
save(f,'04-three-nodes')

f=page(5,'Construction follows a capacity ledger','Relative timing is a scenario; every remote settlement must pass its own resource and service tests.')
cols=['Phase','New residents','Total residents','New homes','Total homes','New jobs','Total jobs']
table=f.add_axes([.045,.56,.91,.23]);table.axis('off')
tb=table.table(cellText=[[str(v) for v in r] for r in rows],colLabels=cols,cellLoc='center',bbox=[0,0,1,1]);tb.auto_set_font_size(False);tb.set_fontsize(11)
for (r,c),cell in tb.get_celld().items():cell.set_edgecolor('#D2D0C5');cell.set_facecolor('#E1D5C0' if r==0 else BG);cell.PAD=.15
for i,ph in enumerate(program):
 x=.045+i*.315;text(f,x,.49,f"PHASE {ph['phase']}",17,weight='bold',color='#8D614D');text(f,x,.453,ph['period'],9.5)
 text(f,x,.407,wrap(ph['objective'],38),12,weight='bold',va='top')
 text(f,x,.34,wrap(' / '.join(ph['works']),43),10.4,va='top',linespacing=1.5)
 text(f,x,.19,'START ONLY WHEN',10,weight='bold');text(f,x,.16,wrap(ph['trigger'],45),9.7,va='top',linespacing=1.4)
text(f,.045,.071,'S: south-west town / P: local production / K: central compute / N: north town / E: eastern gateway settlement. All jobs are uncontracted programme targets.',9,color=MUT)
save(f,'05-phasing-ledger')

f=page(6,'Water sets the construction threshold','Incremental new-development model only. Fixed pilot and living-quarter demand remain unknown and must be added before any supply claim.')
a=f.add_axes([.15,.25,.415,.52]);names=list(water);values=list(water.values());a.barh(names,values,color=['#A9BCC3','#B7C1C4','#9AADA4','#C3CAA9','#D4C9A8','#8FA5B1','#B6A68C']);a.invert_yaxis();a.set_xlabel('Gross end-use demand / m3 per year');a.spines[['top','right']].set_visible(False);a.set_facecolor(BG);a.tick_params(labelsize=10)
for j,v in enumerate(values):a.text(v+1200,j,f'{v:,.0f}',va='center',fontsize=10)
a.set_xlim(0,max(values)*1.3)
panel(f,.65,.77,'Demand comes before an assumed supply',f"Gross new demand {gross:,.0f} m3/year. Reclaimed substitution {reuse:,.0f}; source requirement {fresh:,.0f} with 10% distribution loss. This is a requirement to secure, not a well yield or entitlement.")
panel(f,.65,.56,'Cooling does not buy adjacency','6 MW peak IT, 60% annual utilisation and 0.02 L/kWh cooling WUE are scenario inputs. Imported electricity gets no unverified carbon-free credit. No hourly carbon-free percentage is carried over from the old 12 MW model.')
panel(f,.65,.34,'A 30% shortage changes operation','Protect safe drinking water, care and wastewater treatment. Curtail new crop trials and nonessential industry first; interrupt compute and discretionary cleaning. Fixed-pilot obligations require operator agreement and cannot be silently subordinated.')
text(f,.06,.13,'Under the arrays: forage grass and jojoba only. This draft neither reallocates the fixed fields nor invents their irrigation demand.\nNo occupancy gate clears until the combined existing + new supply balance is independently verified.',11,weight='bold')
save(f,'06-water-and-operation')

f=page(7,'What is corrected, what remains unproven','Independent content audit / not an organiser assessment / automatic gate success is not a design approval.')
audit=[('CORRECTED / Extents','A new 19.24 km2 study is separate from the 0.81 km2 first town and 0.42 km2 production plot. The entire issued site remains the structural planning extent.'),('CORRECTED / Facilities','Compute moved to a separate access-controlled plot. Distances are computed from candidate geometry; no heat-reuse percentage is assumed.'),('CORRECTED / Phasing','A zone-by-zone draft records new/cumulative people, dwellings and jobs. Phase 3 is conditional; future settlement blocks have not been claimed as already detailed.'),('SOURCE CONFLICT / Boundary','The boundary revision says 1,658.819819 km2 after the authorised open-seam closure. Some narrative site text still repeats the older internal-seam-only account. V7 uses the current geometry + revision record; nominal 1,656 remains the project label.'),('REQUIRED / Engineering and livelihood','Water source, combined pilot demand, external road rights, crossings, seismic structure, dust/noise, school demographics and job demand need verification. A 60 m terrain cell cannot certify a building plot.'),('REQUIRED / Submission and images','This review does not replace the published seven geometry files or assert a new 12/12. Core package integration, matrix reconciliation, camera/control generation and finished-image QA follow the planning review. Older images do not illustrate the changed production location.')]
for i,(title,body) in enumerate(audit):
 col=i%2;row=i//2;panel(f,.05+.49*col,.78-.235*row,title,body,width=62)
text(f,.05,.08,f"PRE-QA / {len(buildings)} candidate buildings / {metrics['new_dwellings']} dwellings / overlap {metrics['permanent_building_overlap_m2']} m2 / hard-screen conflicts {len(bad)} / flood-screen intersections {len(flood_buildings)}",10,weight='bold')
save(f,'07-audit')

with PdfPages(O/'agua-finita-v7-planning-review.pdf') as pdf:
 for fig,name in pages:pdf.savefig(fig,facecolor=BG);plt.close(fig)
for name in ['agua-finita-v7-planning-review.pdf','01-whole-site.png','02-extents-and-nodes.png','03-first-town.png','candidate-metrics.json','phasing-programme-draft.json','07-audit.png']:
 shutil.copy2(O/name,OUT/name)
print(json.dumps(metrics,indent=2));print('OUTPUT',OUT)
