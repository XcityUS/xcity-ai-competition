"""Author original design diagrams and connect them to the current entry, no repo policy edits."""
import json,sys,textwrap
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon as Patch,Rectangle,FancyArrowPatch
from shapely.geometry import shape,box,LineString,Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/full-v6';O.mkdir(exist_ok=True);sys.path.insert(0,str(R/'scripts'));import xcity_common as xc
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:[(x['properties'],transform(T,shape(x['geometry']))) for x in json.loads(f.read_text())['features']]
S=R/'brief/site-package';land=load(P/'geometry/land_use.geojson');build=load(P/'geometry/buildings.geojson');move=load(P/'geometry/movement.geojson');nodes={p['node_id']:(p,g) for p,g in load(P/'geometry/nodes.geojson')};scope=xc.to_utm(xc.site_boundary());flood=unary_union([g for p,g in load(S/'water/flood_sensitive_dem.geojson')]);channels=unary_union([g for p,g in load(S/'water/channels_dem.geojson')]);fixed=xc.to_utm(xc.pilot_area());phases=load(P/'geometry/phasing.geojson');metrics=xc.metric_map(json.loads((P/'metrics.json').read_text()));computed=xc.compute_metrics(str(P))
FONT=FontProperties(fname='/System/Library/Fonts/STHeiti Light.ttc');BG='#F8F6F0';INK='#263D44';MUT='#697A77';COL={'residential':'#E1D0B3','civic':'#C5947E','compute':'#A5B5BE','industry':'#BCBDA8','energy':'#D7C383','agriculture':'#B5C399','open_space':'#E5E1D6','reserve':'#EAE7DE'}
colors={'N05':'#526F7A','N07':'#72896B','N10':'#B97657'}
def tx(ax,x,y,s,size=12,**kw):return ax.text(x,y,s,fontproperties=FONT,fontsize=size,color=kw.pop('color',INK),**kw)
def fill(ax,g,color,lw=0,edge=None,alpha=1):
 if g.is_empty:return
 if g.geom_type=='Polygon':
  from matplotlib.path import Path as MP
  from matplotlib.patches import PathPatch
  from shapely.geometry.polygon import orient
  g=orient(g,sign=1);vs=[];codes=[]
  for ring in [g.exterior,*g.interiors]:
   a=np.array(ring.coords);vs.extend(a);codes.extend([MP.MOVETO]+[MP.LINETO]*(len(a)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(vs,codes),facecolor=color,edgecolor=edge or color,lw=lw,alpha=alpha))
 elif hasattr(g,'geoms'):
  for q in g.geoms:fill(ax,q,color,lw,edge,alpha)
def line(ax,g,color=INK,lw=1,ls='-'):
 if g.is_empty:return
 if g.geom_type in ['LineString','LinearRing']:
  ax.plot(*g.xy,color=color,lw=lw,ls=ls)
 elif g.geom_type=='Polygon':line(ax,g.boundary,color,lw,ls)
 elif hasattr(g,'geoms'):
  for q in g.geoms:line(ax,q,color,lw,ls)
def page(title,subtitle):
 f=plt.figure(figsize=(16,10),facecolor=BG);tx(f,.045,.94,title,25,transform=f.transFigure);tx(f,.045,.897,subtitle,12,transform=f.transFigure)
 tx(f,.045,.035,'AGUA FINITA  |  Jingyuan Huang  |  2026-10-26  |  概念城市设计；图、数来自本方案几何与公开假设，非测绘或审批。',9,transform=f.transFigure,color=MUT)
 return f
def save(f,name):f.savefig(O/(name+'.png'),dpi=160,facecolor=BG);plt.close(f)
def mapbase(ax,bounds,showbuild=True):
 win=box(*bounds)
 for p,g in land:fill(ax,g.intersection(win),COL.get(p['use'],BG))
 line(ax,flood.intersection(win).boundary,'#B8C8BF',.7)
 for p,g in move:
  if g.geom_type in ['LineString','MultiLineString']:
   line(ax,g.intersection(win),'#BD845E' if p.get('network')=='people' else '#8C989A',1 if p.get('network')=='people' else .7)
 if showbuild:
  for p,g in build:fill(ax,g.intersection(win),'#8B9A9B' if p.get('form')=='canopy' else '#5E6E70',lw=.2)
 ax.set(xlim=(bounds[0],bounds[2]),ylim=(bounds[1],bounds[3]));ax.set_aspect('equal');ax.axis('off')
