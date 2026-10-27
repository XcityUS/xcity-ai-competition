"""V3 review only. Source-derived regional structure; does not replace submitted geometry."""
import json,hashlib,heapq,math
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch,Patch as LegendPatch
from matplotlib.collections import PatchCollection
from matplotlib.font_manager import FontProperties
from shapely.geometry import shape,mapping,box,Point,LineString
from shapely.ops import unary_union,transform,nearest_points
from shapely import contains_xy,make_valid
from pyproj import Transformer
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parents[1];S=R/'brief/site-package';O=P/'reviews/whole-site-v3';O.mkdir(parents=True,exist_ok=True)
OUT=R.parent.parent/'outputs/finite-water-city-v3';OUT.mkdir(parents=True,exist_ok=True)
t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
G=lambda f:unary_union([transform(t,shape(v['geometry'])) for v in json.loads((S/f).read_text())['features']])
scope=G('boundaries/scope_9_13.geojson');pilot=G('pilot-area/pilot_area.geojson');living=G('pilot-area/pilot_living_area.geojson');flood=G('water/flood_sensitive_dem.geojson').intersection(scope);channels=G('water/channels_dem.geojson').intersection(scope);fixed=pilot.union(living)
raw=np.array(Image.open(S/'terrain/dem_9_13_utm19s_60m.png')).astype(float)
# 300 m block-mean elevation: a regional screening grid, not survey/civil alignment.
nr,nc=raw.shape[0]//5,raw.shape[1]//5;dem=raw[:nr*5,:nc*5].reshape(nr,5,nc,5).mean((1,3));dy,dx=np.gradient(dem,300);slope=np.hypot(dx,dy)*100
x0,ymax=559572.4,6608973.7;xs=x0+(np.arange(nc)+.5)*300;ys=ymax-(np.arange(nr)+.5)*300;X,Y=np.meshgrid(xs,ys)
inside=contains_xy(scope,X,Y);wet=contains_xy(flood,X,Y);safe=inside & ~wet &(slope<3)&(dem<850)
def cells(mask):
 return unary_union([box(xs[c]-150,ys[r]-150,xs[c]+150,ys[r]+150) for r,c in zip(*np.where(mask))]).intersection(scope)
mountain=cells(inside & ((slope>=5)|(dem>=850)))
protect=mountain.union(flood.buffer(100).intersection(scope)).difference(fixed)
buildable=cells(safe).difference(protect.buffer(150)).difference(fixed.buffer(150))
def snap(x,y,maxd=5000):
 p=Point(x,y);q=p if buildable.covers(p) else nearest_points(p,buildable.buffer(-100))[1]
 assert p.distance(q)<maxd,(x,y,p.distance(q));return q
C={k:snap(x,y) for k,x,y in [('A',574000,6558000),('B',571000,6587000),('C',588000,6594000),('D',613000,6573000),('E',622500,6560000),('K1',582000,6577000),('K2',585000,6587000)]}
# Urban envelopes are reservations clipped by source-derived constraints, not built-up footprints.
urban={k:p.buffer(r).intersection(buildable) for k,p,r in [(k,C[k],r) for k,r in [('A',2100),('B',1700),('C',1700),('D',1600)]]}
compute={k:C[k].buffer(1600).intersection(buildable) for k in ['K1','K2']}
gateway=C['E'].buffer(2300).intersection(buildable);gateway=sorted(gateway.geoms,key=lambda g:g.area,reverse=True)[0] if gateway.geom_type=='MultiPolygon' else gateway
# Retain at most ~7 km2 shared gateway/industry reservation, subject to terrain/flood clipping.
if gateway.area>7e6:gateway=gateway.intersection(C['E'].buffer(1493))
axis=LineString([(C[k].x,C[k].y) for k in ['A','K1','K2','C']])
energy=axis.buffer(4300).intersection(buildable)
# Single non-overlapping land account: overlays appear in a separate routes dataset.
zones=[];remain=scope
def alloc(g,key,name):
 global remain
 q=g.intersection(remain)
 if not q.is_empty:zones.append((q,key,name));remain=remain.difference(q)
