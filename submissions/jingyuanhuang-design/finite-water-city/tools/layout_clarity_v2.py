"""Planning review only: source geometry frozen, proposed connection kept in a separate layer."""
import json,hashlib,shutil
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Rectangle, Circle
from matplotlib.collections import PatchCollection
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from shapely.geometry import shape,box,LineString,Point,mapping
from shapely.ops import transform,unary_union
from pyproj import Transformer,Geod
P=Path(__file__).resolve().parents[1];R=P.parents[2];D=P/'reviews/layout-v2';G=D/'geometry-source';D.mkdir(exist_ok=True)
FP=FontProperties(fname='/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
plt.rcParams.update({'font.family':FP.get_name(),'font.size':13,'axes.unicode_minus':False,'svg.fonttype':'path','pdf.fonttype':42,'hatch.linewidth':.35})
from matplotlib import font_manager
font_manager.fontManager.addfont('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
plt.rcParams['font.family']=FP.get_name()
t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
INK='#183D4D';MUT='#687474';PAPER='#F8F6F0';SAND='#EEE7D9';ORANGE='#C88C58';BLUE='#718F9C';RES='#E8DDC2';CIV='#BE8169';AG='#B5C199';IND='#AAB7BC';EN='#E0C986'
def read(path):return [(f['properties'],transform(t,shape(f['geometry']))) for f in json.loads(Path(path).read_text())['features']]
geo={f.stem:read(f) for f in G.glob('*.geojson')}
site=R/'brief/site-package';scope=unary_union([g for p,g in read(site/'boundaries/scope_9_13.geojson')]);pilot=unary_union([g for p,g in read(site/'pilot-area/pilot_area.geojson')]);flood=unary_union([g for p,g in read(site/'water/flood_sensitive_dem.geojson')]);channels=read(site/'water/channels_dem.geojson');master=geo['master_area'][0][1]
source_hash={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(G.glob('*.geojson'))};finger=hashlib.sha256(json.dumps(source_hash,sort_keys=True).encode()).hexdigest()
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for c in g.geoms for p in polys(c)] if hasattr(g,'geoms') else []
def fill(ax,g,color,edge='none',lw=.5,alpha=1,hatch=None,z=1):
 ps=[Patch(np.asarray(q.exterior.coords)/1000,closed=True) for q in polys(g)]
 if ps:ax.add_collection(PatchCollection(ps,facecolor=color,edgecolor=edge,linewidth=lw,alpha=alpha,hatch=hatch,zorder=z))
def outline(ax,g,c=INK,lw=1,z=8,ls='-'):
 if g.is_empty:return
 if g.geom_type=='Polygon':ax.plot(np.asarray(g.exterior.coords)[:,0]/1000,np.asarray(g.exterior.coords)[:,1]/1000,c=c,lw=lw,zorder=z,ls=ls)
 elif g.geom_type=='LineString':ax.plot(np.asarray(g.coords)[:,0]/1000,np.asarray(g.coords)[:,1]/1000,c=c,lw=lw,zorder=z,ls=ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:outline(ax,q,c,lw,z,ls)
def text(ax,x,y,s,fs=13,c=INK,ha='left',va='center',boxcolor=None,**kw):
 return ax.text(x/1000,y/1000,s,fontsize=fs,color=c,ha=ha,va=va,zorder=30,bbox=dict(facecolor=boxcolor,edgecolor='none',pad=3,alpha=.94) if boxcolor else None,**kw)
def label(ax,xy,s,xytext,c=INK,fs=13):
 ax.annotate(s,xy=np.array(xy)/1000,xytext=np.array(xytext)/1000,fontsize=fs,color=c,ha='left',va='center',zorder=40,bbox=dict(fc=PAPER,ec='none',pad=4,alpha=.96),arrowprops=dict(arrowstyle='-',color=c,lw=.9,connectionstyle='angle3'))
def setup(ax,bounds,scale,bar_at=None):
 x0,y0,x1,y1=bounds;ax.set_xlim(x0/1000,x1/1000);ax.set_ylim(y0/1000,y1/1000);ax.set_aspect('equal');ax.axis('off')
 x,y=bar_at if bar_at else (x0+(x1-x0)*.035,y0+(y1-y0)*.035)
 ax.plot([x/1000,(x+scale)/1000],[y/1000,y/1000],c=INK,lw=3,zorder=50)
 for xx in [x,x+scale]:ax.plot([xx/1000,xx/1000],[y/1000,(y+scale*.012)/1000],c=INK,lw=1,zorder=50)
 text(ax,x,y+scale*.035,f'0                         {scale/1000:g} km',10,va='bottom')
 xx=x1-(x1-x0)*.05;yy=y1-(y1-y0)*.07
 ax.annotate('',xy=(xx/1000,(yy+scale*.12)/1000),xytext=(xx/1000,yy/1000),arrowprops=dict(arrowstyle='-|>',color=INK,lw=1.1),zorder=60)
 text(ax,xx,yy+scale*.15,'N',11,ha='center',va='bottom')
def new(num,title,sub):
 f=plt.figure(figsize=(16.54,11.69),facecolor=PAPER)
 f.text(.045,.955,'AGUA FINITA  /  有限水城',fontsize=12,color=INK)
 f.text(.955,.955,f'布局澄清 V2  ·  {num}',fontsize=11,color=MUT,ha='right')
 f.text(.045,.903,title,fontsize=27,color=INK)
 f.text(.045,.867,sub,fontsize=12,color=MUT)
 f.text(.045,.032,'规划审阅稿 / 未公开；非测绘或工程结论。来源：竞赛边界、试点、DEM派生沟道 + 本方案冻结几何。',fontsize=9,color=MUT)
 f.text(.955,.032,'源几何 '+finger[:12]+'  /  2026-10-25',fontsize=9,color=MUT,ha='right')
 return f
def card(f,y,n,title,body,c=INK):
 f.text(.735,y,n,fontsize=23,color=ORANGE)
 f.text(.777,y+.005,title,fontsize=16,color=c)
 f.text(.735,y-.043,body,fontsize=12.5,color=MUT,va='top',linespacing=1.65)
def land(ax,gray=False):
 colors={'residential':RES,'civic':CIV,'compute':EN,'industry':IND,'energy':'#EFE1AB','agriculture':AG,'open_space':SAND}
 for p,g in geo['land_use']:fill(ax,g,'#EBE8E0' if gray else colors[p['use']],edge='white',lw=.55,z=2)
 fill(ax,flood.intersection(master),'#DCE5E5',edge='#A6B6BB',lw=.2,hatch='///',alpha=.55,z=3)
 for p,g in channels:
  q=g.intersection(master.buffer(500));outline(ax,q,BLUE,.8,z=4)
def buildings(ax):
 for p,g in geo['buildings']:
  fill(ax,g,'#CBD0CA' if p.get('form')=='canopy' else '#3E494B',z=10)
def networks(ax,gray=False):
 for p,g in geo['movement']:
  if p.get('network')=='machine':outline(ax,g,BLUE if not gray else '#8C9697',1.8,z=11)
  elif p.get('network')=='people':outline(ax,g,'#A4AFAA',.7,z=9)
 for p,g in geo['movement']:
  if p.get('kind')=='interface':ax.scatter([g.x/1000],[g.y/1000],s=20,fc=PAPER,ec=ORANGE,lw=.8,zorder=15)
arrival=(574750,6554200);axis=LineString([(573400,6553600),(574650,6553600)])
proposed=dict(type='FeatureCollection',features=[dict(type='Feature',geometry=mapping(transform(inv,axis)),properties=dict(status='proposal_for_review',name='Living spine / proposed new pedestrian link',network='people',shaded=False)),dict(type='Feature',geometry=mapping(transform(inv,Point(*arrival))),properties=dict(status='proposal_for_review',name='Arrival at an existing registered interface',kind='arrival_candidate'))])
(D/'proposed_connections.geojson').write_text(json.dumps(proposed,ensure_ascii=False,indent=2))
figs=[]
# 00: Source and proposed layers distinguished without rendering.
f=new('00 / GEOMETRY','先分清：研究范围、真实建设、拟议连接','底图采用同一冻结几何；本轮没有移动建筑。新增步行轴与到达点只保存在独立提案图层中。')
a=f.add_axes([.045,.13,.66,.69]);land(a,True);buildings(a);networks(a,True);outline(a,master,INK,2)
outline(a,axis,ORANGE,2.6,ls='--');a.scatter([arrival[0]/1000],[arrival[1]/1000],s=95,fc=PAPER,ec=ORANGE,lw=2,zorder=22)
setup(a,(571250,6551750,575750,6555250),1000)
text(a,571650,6554700,'12.008 km²\n首期研究范围',15,boxcolor=PAPER)
text(a,573820,6554010,'实际住宅建筑',13,boxcolor=PAPER)
label(a,arrival,'候选到达点\n位于现有平交点', (574850,6554700),ORANGE)
card(f,.765,'01','实线 = 已有方案几何','建筑、用地和人机路径均可追溯。\n七处平交点用空心圆标出。')
card(f,.57,'02','虚线 = 本轮新建议','新增东西向生活主轴约1.25 km。\n尚未写入正式 movement.geojson。')
card(f,.375,'03','蓝灰纹理 = 洪泛筛选','它是地形派生的敏感范围。\n不是绿化面积，也不是安全承诺。')
figs.append(('00-geometry',f))
# 01: Regional / long-term level.
f=new('01 / CITY','全城：从西南首期起步，后续增长有条件','1,656 km²全场地是统筹范围；二、三期是预留。图上不把远期预留画成已经建好的城区或道路。')
a=f.add_axes([.045,.12,.655,.70]);fill(a,scope,'#ECEBE4');outline(a,scope,INK,1.2)
for p,g in geo['structure']:
 if p.get('system')=='energy_compute':fill(a,g,EN,alpha=.32,z=2)
 elif p.get('system')=='agri_production':fill(a,g,AG,alpha=.22,z=2)
for p,g in channels:outline(a,g.intersection(scope),BLUE,.45,z=3)
fill(a,pilot,AG,edge='#6E8059',lw=.7,hatch='///',z=5);fill(a,master,ORANGE,edge=INK,lw=.9,z=7)
ph2=[g for p,g in geo['phasing'] if p['phase']==2][0];fill(a,ph2,'#E6DFCE',edge=ORANGE,lw=1.5,z=6)
third=unary_union([g for p,g in geo['structure'] if p.get('name')=='Third settlement reservation']);port=unary_union([g for p,g in geo['structure'] if p.get('system') in ['port','industry']]);fill(a,third,'#E6DFCE',edge=ORANGE,lw=1.5,z=6);fill(a,port,IND,edge=INK,lw=.8,z=6)
label(a,(573500,6553500),'01 首期聚落\n本轮设计主体',(558000,6547500),INK,14)
label(a,(575250,6581250),'02 二期聚落预留',(558000,6585000),INK,13)
label(a,(611200,6574200),'03 三期聚落预留',(609000,6586000),INK,13)
label(a,(621600,6560200),'东部门户预留\n与首期生活区分开',(625000,6567000),INK,12)
text(a,602000,6555500,'Pie de Palo\n山地与保留地',13,c=MUT,ha='center',boxcolor=PAPER)
text(a,587000,6591000,'能源、农业生产预留\n不等于全部开发或灌溉',12,c=MUT,ha='center',boxcolor=PAPER)
label(a,(570500,6548000),'既有试点 / 固定不改',(558000,6556000),MUT,12)
setup(a,(556000,6541500,636500,6609500),20000,bar_at=(593000,6544000))
card(f,.77,'01','先建一个完整的小城','靠近现有试点，但不改动试点。\n住房、学校、诊所、生产同时成立。')
card(f,.575,'02','再判断能否增设聚落','水有可审计余量，首期入住稳定，\n下一阶段服务与接入资金落实。')
card(f,.38,'03','门户是后期条件项目','靠山体东侧预留；先解决接入、\n出口需求、水与审批等条件。')
f.text(.735,.145,'注意：图中的连线是标签引线。\n未新增跨区道路或获批外部通道。',fontsize=11,color=MUT,linespacing=1.6)
figs.append(('01-city-structure',f))
# 02: Master level.
f=new('02 / FIRST SETTLEMENT','首期：一处到达、两个系统、四组住宅','人从东北侧进入生活网络；机器沿东侧与南侧服务。河道保留地在西，生产在南，光伏在东。')
a=f.add_axes([.045,.12,.66,.70]);land(a);buildings(a);networks(a);outline(a,master,INK,1.8)
outline(a,axis,ORANGE,3.4,ls='--');existing_arrival=LineString([arrival,(574650,6554200),(574650,6553600)])
outline(a,existing_arrival,ORANGE,3.0)
a.scatter([arrival[0]/1000],[arrival[1]/1000],s=150,fc=PAPER,ec=ORANGE,lw=2,zorder=23)
label(a,arrival,'01 到达\n候选落客 / 现有平交点',(574800,6554630),ORANGE,13)
text(a,571850,6553450,'河道与干旱保留地\n不画成整片公园',15,boxcolor=PAPER)
text(a,573890,6553900,'四组住宅\n共960套',14,ha='center',boxcolor=RES)
text(a,573900,6553580,'拟议生活主轴 → 公共中心',12,c=INK,ha='center',va='top',boxcolor=PAPER)
text(a,574970,6553700,'光伏\n储能',14,ha='center',boxcolor='#EFE1AB')
text(a,573950,6552870,'维修 / 加工服务带',13,ha='center',boxcolor=IND)
text(a,573950,6552370,'算力 + 余热接收工坊',14,ha='center',boxcolor=EN)
text(a,573950,6554570,'苗圃与农业试验',13,ha='center',boxcolor=AG)
label(a,(574410,6553650),'02 公共中心',(574850,6553000),INK,13)
text(a,572000,6554750,'C03 河道节点\n季节性使用',12,boxcolor=PAPER)
setup(a,(571250,6551750,575750,6555250),1000)
card(f,.775,'人','到达 → 住宅 → 公共中心','橙实线利用现有步行路径。\n橙虚线补充明确的东西生活主轴。')
card(f,.575,'机','外侧服务 → 生产设施','蓝灰线是现有机器 / 服务网络。\n货运不穿过公共中心与住宅内部。')
card(f,.375,'地','研究范围 ≠ 生活城区','住宅 + 公共服务用地约1.477 km²。\n12.008 km²还包括生产和大块留白。')
f.text(.735,.145,'用地面积：从既有几何重算。\n新增主轴、落客与标识待审阅。',fontsize=11,color=MUT,linespacing=1.6)
figs.append(('02-master-layout',f))
# 03: Daily-life level, actual footprints and four counted groups.
f=new('03 / DAILY LIFE','生活区：四个组团围绕一条清楚的日常联系','按现有建筑分组，每组240套 / 600人情景；只是层级读图，不把组团色块当成新的产权边界。')
a=f.add_axes([.045,.12,.66,.70]);land(a)
groups=[('A',(573380,6553150,573800,6553600)),('B',(573800,6553150,574250,6553600)),('C',(573380,6553600,573800,6554150)),('D',(573800,6553600,574250,6554150))]
counts={}
for name,b in groups:
 g=box(*b);outline(a,g,'#BEAE91',1.1,ls=':');bs=[(p,z) for p,z in geo['buildings'] if p.get('use')=='residential' and g.covers(z.centroid)];counts[name]=sum(p.get('dwellings',0) for p,z in bs)
 assert counts[name]==240,(name,counts[name])
 xx=(b[0]+b[2])/2;yy=(b[1]+b[3])/2;text(a,xx,yy,f'{name} 组团\n240套',14,ha='center',boxcolor=PAPER)
buildings(a);networks(a);outline(a,axis,ORANGE,3.8,ls='--');outline(a,existing_arrival,ORANGE,2.6)
a.scatter([arrival[0]/1000],[arrival[1]/1000],s=140,fc=PAPER,ec=ORANGE,lw=2,zorder=24)
text(a,574470,6553660,'A03\n公共中心',14,ha='center',boxcolor=PAPER)
label(a,(574390,6553260),'学校 / 诊所',(574330,6553080),INK,12)
label(a,(574420,6553880),'培训 / 夜间服务',(574270,6554410),INK,12)
text(a,574745,6554070,'到达点',12,c=ORANGE,ha='right',boxcolor=PAPER)
setup(a,(573300,6553000,574900,6554500),250)
card(f,.775,'住','住宅不再只是一排排体块','A / B / C / D各24栋、240套。\n四组共享学校、诊所与公共中心。')
card(f,.575,'轴','新主轴放在两排建筑之间','连接南北两组住宅与东侧公共中心。\n约1.25 km，避开现有封闭建筑。')
card(f,.375,'心','公共中心是日常目的地','市场、厨房、图书馆与遮阴广场\n形成一个中心，学校与诊所在南侧。')
f.text(.735,.145,'600人 / 组团按2.5人 / 套情景计算。\n不是人口调查，也未验证设施容量。',fontsize=11,color=MUT,linespacing=1.6)
figs.append(('03-living-core',f))
# QA: no accidental changes to source, proposed centreline clear of permanent buildings.
permanent=unary_union([g for p,g in geo['buildings'] if p.get('form')!='canopy'])
assert not axis.intersects(permanent),'proposed spine crosses buildings'
assert master.covers(axis),'proposed spine leaves master'
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==source_hash[p.name] for p in G.glob('*.geojson'))
assert sum(counts.values())==960
qa=dict(status='planning_review_only',public_submission='withheld_by_user',source_geometry_sha256=source_hash,combined_source_sha256=finger,checks={'source_geometry_unchanged':'PASS','four_groups_240_dwellings_each':'PASS','total_dwellings_960':'PASS','proposed_axis_inside_master':'PASS','proposed_axis_no_permanent_building_intersection':'PASS'},limitations=['New connection is a separate review proposal, not adopted geometry.','Arrival uses an existing registered interface; stopping, waiting and safety details remain to design.','Facility capacity, thermal comfort, flood protection and access engineering are not validated.'],user_feedback='Overall layout unclear; user declined public submission and requested revision.')
(D/'review.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
with PdfPages(D/'AGUA-FINITA-layout-v2.pdf') as pdf:
 for name,f in figs:
  f.savefig(D/f'{name}.png',dpi=160,facecolor=PAPER);f.savefig(D/f'{name}.svg',facecolor=PAPER);pdf.savefig(f,facecolor=PAPER);plt.close(f)
print('Review PDF: 4 pages; source geometry unchanged; 4 x 240 dwellings; candidate axis clear of buildings.')