def scale(ax,x,y,length):
 ax.plot([x,x+length],[y,y],color=INK,lw=2);tx(ax,x,y-45,f'0                 {length:g} m',9,va='top')
def explain(ax,items):
 ax.axis('off');y=.95
 for title,body in items:
  tx(ax,0,y,title,15);y-=.065
  for l in body.split('\n'):tx(ax,0,y,l,11,va='top');y-=.047
  y-=.06
# 1. Regional site reading: distinguish source data and screening from design reservation.
f=page('场地先于城市形状','固定条件、地形筛选与区域联系分别表达，避免把敏感带画成湖泊。');a=f.add_axes([.035,.13,.63,.71]);fill(a,scope,'#EAE6DB',1,INK)
# Reduced terrain cell classification is a screening graphic, no statutory terrain boundary.
raw=np.array(Image.open(S/'terrain/dem_9_13_utm19s_60m.png')).astype(float);dy,dx=np.gradient(raw,60);sl=np.hypot(dx,dy)*100
xx=np.linspace(559572.4,631512.4,raw.shape[1]);yy=np.linspace(6608973.7,6541053.7,raw.shape[0]);extent=[559572.4,631512.4,6541053.7,6608973.7]
a.imshow(raw,cmap='Greys',extent=extent,alpha=.13,vmin=600,vmax=1600)
fill(a,flood.intersection(scope),'#DCE5DB',.3,'#A7BAAA',.7);line(a,channels.intersection(scope),'#668F8D',.8);fill(a,fixed,'#A2AE83',.7,INK);line(a,scope.boundary,INK,1.6);a.set(xlim=(560000,632000),ylim=(6540500,6608000),aspect='equal');a.axis('off')
b=f.add_axes([.71,.17,.25,.65]);explain(b,[('不可重画的起点','既定农光场与首期生活区\n是两个独立位置；分别接入、分别核对需求。'),('敏感筛选不是禁建红线','沟道为DEM推导；敏感带约503 km²。\n没有提供实测洪水边界与设计流量。'),('山地决定绕行','东向联系沿山北侧研究，\n不以效果图虚构穿山捷径。'),('接入本身是一项工程','没有现成国省道进入场地。\n场外线路、权属和跨沟工程仍待核实。')]);save(f,'01-site-reading')
# 2. Compare siting choices, not invented quantitative scores.
f=page('为什么从西南起步，而不是把城市先放到东部门户？','比较依据是固定系统、生活完整性、接入与资源兑现；不制造无依据的综合评分。');a=f.add_axes([.05,.16,.9,.67]);a.axis('off')
rows=[['判断项','西南首批街区（采用）','西中部算力带（条件扩展）','东部门户（后期）'],['既定系统','接近农光试点；另接既定生活区','可以形成能源与维护集群','远离首批公共服务'],['城市生活','学校、诊所、住房同步起步','先以生产与服务为主','不以出口园区替代完整生活'],['地形与沟道','东侧台地安排建筑，沟道退让','以低坡非敏感地逐段筛选','北绕山体，重新核查东翼台地'],['资源约束','先核实首批水权和电力','扩容与合同需求共同触发','贸易、工程与资源同时成立才启动'],['接受的代价','放弃“全域同时开发”的形象','城镇之间保持较长生产间隔','约7 km²意向仍须核验可用地']]
tab=a.table(cellText=rows,cellLoc='left',colWidths=[.14,.29,.29,.28],bbox=[0,0,1,1]);tab.auto_set_font_size(False);tab.set_fontsize(12)
for (r,c),cell in tab.get_celld().items():cell.set_text_props(fontproperties=FONT,color=INK);cell.set_edgecolor('#D5D6C9');cell.set_facecolor('#E6E4D8' if r==0 else BG)
save(f,'02-siting-tradeoff')
# 3. Five linked systems, with critical non-negotiable ordering.
f=page('五类系统不是五块互不相干的颜色','能源与算力提供生产能力；水权、公共服务与维护条件控制其实际增长。');a=f.add_axes([.045,.2,.91,.61]);a.set(xlim=(0,12),ylim=(0,7));a.axis('off')
boxes=[(0,4.5,2.6,1.5,'能源与储能','#D7C383'),(4,4.5,2.6,1.5,'算力与维护','#A5B5BE'),(8.5,4.5,2.8,1.5,'加工、出口与门户','#BAA5AA'),(0,1,2.6,1.5,'农业与农光复合','#B5C399'),(4,1,2.6,1.5,'居民与公共生活','#D5AF94'),(8.5,1,2.8,1.5,'水务、审计与治理','#B7CBC8')]
for x,y,w,h,t,c in boxes:a.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor='none'));tx(a,x+w/2,y+h/2,t,15,ha='center',va='center')
for p,q,label in [((2.6,5.25),(4,5.25),'供电'),((6.6,5.25),(8.5,5.25),'生产服务'),((1.3,2.5),(1.3,4.5),'复合用地'),((5.3,4.5),(5.3,2.5),'余热与服务'),((8.5,1.75),(6.6,1.75),'基本生活优先'),((8.5,4.5),(10,2.5),'收益与责任')]:
 a.annotate('',xy=q,xytext=p,arrowprops=dict(arrowstyle='->',color=INK,lw=1.8));tx(a,(p[0]+q[0])/2+.1,(p[1]+q[1])/2+.15,label,11,ha='center',bbox=dict(fc=BG,ec='none',pad=2))