alloc(pilot,'fixed_agri','既定农光试点 / unchanged');alloc(living,'fixed_living','既定首期生活区 / outline only')
alloc(mountain,'protect','区域山地与坡地保育研究')
alloc(channels.buffer(150).intersection(scope),'wash','沟道行洪研究带 / 150m each side assumption')
alloc(flood,'floodstudy','洪泛敏感筛选 / 非永久禁建认定')
alloc(protect,'dry','额外保守退让研究 / 待复核')
priorland=P/'reviews/whole-site-v3/previous-submitted/geometry/land_use.geojson'
if priorland.exists():
 for f in json.loads(priorland.read_text())['features']:
  use=f['properties']['use']; key={'residential':'town','civic':'town','compute':'compute','energy':'energy','industry':'localindustry'}.get(use)
  if key:alloc(transform(t,shape(f['geometry'])),key,'首批街区 / '+use)
for k,g in urban.items():alloc(g,'town',k+' 城镇发展预留')
for k,g in compute.items():alloc(g,'compute',k+' 算力与维护集群预留')
alloc(gateway,'gateway','东部门户与出口产业共用预留')
alloc(energy,'energy','能源优先复合生产带 / conditional')
alloc(cells(inside & (slope<2)&(dem<800)),'agri','低坡生产研究区 / 未承诺灌溉')
alloc(remain,'dry','保留原生旱地 / 不启动建设')
# Proposed master-study envelope: pilot north edge / western parcel / flood edge / foothill.
masterseed=LineString([(571700,6551000),(573800,6555000),(C['A'].x,C['A'].y)]).buffer(2900)
master=masterseed.intersection(scope).difference(fixed).difference(protect)
# Retain the complete initial-neighbourhood and wash-node grounds in the wider envelope.
prior=P/'reviews/whole-site-v3/previous-submitted/geometry/master_area.geojson'
if prior.exists():master=master.union(unary_union([transform(t,shape(f['geometry'])) for f in json.loads(prior.read_text())['features']])).difference(fixed)
# Routing: 300m minimum-cost paths; minimise slope, flood exposure and fixed-area incursion.
cost=1+np.minimum(slope,30)**2*.12+wet*4
cost[~inside]=np.inf;cost[slope>12]=np.inf
cost[contains_xy(fixed,X,Y)]=np.inf
# Boundary cells/steep fixed living quarter are approached at the nearest permitted grid point.
def ij(p):
 r=int((ymax-p.y)/300);c=int((p.x-x0)/300)
 valid=np.isfinite(cost);rr,cc=np.where(valid);i=np.argmin((rr-r)**2+(cc-c)**2);return int(rr[i]),int(cc[i])
def route(p,q):
 a,b=ij(p),ij(q);dist={a:0};prev={};heap=[(0,a)];seen=set()
 while heap:
  d,u=heapq.heappop(heap)
  if u in seen:continue
  seen.add(u)
  if u==b:break
  for dr,dc in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
   v=u[0]+dr,u[1]+dc
   if not(0<=v[0]<nr and 0<=v[1]<nc) or not np.isfinite(cost[v]):continue
   seg=LineString([(xs[u[1]],ys[u[0]]),(xs[v[1]],ys[v[0]])])
   if not scope.covers(seg) or seg.intersects(fixed):continue
   nd=d+(cost[u]+cost[v])*.5*math.hypot(dr,dc)
   if nd<dist.get(v,1e99):dist[v]=nd;prev[v]=u;heapq.heappush(heap,(nd,v))
 if b not in dist:raise RuntimeError(('disconnected',a,b))
 path=[b]
 while path[-1]!=a:path.append(prev[path[-1]])
 g=LineString([(xs[c],ys[r]) for r,c in reversed(path)]); simplified=g.simplify(110)
 return simplified if scope.covers(simplified) and not simplified.intersects(fixed) else g
# Choose west boundary arrival by nearest approach to RN40; external approach is contextual, not submitted land.
roads=json.loads((S/'access/roads_osm.geojson').read_text())
print('road labels',[v['properties'] for v in roads['features']][:8])
roadgeoms=[transform(t,shape(v['geometry'])) for v in roads['features'] if '40' in str(v['properties'])]
rn40=unary_union(roadgeoms) if roadgeoms else unary_union([transform(t,shape(v['geometry'])) for v in roads['features']])
regional=nearest_points(C['A'],rn40)[1]
approach=LineString([C['A'],regional]); boundary=nearest_points(C['A'],approach.intersection(scope.boundary))[1]
links=[('P1 首批街区接驳','initial','A',Point(574750,6554900),C['A'],'P1'),('P1 西侧接入','entry','A',boundary,C['A'],'P1'),('P1 既定生活区接驳','living','A',nearest_points(living,C['A'])[0],C['A'],'P1'),('P2 生产主轴南段','A','K1',C['A'],C['K1'],'P2'),('P2 北段生产主轴','K1','K2',C['K1'],C['K2'],'P2'),('P2 西北生活支线','K2','B',C['K2'],C['B'],'P2'),('P2 北部生活支线','K2','C',C['K2'],C['C'],'P2'),('P3 绕山向东通道','K1','D',C['K1'],C['D'],'P3'),('P3 门户联系','D','E',C['D'],C['E'],'P3')]
routes=[]
for name,a,b,p,q,phase in links:
 g=route(p,q);routes.append((g,dict(name=name,from_id=a,to_id=b,phase=phase,length_km=round(g.length/1000,2),flood_band_km=round(g.intersection(flood).length/1000,2),status='300 m least-cost corridor; not road engineering')))
