"""Original English review sheets and geometry-derived massing controls. No legacy node aliases."""
import json, textwrap
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly,Patch
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import shape,box,LineString
from shapely.ops import transform,unary_union
from shapely.geometry.polygon import orient
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];S=R/'brief/site-package';O=P/'pages';O.mkdir(exist_ok=True)
t=Transformer.from_crs(4326,32719,always_xy=True).transform
load=lambda p:[(transform(t,shape(f['geometry'])),f['properties']) for f in json.loads(p.read_text())['features']]
geo={n:load(P/'geometry'/f'{n}.geojson') for n in ['structure','master_area','land_use','buildings','movement','nodes','phasing']}
scope=unary_union([g for g,p in load(S/'boundaries/scope_9_13.geojson')]);pilot=unary_union([g for g,p in load(S/'pilot-area/pilot_area.geojson')]);living=unary_union([g for g,p in load(S/'pilot-area/pilot_living_area.geojson')]);channels=unary_union([g for g,p in load(S/'water/channels_dem.geojson')]);flood=unary_union([g for g,p in load(S/'water/flood_sensitive_dem.geojson')])
master=geo['master_area'][0][0];x0,y0=json.loads((P/'tools/selected_site.json').read_text())['origin_utm_m'];qa=json.loads((P/'report/geometry-qa.json').read_text())
BG='#f5f1e8';INK='#263b3b';TEAL='#275f62';GOLD='#c79955';RED='#b7644e';COL={'living':'#c88868','energy_compute':'#6b8f95','agri_production':'#a9b397','industry':'#b8a079','port':'#b58b99','reserve':'#e3dfd3','residential':'#c88868','civic':'#cfb56c','compute':'#6b8f95','energy':'#a6b799','open_space':'#ece6d5','infrastructure':'#aeb9b8'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK,'axes.labelcolor':INK})
index=[]
def parts(g):
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from parts(q)
def fill(ax,g,c,edge='none',lw=.4,alpha=1):
 for q in parts(g):
  q=orient(q,sign=1);vs=[];codes=[]
  for ring in [q.exterior,*q.interiors]:
   a=np.asarray(ring.coords)/1000;vs.extend(a);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(a)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(vs,codes),facecolor=c,edgecolor=edge,lw=lw,alpha=alpha))