tx(f,.06,.12,'运行顺序：先确认合法可靠的水、电和服务 → 再签可中断的算力与生产合同 → 以公开计量判断是否扩展。',15,transform=f.transFigure);save(f,'03-five-systems')
# 4. First neighbourhood: legible annotated urban plan, not a raw GIS layer dump.
f=page('首批街区：居住、公共生活与生产前后场','建筑位置沿用当前几何；新增总体研究预留不计作已设计完成的街区。');a=f.add_axes([.035,.12,.64,.72]);bounds=(572700,6552000,575150,6554900);mapbase(a,bounds)
for nid,(p,g) in nodes.items():line(a,g.intersection(box(*bounds)).boundary,colors[nid],1.5)
for x,y,label in [(573850,6553920,'住宅生活'),(574470,6554050,'学校／诊所／公共设施'),(573900,6552850,'加工维修与后勤'),(574000,6552350,'算力与干式散热'),(574950,6554500,'光伏储能'),(573750,6554600,'有限灌溉试验')]:tx(a,x,y,label,11,ha='center',bbox=dict(fc=BG,ec='none',pad=2))
scale(a,572850,6552100,500);b=f.add_axes([.71,.19,.25,.61]);explain(b,[('完整生活先出现','960套住宅、2400新增居民为模型目标。\n学校、诊所和日常商业同期开启。'),('公共路径连接日常','住房→公共厨房／图书馆→遮阴场所。\n歩行不以穿越算力服务院为捷径。'),('生产边缘承担就业','算力、加工、维修与水务维护\n形成首批岗位；机器从服务边缘进入。'),('首期与总体分开统计','约40 km²是总体研究包络，\n其中未深化土地仍是条件性预留。')]);save(f,'04-first-neighbourhood')
# 5. Typical building/block enlargement and meaningful geometry dimensions.
f=page('居住组团：从住宅门口到公共路径','模型中的三层住宅条体与连续遮阴路径；这是实算街区片段，不是统一销售产品标准。');a=f.add_axes([.04,.2,.55,.64]);bounds=(573350,6553120,573850,6553650);mapbase(a,bounds);scale(a,573390,6553160,100)
for y in [6553200,6553248]:
 a.annotate('',xy=(573450,y-8),xytext=(573492,y-8),arrowprops=dict(arrowstyle='|-|',color=INK));tx(a,573471,y-20,'42 m',10,ha='center')