# A topology-based flood-crossing list, with crossings counted by components, not claimed bridge quantities.
def ft(g,**props):return dict(type='Feature',properties=props,geometry=mapping(make_valid(transform(inv,g))))
def save(name,features):(O/(name+'.geojson')).write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False))
save('structure',[ft(g,system=k,name=n,area_km2=round(g.area/1e6,4)) for g,k,n in zones])
save('corridors',[ft(g,**p) for g,p in routes])
save('master_study',[ft(master,name='西南深化研究范围',status='review envelope, not phase-one built area')])
save('centres',[ft(p,id=k,status='proposed reservation') for k,p in C.items()])
area={}
for g,k,n in zones:area[k]=area.get(k,0)+g.area/1e6
qa=dict(source_commit='c60cd1d',crs='EPSG:32719 regional calculation; outputs EPSG:4326',site_utm_km2=scope.area/1e6,area_account_km2=area,partition_gap_m2=scope.difference(unary_union([g for g,_,_ in zones])).area,partition_overlap_m2=sum(g.area for g,_,_ in zones)-unary_union([g for g,_,_ in zones]).area,proposal_fixed_overlap_m2=sum(g.intersection(fixed).area for g,k,n in zones if not k.startswith('fixed')),master_km2=master.area/1e6,routes=[p for _,p in routes],limits=['300m regional screening; source channels are DEM-derived, not surveyed','No water rights, grid connection, road right-of-way, soil or bridge approvals inferred','Production reservations are not irrigated or installed area; no new population promise','Gateway suitable reservation may be below indicative 7km2; remaining land is not forced into flood zone','This review does not replace canonical submission geometry or certify all twelve gates'])
(O/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
# Freeze hash before drawing, all views use these exact in-memory geometries.
h=hashlib.sha256(b''.join((O/f).read_bytes() for f in ['structure.geojson','corridors.geojson','master_study.geojson','centres.geojson'])).hexdigest();(O/'geometry.sha256').write_text(h+'\n')
font=FontProperties(fname='/System/Library/Fonts/STHeiti Light.ttc');plt.rcParams['axes.unicode_minus']=False
BG='#F8F6F0';INK='#263D44';COL={'protect':'#C9C9B9','wash':'#7B9992','floodstudy':'#F0EEE4','fixed_agri':'#748951','fixed_living':'#A25447','town':'#C58B6C','compute':'#536E7C','gateway':'#AC7884','localindustry':'#B49B88','energy':'#DFCA84','agri':'#B9C69D','dry':'#E8E3D7'}
def text(ax,x,y,s,size=12,**kw):return ax.text(x,y,s,fontproperties=font,fontsize=size,color=kw.pop('color',INK),**kw)
def polygons(g):
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for q in g.geoms:yield from polygons(q)
def fill(ax,g,color,alpha=1,lw=0,edge=None,hatch=None):
 # Compound paths preserve holes in protections / reservations.
 from matplotlib.path import Path as MPath
 from matplotlib.patches import PathPatch
 from shapely.geometry.polygon import orient
 for q in polygons(g):
  q=orient(q,sign=1);vs=[];codes=[]
  for ring in [q.exterior,*q.interiors]:
   a=np.asarray(ring.coords)/1000;vs.extend(a);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(a)-2)+[MPath.CLOSEPOLY])
  ax.add_patch(PathPatch(MPath(vs,codes),facecolor=color,edgecolor=edge or color,lw=lw,alpha=alpha,hatch=hatch))
def lines(ax,g,c,lw=1,style='-',alpha=1):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  a=np.array(g.coords)/1000;ax.plot(a[:,0],a[:,1],color=c,lw=lw,ls=style,alpha=alpha)
 elif hasattr(g,'geoms'):
  for q in g.geoms:lines(ax,q,c,lw,style,alpha)
 elif g.geom_type=='Polygon':lines(ax,g.boundary,c,lw,style,alpha)