def line(ax,g,c,lw=1,ls='-'):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  a=np.asarray(g.coords)/1000;ax.plot(a[:,0],a[:,1],color=c,lw=lw,ls=ls)
 elif g.geom_type in ['Polygon','MultiPolygon']:line(ax,g.boundary,c,lw,ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(ax,q,c,lw,ls)
def new(num,title,sub):
 fig=plt.figure(figsize=(16.54,11.69),facecolor=BG)
 fig.text(.045,.953,'THE EVERYDAY CITY',size=11,weight='bold',color=TEAL)
 fig.text(.955,.953,f'XCITY / DESIGN REVIEW 01 / {num:02d}',size=9,ha='right')
 fig.text(.045,.898,title,size=25,weight='bold');fig.text(.045,.861,sub,size=11)
 fig.text(.045,.026,'Jingyuan Huang  |  27 October 2026  |  Concept proposal; capacities assumed unless stated; no approval claimed.',size=8)
 fig.text(.955,.026,f'{num:02d}',ha='right',size=10)
 return fig

def note(fig,x,y,title,body,width=45):
 fig.text(x,y,title,size=14,weight='bold',color=TEAL,va='top')
 fig.text(x,y-.04,'\n'.join(textwrap.wrap(body,width)),size=11,va='top',linespacing=1.55)
def finish(fig,num,key):
 path=O/f'{num:02d}-{key}.png';fig.savefig(path,dpi=150,facecolor=BG);plt.close(fig);index.append({'number':num,'path':str(path.relative_to(P)),'title':key.replace('-',' ').title()})
def frame(ax,bounds,pad=.05):
 a,b,c,d=bounds;dx=(c-a)*pad;dy=(d-b)*pad;ax.set_xlim((a-dx)/1000,(c+dx)/1000);ax.set_ylim((b-dy)/1000,(d+dy)/1000);ax.set_aspect('equal');ax.axis('off')
 ax.annotate('N',xy=(.965,.96),xytext=(.965,.86),xycoords='axes fraction',ha='center',arrowprops={'arrowstyle':'->','color':INK},color=INK)
 scale=100 if c-a<3000 else 1000 if c-a<15000 else 10000;xx=a/1000;yy=(b-(d-b)*.025)/1000;ax.plot([xx,xx+scale/1000],[yy,yy],color=INK,lw=2);ax.text(xx,yy-(d-b)/1000*.026,f'{scale:g} m',fontsize=8)
def mastermap(ax,bounds=None,movement=True):
 for g,p in geo['land_use']:fill(ax,g,COL.get(p['use'],'#d1c5ac'))
 for g,p in geo['buildings']:fill(ax,g,'#f9f7ef' if p.get('form')!='canopy' else '#dfc177',INK,.32)
 if movement:
  for g,p in geo['movement']:
   if g.geom_type=='LineString':line(ax,g,TEAL if p['network']=='people' else RED,.8 if p['network']=='people' else 1.2,'-' if p['network']=='people' else '--')
 frame(ax,bounds or (x0,y0,x0+1900,y0+1400))
# 01 full site: exact source extent, strategic reservations and links.
f=new(1,'A city of everyday centres','Whole competition site / fixed boundary / source-derived research framework')
a=f.add_axes([.04,.10,.63,.71])
for g,p in geo['structure']:fill(a,g,COL[p['system']])
line(a,scope,INK,1.2);line(a,channels,'#a8b8b5',.5)
for g,p in load(P/'report/regional-corridors.geojson'):line(a,g,TEAL,1.4,'--' if p['phase']>1 else '-')
for g,p in load(P/'report/centres.geojson'):
 a.scatter(g.x/1000,g.y/1000,s=25,color=TEAL);a.text(g.x/1000+.4,g.y/1000+.4,p['name'],size=9)
frame(a,scope.bounds);note(f,.70,.79,'One main city first','A complete primary district supports daily life. Two conditional service towns grow only with their own services and resource contracts. The eastern gateway remains a later shared freight reserve.')
note(f,.70,.51,'Five systems, linked','Homes and public services define the primary city; regional energy and compute form a separate production backbone; agricultural research occupies low-slope land; repair and processing accompany centres; trade is reserved at the east.')
note(f,.70,.23,'Land is not installed capacity','Reserve colours show proposed roles, not realised buildings, irrigation or a verified resource entitlement. Fixed pilots remain unchanged.',40);finish(f,1,'whole-site')
f=new(2,'Read the ground before drawing the city','DEM-derived screening is neither a lake nor a surveyed flood boundary')
a=f.add_axes([.04,.12,.62,.68]);fill(a,scope,'#e7e1d4');fill(a,flood.intersection(scope),'#cdd9d4',alpha=.8);line(a,channels,TEAL,.6);fill(a,pilot,GOLD);fill(a,living,RED);line(a,scope,INK,1);line(a,master,RED,2);frame(a,scope.bounds)
note(f,.70,.79,'Fixed facts','The issued boundary covers 1,656.684229 km2 geodesically. The 13.9 km2 agrivoltaic pilot and 2.48 km2 first living-quarter outline are fixed separately. No internal stock or service capacity is invented.')
note(f,.70,.48,'Screening, then verification','60 m DEM and regional flood sensitivity inform siting. Neither proves site safety. Actual channels have no permanent construction. The first district is clear of the supplied 150 m channel-research screen.')
note(f,.70,.18,'Source','XCITY site package at 9e504de; boundary revision 2026-10-27-seam-closure. Survey, small washes and utility rights remain unverified.');finish(f,2,'site-reading')
f=new(3,'Choose proximity without hiding the terrain cost','Three spatially meaningful fit tests / same 1.9 x 1.4 km programme')
a=f.add_axes([.06,.17,.52,.60]);fill(a,scope,'#e6e0d2');fill(a,pilot,GOLD);fill(a,flood.intersection(box(570000,6550000,578000,6560000)),'#cbd8d2')
for i,v in enumerate(json.loads((P/'tools/selected_site.json').read_text())['comparison']):
 x,y=v['origin_utm_m'];g=box(x,y,x+1900,y+1400);line(a,g,RED if v['selected'] else TEAL,2);a.text(x/1000,y/1000+.3,str(i+1),weight='bold')
frame(a,(569500,6549500,577000,6557000));note(f,.64,.77,'1 / Selected','About 1.1 km from the pilot, with a 2.64% mean screened slope. A productive trail reaches the actual fixed field edge. Cut/fill, drainage and accessible gradients need a detailed survey.',46)
note(f,.64,.48,'2 / Flatter but more remote','Mean screened slope 1.26%, about 3.0 km from the pilot. A simpler grading starting point, but weaker direct connection between farm services and city life.',46)
note(f,.64,.23,'3 / Intermediate','Mean screened slope 1.86%, about 2.6 km from the pilot. Not chosen because it adds distance without resolving external rights. Distances are geometric screening, not engineered routes.',46);finish(f,3,'siting-choice')
f=new(4,'Six neighbourhoods. One everyday spine.','Complete first district / 1,440 homes / 3,600 residents / services in the first phase')
a=f.add_axes([.04,.10,.70,.71]);mastermap(a)
for j in range(2):
 for i in range(3):a.text((x0+230+i*360)/1000,(y0+660+j*380)/1000,f'{j*3+i+1}',size=16,weight='bold',ha='center')
note(f,.77,.77,'Homes','Six neighbourhoods. Each has four court units and 240 homes. Three-storey wings frame common rooms and shaded shared ground.',29)
note(f,.77,.49,'Public life','School, health, market, kitchen, library, childcare and indoor heat refuge line one civic spine.',29)
note(f,.77,.27,'Productive edge','Compute, workshops and farm services use perimeter freight access. Utility yards sit on the east edge.',29);finish(f,4,'first-district')
f=new(5,'A courtyard is a shared address','Urban-design enlargement / one complete 240-home neighbourhood')
a=f.add_axes([.045,.16,.59,.64]);mastermap(a,(x0+60,y0+470,x0+460,y0+870));note(f,.69,.78,'Four courts, different thresholds','Four groups each contain four 48 x 12 m residential wings, three storeys high, with 15 homes per wing. The open corners allow several entries rather than a gated superblock.',42)
note(f,.69,.48,'Daily use before spectacle','Shared laundry, a common room, shaded sitting and play belong to each court. The surrounding slow access loop supports emergency vehicles; inner walks remain pedestrian.',42)
note(f,.69,.22,'What remains to resolve','Dwelling plans, door positions, lifts and accessible gradients need the next architectural iteration. 115.2 m2 gross floor area per assumed dwelling is a capacity allowance, not saleable area.',42);finish(f,5,'courtyard-neighbourhood')
f=new(6,'The public street earns its space','Civic and service section / declared dimensions, not construction engineering')
a=f.add_axes([.07,.30,.86,.42]);a.set_xlim(0,100);a.set_ylim(-2,20);a.axis('off')
for x,w,h,c,label in [(0,16,9.9,RED,'Homes / 3 floors'),(16,4,0,GOLD,'Porch 4 m'),(20,6,4.5,GOLD,'Shaded walk 6 m'),(26,10,0,'#b8c1aa','Dry commons 10 m'),(36,6,0,'#b8c1aa','Cycle / foot 6 m'),(42,6,0,'#c9c0ad','Emergency 6 m'),(48,4,0,'#c9c0ad','Filter edge 4 m'),(52,20,6.6,GOLD,'Public services / 2 floors')]:
 a.add_patch(Poly([(x,0),(x+w,0),(x+w,h if h else .4),(x,h if h else .4)],facecolor=c,edgecolor=INK,lw=.5));a.text(x+w/2,-1,label,rotation=35,ha='right',va='top',size=9)
a.plot([0,98],[0,0],color=INK);note(f,.07,.78,'Human scale, lower-rise form','Courtyard housing reaches 9.9 m; public buildings reach 6.6 m. Lightweight shade is conceptually 4.5 m high. Short independent wings require seismic separation, structural design and roof wind-load verification.',105)
note(f,.07,.16,'Heat and wind','Shade protects routes and edges; indoor refuge handles extreme heat. No lawn or decorative lake. Wind-filtering edges are a design hypothesis, pending local wind and thermal testing.',105);finish(f,6,'street-section')
f=new(7,'People first. Every crossing visible.','Actual line intersections registered; the crossing count is not a safety score')
a=f.add_axes([.045,.12,.68,.69]);mastermap(a)
for g,p in geo['movement']:
 if p.get('kind')=='interface':a.scatter(g.x/1000,g.y/1000,s=22,facecolor=BG,edgecolor=RED,zorder=10)
note(f,.76,.78,'Public network','Court walks join two transverse public routes and the civic spine. A longer productive trail connects to the fixed farm edge.',30)
note(f,.76,.52,'Controlled interfaces',f"{qa['interfaces']} same-level interfaces are recorded from line geometry. Shared loops are 10 km/h concept operation; pedestrian crossings require machine stop and manual release.",30)
note(f,.76,.22,'Next check','Audit actual doors, dropped kerbs, waiting space, corner visibility and turning envelopes. Path/building conflicts are tested separately.',30);finish(f,7,'movement')
f=new(8,'One water account. Real priorities.','Full first-phase use scenario / fixed pilot demand is an unverified placeholder')
a=f.add_axes([.08,.27,.51,.49]);vals=[183960,788.4,650000,12000,45000];labels=['Domestic + public','Compute','Agriculture incl. pilot','Landscape','Industry'];a.barh(labels,vals,color=[RED,TEAL,'#91a177',GOLD,'#9a8f80']);a.invert_yaxis();a.set_xlabel('m3 / year');a.spines[['top','right']].set_visible(False)
for i,v in enumerate(vals):a.text(v+5000,i,f'{v:,.1f}',va='center',size=9)
note(f,.67,.77,'891,748.4 m3 / year','183,960 domestic; 788.4 compute; 650,000 agriculture including a 600,000 fixed-pilot placeholder; 12,000 landscape; 45,000 industry. Actual pilot and fixed living-quarter demand must be verified.',45)
note(f,.67,.47,'Supply scenario','180,000 m3 reuse plus 711,748.4 delivered fresh water. With 40,000 distribution losses, fresh abstraction would be 751,748.4 m3. None is an acquired water right.',45)
note(f,.67,.20,'30% gross-use reduction','Cut 12,000 landscape, 35,000 industrial, 180,000 agricultural and 40,524.52 discretionary domestic/public use. Residual domestic allowance is about 109 L/person/day. Pilot reductions require operator agreement.',45);finish(f,8,'water-priorities')
f=new(9,'Energy serves a complete city','Solar, storage and a flexible 8 MW IT peak / hourly simulation disclosed separately')
e=json.loads((P/'report/energy-results.json').read_text());a=f.add_axes([.07,.24,.54,.51]);v=np.loadtxt(P/'report/hourly-energy.csv',delimiter=',',skiprows=1);a.plot(v[:72,0],v[:72,1],label='Total load',color=RED);a.plot(v[:72,0],v[:72,2],label='PV output',color=GOLD);a.plot(v[:72,0],v[:72,5],label='Grid import',color=TEAL);a.legend(frameon=False);a.set_xlabel('Hour / synthetic summer sample');a.set_ylabel('MW');a.spines[['top','right']].set_visible(False)
note(f,.67,.77,'Declared supply scenario','20 MW PV and 180 MWh battery; grid limit 20 MW. Battery protected reserve 72 MWh supports a 1 MW critical-service scenario for 72 hours, subject to equipment and load verification.',43)
note(f,.67,.46,'Two matching measures',f"Fully matched hours: {e['fully_matched_hours_pct']:.2f}%. Clean-energy share: {e['clean_energy_share_pct']:.2f}%. Synthetic 8,760-hour dispatch is a scenario, not site climate or a supply contract.",43)
note(f,.67,.21,'Heat has a receiver','2,628 MWh/year usable heat target goes to named drying and processing workshops. Temperature lift, losses and seasonal demand require equipment and customer contracts.',43);finish(f,9,'energy')
f=new(10,'Three places test the same city','A01 homes / B03 useful compute / C02 the working farm edge')
a=f.add_axes([.045,.12,.65,.69]);mastermap(a)
frame(a,master.bounds)
for g,p in geo['nodes']:
 line(a,g,RED,2);q=g.representative_point();a.text(q.x/1000,q.y/1000,p['node_id'],size=18,weight='bold',ha='center',bbox={'facecolor':BG,'edgecolor':'none','alpha':.9})
note(f,.74,.77,'A01 / Courtyard Homes','Inside the western neighbourhood. A complete court and its shared services test everyday life without employer-controlled housing.',32)
note(f,.74,.49,'B03 / Useful Compute','At the southern productive edge. Separate service access, heat reception and paid maintenance connect production to public benefit.',32)
note(f,.74,.21,'C02 / Working Farm Edge','The southwest service campus and trail reach the actual fixed pilot edge. No new buildings enter the pilot.',32);finish(f,10,'node-locator')
for num,(g,p) in enumerate(geo['nodes'],11):
 f=new(num,p['node_id']+' / '+p['name'],'Detailed concept plan / location, dimensions, access and use')
 a=f.add_axes([.045,.19,.61,.60]);mastermap(a,(x0+80,y0+70,x0+870,y0+380) if p['node_id']=='C02' else g.bounds);line(a,g,RED,1.7)
 if p['node_id']=='A01':texts=[('Everyday home','Four courts contain 240 homes, shared laundry and common rooms. Flexible household tenure accommodates residents, rotating workers and care households without tying the home to a job.'),('Normal / exceptional use','Morning school trips and shared meals use the pedestrian interior. In heat or Zonda alerts, common rooms become indoor refuge; emergency access remains on the perimeter.'),('Architectural next step','Resolve real apartment layouts, accessible entries, shaded thresholds, fire separation, acoustic privacy and seismic joints. Shared ground needs a funded resident-managed maintenance agreement.')]
 elif p['node_id']=='B03':texts=[('Useful production','Two 180 x 75 m halls, four 110 x 35 m workshops and an 80 x 30 m heat reception building form a service campus. A service loop remains south of everyday living.'),('Normal / exceptional use','Separate delivery, repair and public learning access. Dry cooling avoids evaporative towers; high heat can increase electrical demand and reduce IT output. Workers retain pay during contracted reassignment.'),('Heat and accountability','A 5% IT-energy heat-use target names the processing workshops as receivers. A physical meter, operating contract and fallback heat rejection are required; arrows alone do not prove reuse.')]
 else:texts=[('A working boundary','Three 140 x 20 m teaching and service buildings support repair, sorting and training. A 560 x 8 m shaded public frontage leads to a productive trail and the real protected field edge.'),('Normal / exceptional use','Visitors stop at managed viewing gates. Farm servicing uses the rear loop; the trail is closed in dust or storm alerts. No tall crops are proposed under fixed arrays.'),('Scope and honest distance','This is a linked interface, not a claim that the city touches every field. The trail and service alignment require wash, gradient and rights verification. The original pilot remains unchanged.')]
 for yy,(title,body) in zip([.79,.52,.24],texts):note(f,.70,yy,title,body,40)
 finish(f,num,p['node_id'].lower()+'-plan')
f=new(14,'Build a complete first chapter','First works and observable growth triggers / no automatic expansion dates')
a=f.add_axes([.06,.18,.88,.58]);a.axis('off')
steps=[('00 / VERIFY','Survey, small washes, soils, water rights, utility and external access commitments.\nNo occupancy promised.'),('01 / COMPLETE','Access + emergency; water and sanitation; primary power; homes + school + care; market + maintenance.\nLater phases may stop.'),('02 / CONNECT','North town and energy backbone only after audited resource margin >=20%, occupancy >=80%, funded services and safe access.'),('03 / GATEWAY','Eastern town and freight reserve only with binding demand, verified corridors, resource capacity and funded local services.')]
for i,(h,b) in enumerate(steps):
 x=.015+i*.25;a.add_patch(Poly([(x,.12),(x+.225,.12),(x+.225,.88),(x,.88)],transform=a.transAxes,facecolor='#e4dfd1',edgecolor=TEAL));a.text(x+.015,.81,h,transform=a.transAxes,size=14,weight='bold');a.text(x+.015,.69,'\n'.join(textwrap.wrap(b,28)),transform=a.transAxes,size=11,va='top',linespacing=1.6)
finish(f,14,'phasing')
f=new(15,'Housing is not a labour contract','Governance, work and public-service continuity')
note(f,.07,.78,'Homes and common ground','A proposed civic housing trust holds common land and essential service assets. Mixed tenure includes a declared 25% protected rental target. Residents have public access and housing rights independent of a compute operator. This is a proposed governance model, not an existing legal entity.',65)
note(f,.55,.78,'Jobs and skills','1,500 jobs: 300 care/education, 300 farm/food, 220 repair, 180 energy/compute, 250 retail/culture and 250 utilities/logistics/administration. Of these, 1,350 are held by residents and 150 by incoming specialists. Training needs named providers and funded paid placements.',64)
note(f,.07,.39,'A population account','3,600 residents: 1,350 local workers, 200 remote workers, 1,000 children/students, 500 retired adults and 550 carers or jobseekers. These exclusive scenario categories sum to the resident target. Pensions, household transfers and remote income support non-local employment.',65)
note(f,.55,.39,'Public audit and exit','Hourly aggregate energy/water/compute records; daily published summaries; annual independent meter and financial audit. Household tracking is excluded. AI suggests schedules; humans retain authority over basic service priority. Operator exit triggers an asset handover and reserve-funded service continuity plan.',64);finish(f,15,'governance')
f=new(16,'Know what is designed, assumed and unresolved','Review dashboard / numbers are not approval')
a=f.add_axes([.07,.22,.56,.56]);a.axis('off');items=[['Phase-one district',f"{qa['phase_one_planar_km2']:.3f} km2 planar; geodesic account separate"],['Homes / residents / jobs','1,440 / 3,600 / 1,500 scenario'],['Residential form','96 wings; 3 floors; 24 courts'],['Public facilities','360 primary + 240 secondary school places; 120 childcare'],['Peak / mean IT','8 MW / 6 MW; PUE 1.30 target'],['Gross water use','891,748.4 m3/year scenario'],['Critical electricity reserve','72 MWh deliverable scenario'],['Same-level interfaces',str(qa['interfaces'])],['Fixed-pilot building overlap',f"{qa['building_fixed_overlap_m2']:.2f} m2"],['Land account gap',f"{qa['land_partition_gap_m2']:.2f} m2"]];tab=a.table(cellText=items,colWidths=[.40,.60],loc='center',cellLoc='left');tab.auto_set_font_size(False);tab.set_fontsize(10);tab.scale(1,2.2)
for (r,c),cell in tab.get_celld().items():cell.set_facecolor('#e6e0d2' if r%2==0 else BG);cell.set_edgecolor('#cfc9bc')
note(f,.70,.77,'Accepted trade-off','Sacrifice uninterrupted compute output and the shortest possible productive routes to protect independent housing, public life and a clear service boundary.',40)
note(f,.70,.48,'Unresolved engineering','Survey, hydrology, access rights, utility capacity, seismic and fire design, grading and actual dwelling plans remain unverified. Regional routes are 300 m-grid studies.',40)
note(f,.70,.19,'Submission status','Independent English proposal; A/B/C IDs under current rules. Public preview authorised 27 October 2026. Automatic compliance and independent design review remain separate.',40);finish(f,16,'review-dashboard')
# Geometry-derived aerial controls for exact selected extents; real level changes remain unmodelled.
(P/'media/controls').mkdir(parents=True,exist_ok=True)
for key,bounds,elev,azim in [('district',(x0,y0,x0+1900,y0+1400),53,-65),('A01',geo['nodes'][0][0].bounds,48,-62),('B03',geo['nodes'][1][0].bounds,43,-68),('C02',(x0+80,y0+70,x0+870,y0+380),40,-65)]:
 fig=plt.figure(figsize=(14,9),facecolor='#e8dfcc');ax=fig.add_subplot(111,projection='3d');ax.set_facecolor('#e8dfcc');xmin,ymin,xmax,ymax=bounds
 for g,p in geo['buildings']:
  if not g.intersects(box(*bounds)):continue
  for q in parts(g):
   xy=np.array(q.exterior.coords)[:-1];xy[:,0]-=xmin;xy[:,1]-=ymin;h=p.get('height_m',3.3);color=COL.get(p['use'],GOLD)
   roof=[(x,y,h) for x,y in xy];faces=[roof]
   if p.get('form')!='canopy':
    for i in range(len(xy)):
     j=(i+1)%len(xy);faces.append([(xy[i,0],xy[i,1],0),(xy[j,0],xy[j,1],0),(xy[j,0],xy[j,1],h),(xy[i,0],xy[i,1],h)])
   ax.add_collection3d(Poly3DCollection(faces,facecolor=color,edgecolor='#525a55',linewidths=.3,alpha=1))
 ax.set_xlim(0,xmax-xmin);ax.set_ylim(0,ymax-ymin);ax.set_zlim(0,80 if key=='district' else 30);ax.set_box_aspect((xmax-xmin,ymax-ymin,(xmax-xmin)*.2));ax.view_init(elev=elev,azim=azim);ax.axis('off');fig.subplots_adjust(0,0,1,1);fig.savefig(P/'media/controls'/f'{key}-aerial.png',dpi=160);plt.close(fig)
(P/'report/page-index.json').write_text(json.dumps(index,indent=2));print('Drawn',len(index),'English design sheets and four geometry controls')