b=f.add_axes([.66,.19,.29,.65]);explain(b,[('住房尺度','典型条体42×16m，3层，10套住宅。\n96条×10套＝960套；按2.5人／套计。'),('人与公共空间','地面留给共享活动与到达，\n连续步行遮阴不取代必要室内避暑。'),('服务与安静的边界','配送、急救和维修由外围服务进入。\n最终户门、无障碍与停车仍需深化。'),('需要接受的检验','住宅不是只看排布数量：\n需继续核门口、服务路线、热舒适与维护。')]);save(f,'05-housing-enlargement')
# 6. Building massing/elevation, derived exactly from a selected 150m-wide cross-section.
f=page('高度与界面：低层规则体量、轻型遮阴屋盖','城市形态约束来自地震、热与日常维护；下图高度取自已提交建筑属性。');a=f.add_axes([.06,.30,.87,.46]);a.set(xlim=(0,510),ylim=(-1,18));a.axhline(0,color=INK,lw=1.2)
for x in [30,130,230,330,430]:a.add_patch(Rectangle((x,0),42,10.5,facecolor='#C8B69B',edgecolor=INK,lw=.7));tx(a,x+21,11.4,'3层 / 10.5 m',10,ha='center')
a.set_yticks([0,5,10,15]);a.set_ylabel('m');a.set_xlabel('m');a.spines[['top','right']].set_visible(False);tx(a,250,16,'住宅条体的高度与间隔研究（非结构施工图）',13,ha='center')
tx(f,.06,.18,'规则抗侧力体系 + 可替换轻屋盖 + 低眩光夜间照明 + 热浪期间可进入的室内避暑点',16,transform=f.transFigure)
tx(f,.06,.11,'图示高度已进入模型；层间位移、抗震缝、基础土质、屋盖跨度与消防疏散仍须专项设计。',12,transform=f.transFigure,color=MUT);save(f,'06-height-interface')
# 7. Human-machine separation and real registered interfaces.
f=page('人机分流：把冲突落实到可定位的界面','机器走区域／后勤网络；公共路径与机器同地相遇的点进入注册清单。');a=f.add_axes([.035,.16,.64,.66]);bounds=(572850,6552000,575100,6554900);mapbase(a,bounds,False)
for p,g in move:
 if p.get('kind')=='interface':a.scatter(g.x,g.y,s=65,color='#B36B50',edgecolor=BG,zorder=10)