def basemap(ax,mode):
 ax.set_facecolor(BG)
 for g,k,n in zones:fill(ax,g,COL[k] if mode!='geometry' else ('#D9DDD7' if k=='protect' else '#F8F6F0'),edge=('#B6C4BA' if k=='floodstudy' else ('#A0A8A4' if mode=='geometry' else None)),lw=.25 if mode=='geometry' else 0,hatch='....' if k=='floodstudy' else None)
 lines(ax,channels,'#7D9B9A',.6,alpha=.7)
 lines(ax,scope.boundary,INK,1.7)
 lines(ax,pilot.boundary,'#52683B',1.5);lines(ax,living.boundary,'#8C4037',1.6)
 ax.set(xlim=(559,634),ylim=(6540,6610));ax.set_aspect('equal');ax.axis('off')
 # Geographical north in projected UTM19S, grid north differs slightly; explicitly grid north.
 ax.annotate('',xy=(629,6605),xytext=(629,6600),arrowprops=dict(arrowstyle='-|>',color=INK,lw=1.4));text(ax,629,6606,'网格北',10,ha='center')
 ax.plot([563,573],[6541.5]*2,color=INK,lw=2);ax.plot([563,568,573],[6541.5]*3,'|',color=INK);text(ax,568,6542.5,'0       5       10 km',9,ha='center')
def routeplot(ax,mode):
 for g,p in routes:
  col='#B76F40' if p['phase']=='P1' else '#496F78'
  lines(ax,g,col,2.7 if p['phase']=='P1' else 1.7,'-' if p['phase']=='P1' else '--')
  if mode=='network':lines(ax,g.intersection(flood),'#BA4C42',3.3)
 for k,p in C.items():
  x,y=p.x/1000,p.y/1000;ax.scatter(x,y,s=60 if k in 'ABCDE' else 40,c=INK,edgecolors=BG,zorder=8)
  text(ax,x+.65,y+.5,{'A':'A 西南主城','B':'B 西北聚落','C':'C 北部服务镇','D':'D 东部服务镇','E':'E 东部门户','K1':'K1','K2':'K2'}[k],11,weight='bold',bbox=dict(facecolor=BG,edgecolor='none',pad=1))
 # External approach not a verified road or right of way.
 lines(ax,LineString([regional,boundary]),'#AD8E74',1.1,':')
 text(ax,559.5,6553,'西向区域接入\nRN40 方向／权属待核',9,ha='left')
def panel(ax,mode):
 ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
 if mode=='planning':
  text(ax,0,.98,'一个完整场地，分层实施',23,va='top')
  text(ax,0,.89,'1656 km² 全场地结构规划 · 审阅稿 V3',12)
  blocks=[('01  从既有系统启动','保留农光场与首期生活区；补齐接入、\n维护、供水与公共服务，连接西南发展区。'),('02  沿西侧低坡地组织城市','A 西南主城；B 西北生产生活聚落；\nC 北部农业服务镇。城镇之间保留生产地。'),('03  能源与算力成带，生活成点','K1/K2 集中算力、维修与热利用；\n能源复合生产带连接它们，避开山地沟道。'),('04  绕山向东，门户延后启动','D 东部服务镇接 E 门户／出口产业；\n通道沿北侧低坡地走，不穿越山体。')]
  y=.80
  for a,b in blocks:text(ax,0,y,a,15);text(ax,0,y-.045,b,11,va='top',linespacing=1.6);y-=.15
  text(ax,0,.16,'范围 ≠ 建设量',15);text(ax,0,.115,'色块是功能优先与条件性预留，\n不表示全域开发、灌溉或已经取得资源。',11,va='top',linespacing=1.6)
 elif mode=='network':
  text(ax,0,.98,'把联系画实，把风险标出',23,va='top')
  text(ax,0,.88,'区域通道 · 同廊预留电力、通信与水务',12)
  y=.78
  for title,body in [('P1  先接通既定生活与生产','橙色实线：先行接入与生活区接驳。\n现有生活区位于坡地，接驳须专项论证。'),('P2  西侧城镇与生产主轴','蓝灰虚线：分段建成，不把远期全线\n作为首期居民获得服务的前提。'),('P3  东向门户通道','沿山北侧连接 D 与 E；贸易需求、\n水电承载与道路工程成立后启动。'),('红段  洪泛敏感带内的通道','只作桥涵／路线比选研究段；\n图中走通，不等于工程已经可行。')]:
   text(ax,0,y,title,15);text(ax,0,y-.045,body,11,va='top',linespacing=1.6);y-=.17
  total=sum(p['length_km'] for _,p in routes);wetlen=sum(p['flood_band_km'] for _,p in routes)
  text(ax,0,.09,f'候选联系累计 {total:.1f} km；其中敏感带 {wetlen:.1f} km',11)
 else:
  text(ax,0,.98,'先核边界，再决定建设',23,va='top');text(ax,0,.88,'来源几何与本轮规划分开表达',12)
  y=.77
  for title,body in [('固定条件','深线：1656 km² 业主边界；\n绿色／红色轮廓：既定农光场／生活区。'),('地形与雨洪','灰色：区域坡地；点纹：洪泛敏感筛选；\n深绿细带：沟道行洪研究带。'),('本轮规划','A–E 城镇／门户预留，K1/K2 算力预留；\n虚线是需工程核验的候选联系。'),('西南深化研究范围','围绕农光场北侧、西南城镇与接入组织，\n由边界、山地和雨洪条件裁切；\n它不是首期建成面积。')]:
   text(ax,0,y,title,15);text(ax,0,y-.045,body,11,va='top',linespacing=1.6);y-=.17
  text(ax,0,.06,f'深化研究包络 {master.area/1e6:.1f} km²／分片继续核实',11)