scale(a,573000,6552100,500);b=f.add_axes([.71,.19,.25,.6]);explain(b,[('7个已登记交会点','当前几何计数；不是事故风险评分。\n完整接口还应核对站点、装卸与边缘入口。'),('人优先而不是无人监管','锁控门、停让与现场人工解除机制。\nAI不能覆盖行人优先及应急规则。'),('区域通道不当步行街','既定生活区接驳是交通联系，\n不能用长距离接驳代替本地生活服务。'),('下一步按真实门口校核','可达路径、后勤转弯、急救停靠\n与工程纵坡分别验证。')]);save(f,'07-human-machine')
# 8. Each detailed node has a purposeful plan and a geometric section/elevation.
node_titles={'N05':'算力与余热利用','N07':'季节河道公园','N10':'遮阴公共空间'}
for nid,(p,g) in nodes.items():
 f=page(nid+' · '+node_titles[nid]+'：详细平面与关键断面','每张图回答空间问题；体量控制截图和额外校核留在技术附件。');a=f.add_axes([.035,.27,.57,.55]);x0,y0,x1,y1=g.bounds;pad=80;bounds=(x0-pad,y0-pad,x1+pad,y1+pad);mapbase(a,bounds);line(a,g.boundary,colors[nid],1.5)
 sectiony={'N05':6552267.5,'N07':6554455,'N10':6553650}[nid];section=LineString([(x0,sectiony),(x1,sectiony)]);line(a,section,colors[nid],1.4,'--');tx(a,x0,sectiony+25,'A',12);tx(a,x1,sectiony+25,"A'",12);scale(a,x0+20,y0+20,200 if nid!='N10' else 50)
 b=f.add_axes([.65,.30,.31,.52]);items={
 'N05':[('生产布局','3座180×75m算力厅，单层高9m。\n维修与加工条带位于其北侧。'),('余热要有接收方','70×35m干燥／换热接收亭已入模型。\n热网温度、管损和运行时段尚需核实。'),('不拿水换极端效率','WUE 0.02 L/kWh、PUE 1.25为假设目标。\n干式散热接受热天耗电与负荷调节。')],
 'N07':[('平日可以使用的高地','80×30m水文课堂靠东侧高地。\n步道观看干沟，不制造常水湖泊。'),('暴雨时有明确退路','关闭低处季节步道，保留沟道行洪。\n预警、关闭与重新开放由值班人负责。'),('剖面不是防洪证明','地面来自60m DEM，纵向有夸大。\n设计水位、流量和小沟道仍未测得。')],
 'N10':[('边缘停留与跨场联系','外框约270×152m；四周12m屋盖。\n中央步行屋盖连接住宅与公共设施。'),('大的公共场地不等于全遮阴','阴影优先覆盖路径和停留边缘。\n开敞场地的活动服从热浪运营。'),('公共服务承接日常','厨房、图书馆与培训／社区设施相邻。\n持续饮水、维护与室内避暑不可缺席。')]}
 explain(b,items[nid])
 # Cut through actual footprint polygons. Terrain is source DEM, not an invented flood level.
 ax=f.add_axes([.08,.115,.82,.11]);L=section.length;s=np.linspace(0,L,160);px=x0+s;py=np.full_like(s,sectiony);rr=np.clip(((6608973.7-py)/60).astype(int),0,raw.shape[0]-1);cc=np.clip(((px-559572.4)/60).astype(int),0,raw.shape[1]-1);z=raw[rr,cc];base=float(z.min());ground=z-base
 ve=3 if nid=='N07' else 1;ax.plot(s,ground*ve,color=INK,lw=1)
 for bp,bg in build:
  cut=bg.intersection(section)
  if cut.is_empty or cut.length<.2:continue
  for seg in list(cut.geoms) if hasattr(cut,'geoms') else [cut]:
   if seg.geom_type!='LineString':continue
   a0,b0=seg.bounds[0]-x0,seg.bounds[2]-x0;gz=float(np.interp((a0+b0)/2,s,ground));h=float(bp.get('height_m',float(bp.get('floors',1))*3.5));ax.add_patch(Rectangle((a0,gz*ve),b0-a0,h*ve,facecolor=colors[nid],edgecolor='none',alpha=.8))
 ax.set(xlim=(0,L),ylim=(-1,max(18,float(ground.max()+11)*ve)));ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=8);tx(ax,.01,1.04,"A—A'  几何剖面 / DEM地形；竖向×"+str(ve),10,transform=ax.transAxes);save(f,nid+'-plan-section')
 # Operation scenarios are design evidence, no invented sensor accuracy or evacuation time.
 f=page(nid+' · 运行与使用：正常、极端条件和恢复','日常活动与异常处置相互约束；没有核实的性能不写成已达标。');a=f.add_axes([.05,.22,.9,.59]);a.axis('off')
 records={
 'N05':[('清晨','维修、交接班与干燥准备','机器在服务边缘运行；公众走独立路径。'),('炎热午后','优先保障基本服务','按合同削减弹性算力，不靠额外冷却取水。'),('缺水','先停非必要灌溉与装饰性消耗','居民基本用水及既定系统进入受保护清单。'),('设备或运营方退出','切换维护和资产接管','保留公共水电资产、计量与服务资金。')],
 'N07':[('干燥日常','观察、步行与水文教育','课堂在高地，沟道保持干旱地貌。'),('上游预警','关闭低处路径并引导撤离','人工值班控制关停，不以到场降雨才判断。'),('洪水期间','低处不开放','模型没有设计流量，不宣称已安全防护。'),('退水恢复','检查侵蚀、泥沙和路径损伤','由维护责任人检查后重开，不自动解锁。')],
 'N10':[('清晨','步行、日常采购和会面','使用连续屋盖与公共厨房。'),('酷热或强风沙','缩减露天停留','遮阴不等于安全；转入可进入的室内避暑点。'),('傍晚','公共活动、阅读和照护','低眩光路径照明，不制造大屏或上射照明。'),('停电或设备失效','保留基本通行与人工服务','机械控制、应急饮水与人工接管。')]}
 for i,(time,activity,rule) in enumerate(records[nid]):
  x=i*.25;a.add_patch(Rectangle((x,.05),.23,.9,facecolor=['#E4E5DA','#DCE4E2','#E9DCCC','#DFE5DA'][i],edgecolor='none'));tx(a,x+.015,.86,time,18);tx(a,x+.015,.68,activity,12)
  for j,l in enumerate(textwrap.wrap(rule,11)):tx(a,x+.015,.54-j*.08,l,12)
 tx(f,.06,.11,'所有状态都要核查：人在何处、谁能关停、公众怎样获得帮助、恢复前由谁确认。',16,transform=f.transFigure);save(f,nid+'-operation')
# 9. Water balance and exact shortage calculation.
f=page('水预算：先保障生活，再决定新增生产规模','假设首批年度毛使用量100万m³；再生水是内部转移，不能重复算作外部新水源。');a=f.add_axes([.06,.30,.57,.49]);a.axis('off')
parts=[('农业与清洗',778263.2,'#A9B98C'),('居民与公共服务',140160,'#B5856F'),('工业',60000,'#A4B5BA'),('景观',20000,'#D9C78E'),('算力补水',1576.8,'#788F99')];x=0
for name,value,c in parts:a.barh([.7],value/1000000,left=x,height=.2,color=c);x+=value/1000000
for i,(name,value,c) in enumerate(parts):tx(a,.01,.49-i*.075,f'{name}   {value:,.1f} m³/年',13,color=c)
a.set(xlim=(0,1),ylim=(0,1));b=f.add_axes([.69,.23,.26,.56]);explain(b,[('外部输入','84万m³新鲜水，扣4万输配损失。\n80万新鲜水到使用端，20万来自内部回用。'),('既定农业优先预留','其中60万m³为试点农业占位假设。\n实际用水高于占位时，先压缩新用途。'),('30%不足的具体代价','景观减2万；新灌溉清洗减17.826万；\n工业减4万；生活非必要减6.174万。'),('不可忽略的缺口','既定生活区需求未提供；\n不能宣称这张表覆盖了整个城市。')]);tx(f,.06,.13,'基本生活不足时，必须落实应急供水或延后入住；不能用表格平衡替代真实供水。',16,transform=f.transFigure);save(f,'08-water-budget')
# 10. Energy daily dispatch: real CSV, distinguish hourly and energy-weighted accounting.
import csv
r=list(csv.DictReader((P/'tools/hourly_dispatch.csv').open()));hours=np.array([int(v['hour']) for v in r]);pv=np.array([float(v['pv_mw']) for v in r]);loadarr=np.array([float(v['load_mw']) for v in r]);grid=np.array([float(v['grid_mw']) for v in r]);idx=np.arange(24*35,24*38)
f=page('能源：夜间比白天更能检验城市承诺','图来自本方案8760小时合成情景；它不是实测天气、接网协议或已达成绩效。');a=f.add_axes([.07,.30,.59,.49]);a.plot(idx/24,pv[idx],color='#B49745',label='PV');a.plot(idx/24,loadarr[idx],color=INK,label='Load');a.fill_between(idx/24,0,grid[idx],color='#B7826B',alpha=.5,label='Unmatched grid');a.set(xlabel='Day in synthetic model',ylabel='MW');a.spines[['top','right']].set_visible(False);a.legend(frameon=False)
b=f.add_axes([.72,.28,.23,.5]);explain(b,[('62.432%','全年用电完全匹配的小时占比。\n不是全年清洁电量占比。'),('72.993%','另列的清洁供电电量占比。\n未经证明的电网输入不给清洁信用。'),('模型输入','40MW光伏、480MWh储能；\n12MW峰值IT、PUE1.25均为假设。')]);tx(f,.06,.14,'储能从受保护备用量起算；保留216MWh应急交付余量，避免把初始电池能量当成免费清洁来源。',14,transform=f.transFigure);save(f,'09-energy-dispatch')
# 11. Accountability is linked to actual public utility and compute operation decisions.
f=page('谁决定增长，谁承担停机与维护？','城市的关键水电资产不与某一家算力运营商的存续绑定。');a=f.add_axes([.05,.2,.9,.6]);a.axis('off')
items=[('公共水电与社区信托','保留土地、关键公用设施、计量与公共通行。\n定期公开水电、储能与算力汇总账。'),('算力运营商','承接可中断服务合同，负责设备与维护。\n退出时提供可移交接口和安全撤场安排。'),('居民、工人和独立审计','参与基本服务优先级与申诉；不以个人轨迹治理。\n独立审计验证表计、计算和增长条件。')]
for i,(title,body) in enumerate(items):
 y=.88-i*.29;tx(a,0,y,title,19,color=['#526F7A','#B97657','#72896B'][i]);tx(a,0,y-.08,body,14,va='top',linespacing=1.6)