legendnames={'protect':'山地坡地保育研究','wash':'沟道行洪研究带','floodstudy':'洪泛敏感筛选（待核）','fixed_agri':'既定农光试点','fixed_living':'既定首期生活区','town':'城镇发展预留','compute':'算力与维护预留','gateway':'门户与出口产业','localindustry':'首批加工维修','energy':'能源优先复合生产','agri':'低坡生产研究区','dry':'原生旱地保留'}
for mode,filename,title in [('planning','01_whole_site_plan','有限水城  /  全场地总体结构'),('network','02_corridors_and_phases','有限水城  /  城镇、通道与实施顺序'),('geometry','03_source_geometry','有限水城  /  来源边界与规划范围核对')]:
 fig=plt.figure(figsize=(20,12),facecolor=BG);ax=fig.add_axes([.025,.15,.67,.73]);pa=fig.add_axes([.72,.17,.26,.69]);basemap(ax,mode);routeplot(ax,mode);panel(pa,mode)
 if mode=='geometry':
  lines(ax,master.boundary,'#C88C58',1.8,'--')
  for g in [*urban.values(),*compute.values(),gateway]:lines(ax,g.boundary,'#647D83',1)
 else:
  text(ax,576.2,6552.2,'首批街区',10,ha='left');text(ax,569,6546,'既定农光场',10,ha='center',bbox=dict(facecolor=BG,edgecolor='none',pad=1));text(ax,584.5,6543.5,'既定首期生活区',10,ha='center')
  text(ax,602,6557,'Pie de Palo\n山地保护',14,ha='center',color='#68776A')
  text(ax,594,6583,'能源—算力\n复合生产带',12,ha='center',color='#786739')
  text(ax,573,6597,'北西生产研究区',11,ha='center');text(ax,605,6570,'东向生产研究区',11,ha='center')
 text(fig,.04,.95,title,28,transform=fig.transFigure);text(fig,.04,.912,'XCITY OPEN AGENT CALL  ·  Jingyuan Huang  ·  2026-10-26  ·  V3 REVIEW',11,transform=fig.transFigure)
 if mode!='geometry':
  handles=[LegendPatch(facecolor=COL[k],label=legendnames[k]) for k in COL];leg=fig.legend(handles=handles,loc='lower left',bbox_to_anchor=(.04,.055),ncol=6,frameon=False,prop=FontProperties(fname=font.get_file(),size=11),columnspacing=1.8)
 text(fig,.04,.025,'来源：XCITY c60cd1d｜业主边界、既定试点、Copernicus DEM 60m、DEM 沟道与洪泛筛选。新规划为概念预留；通道采用300m区域寻径，尚非道路工程。',9,transform=fig.transFigure)
 for ext in ['png','svg']:
  fig.savefig(OUT/(filename+'.'+ext),dpi=180,facecolor=BG);fig.savefig(O/(filename+'.'+ext),dpi=180,facecolor=BG)
 plt.close(fig)
print(json.dumps(qa,ensure_ascii=False,indent=2));print('OUTPUT',OUT,'HASH',h)