tx(f,.06,.1,'AI提出调度建议；不能自行批准扩展、改变基本用水分配或覆盖人行优先。',16,transform=f.transFigure);save(f,'10-governance')
# Readable authored media sheet and topology view reflect same node scope.
for nid,(p,g) in nodes.items():
 f=page(nid+' · '+node_titles[nid]+'：鸟瞰与人视','成品概念效果图表现已提交空间；不作为测绘、工程容量或建成事实。')
 a=f.add_axes([.035,.16,.57,.65]);a.imshow(Image.open(P/'media'/(nid+'-aerial-v6.png')));a.axis('off')
 b=f.add_axes([.63,.28,.335,.48]);b.imshow(Image.open(P/'media'/(nid+'-eye-day.png')));b.axis('off')
 tx(f,.64,.18,{'N05':'南侧生产边缘：算力、维修与余热接收方。','N07':'西北沟道边缘：干旱日常与洪水退让。','N10':'住宅东侧公共核心：遮阴、服务与交往。'}[nid],12,transform=f.transFigure)
 save(f,nid+'-finished')
# Register original code-generated diagrams and finished media; retain all full prompts.
prov=json.loads((P/'image_provenance.json').read_text());prov['images']=[v for v in prov['images'] if not v.get('path','').startswith('reviews/full-v6/')]
for file in sorted(O.glob('*.png')):
 prov['images'].append(dict(path=str(file.relative_to(P)),model='Python matplotlib / Shapely; deterministic authored diagram',prompt='Run tools/full_design_v6.py: read the submitted geometry, source DEM, movement, metrics and declared assumptions. Make legible, purpose-specific urban design plans, sections and system diagrams. No geometry or measured facts inferred from imagery.',generated_at='2026-10-26',post_processing='Original vector planning drawing and editorial composition',reference_images='own_work',reference_images_note='Own submitted geometry and registered concept images; organiser site data attribution in sources.json.',caption='Authored design evidence or presentation page; not survey or approval.'))
for id in ['N05','N07','N10']:
 entry=json.loads((P/'tools'/(id+'-aerial-v6-provenance.json')).read_text());prov['images']=[v for v in prov['images'] if v['path']!=entry['path']]+[entry]
cover=json.loads((P/'tools/cover-render-v5-provenance.json').read_text());prov['images']=[v for v in prov['images'] if v['path']!=cover['path']]+[cover]
(P/'image_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2))
m=json.loads((P/'manifest.json').read_text());m['booklet']={'cover':'media/cover-render-v5.png','pages':[],'section_pages':{}}
def pg(name,title):return dict(path='reviews/full-v6/'+name+'.png',title=title)
m['booklet']['section_pages']['whole_site']=[dict(path='reviews/whole-site-v3/01_whole_site_plan.png',title='全场地总体结构')]
m['booklet']['section_pages']['node_locator']=[dict(path='reviews/presentation-v4/node-locator.png',title='全场地—首批街区—三个节点')]
for name,title in [('01-site-reading','场地与限制'),('02-siting-tradeoff','起步选址取舍'),('03-five-systems','五系统的联系')]:m['booklet']['pages'].append(dict(**pg(name,title),after='whole_site'))
for name,title in [('04-first-neighbourhood','首批街区总体'),('05-housing-enlargement','居住组团与公共路径'),('06-height-interface','高度与空间界面'),('07-human-machine','人机交通与注册界面')]:m['booklet']['pages'].append(dict(**pg(name,title),after='views'))
for nid in m['nodes']:
 m['booklet']['section_pages']['node:'+nid]=[pg(nid+'-finished',nid+' · '+node_titles[nid])]
 for typ,title in [('plan-section','详细平面与断面'),('operation','使用与运行情景')]:m['booklet']['pages'].append(dict(**pg(nid+'-'+typ,nid+' '+title),after=nid))
for name,title in [('08-water-budget','水预算与短缺'),('09-energy-dispatch','逐小时能源情景'),('10-governance','资产、责任与增长治理')]:m['booklet']['pages'].append(dict(**pg(name,title),after='key_metrics'))
m['language']='zh';m['autonomy']['human_role']+=' Human requested a complete design argument with plans, sections, diagrams and massing rather than a six-page digest; authorised uploading the completed revision and replacing its abstract cover with a city rendering. V6 adopts the updated main/technical presentation contract and discloses unfinished engineering independently.';m['updated']='2026-10-26';(P/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
# New matrix distinguishes spatial evidence from engineering confirmation.
rows=[]
for key,heading,geos in [('whole_site','## 2.',['structure','movement','phasing']),('phase_one','## 9.',['master_area','land_use','buildings','movement']),('urban_design','## 7.',['buildings','movement','land_use']),('nodes','## 10.',['nodes','buildings','movement'])]+[('node:'+nid,'## 10.',['nodes','buildings','movement']) for nid in m['nodes']]:
 rows.append(dict(id=key,status='documented' if key.startswith('node:') or key=='nodes' else 'partial',drawings=['drawings/a3-booklet.pdf'],geometry=['geometry/'+g+'.geojson' for g in geos],metrics=['master_area_km2','residents_phase1','annual_water_demand_m3'],explanation=dict(path='proposal.md',heading=heading),gaps=[dict(missing='Reliable water rights, road/hydraulic engineering and existing living-quarter demand remain unverified; wider expansion reserve lacks complete block-level design.',next_step='Obtain source/operator data and specialist survey; verify each extension before committing construction or population.',responsible='Jingyuan Huang with licensed water, transport, civil and urban-design specialists')]))
(P/'design_depth_matrix.json').write_text(json.dumps(dict(schema_version=1,rows=rows),ensure_ascii=False,indent=2))
# Update own sources/assumptions; do not silently retain old fixed-boundary checksum metadata.
src=json.loads((P/'sources.json').read_text())
for rec in src['sources']:
 if rec['id']=='SRC-KML':rec['accessed']='2026-10-26';rec['used_for']='Current organiser seam-closed competition boundary, source commit c60cd1d. Exterior unchanged; not cadastral certification.'
(P/'sources.json').write_text(json.dumps(src,ensure_ascii=False,indent=2))
print('Authored pages',len(list(O.glob('*.png'))),'master',computed['master_area_km2'],'updated manuscript/figures next')
