"""Human-facing presentation + separate technical appendix. No design geometry changes."""
from pathlib import Path
import json,shutil,hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader,PdfWriter
from PIL import Image
P=Path(__file__).resolve().parents[1];R=P.parents[2];D=P/'reviews/presentation-v4';O=R.parent.parent/'outputs/finite-water-city-v4';O.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('CN','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
W,H=landscape(A3);BG='#F8F6F0';INK='#263D44';MUT='#667773';C={'N05':'#526F7A','N07':'#72896B','N10':'#B97657'}
main=D/'AGUA-FINITA-presentation-v4.pdf';app=D/'AGUA-FINITA-technical-appendix-v4.pdf'
def txt(c,x,y,s,size=14,color=INK):
 c.setFont('CN',size);c.setFillColor(HexColor(color));c.drawString(x,y,s)
def wrap(c,x,y,s,width,size=14,leading=23,color=INK):
 line=''
 for char in s:
  if char=='\n' or pdfmetrics.stringWidth(line+char,'CN',size)>width:
   txt(c,x,y,line,size,color);y-=leading;line='' if char=='\n' else char
  else:line+=char
 if line:txt(c,x,y,line,size,color);y-=leading
 return y
def imagefit(c,path,x,y,w,h):
 im=Image.open(path);iw,ih=im.size;f=min(w/iw,h/ih);dw,dh=iw*f,ih*f
 c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
def base(c,num,label):
 c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
 txt(c,42,H-35,'AGUA FINITA  /  有限水城',12);txt(c,W-315,H-35,label,11,MUT)
 c.setStrokeColor(HexColor('#D2D3C8'));c.line(42,H-48,W-42,H-48);c.line(42,38,W-42,38)
 txt(c,42,23,'XCITY  ·  Jingyuan Huang  ·  2026-10-26  ·  V4 展示审阅稿',9,MUT);txt(c,W-70,23,f'{num:02d}',10,MUT)
def minimap(c,x,y,w,h,active):
 loc=json.loads((D/'node-locations.json').read_text());x0,y0,x1,y1=571700,6551900,575300,6555200
 scale=min(w/(x1-x0),h/(y1-y0));offx=x+(w-(x1-x0)*scale)/2;offy=y+(h-(y1-y0)*scale)/2
 c.setFillColor(HexColor('#ECE7DA'));c.rect(offx,offy,(x1-x0)*scale,(y1-y0)*scale,fill=1,stroke=0)
 for n in loc:
  a,b,e,f=n['bounds_utm'];key=n['node_id'];c.setStrokeColor(HexColor(C[key] if key==active else '#B4B7AC'));c.setLineWidth(2 if key==active else .7)
  c.rect(offx+(a-x0)*scale,offy+(b-y0)*scale,(e-a)*scale,(f-b)*scale,fill=0,stroke=1)
  txt(c,offx+(a-x0)*scale+3,offy+(f-y0)*scale+3,key,10,C[key] if key==active else MUT)
 txt(c,x,y+h+13,'在首批街区中的位置',12,MUT)
c=canvas.Canvas(str(main),pagesize=(W,H));c.setTitle('有限水城 | V4 主展示册');c.setAuthor('Jingyuan Huang / Codex')
base(c,1,'01  /  全场地总体结构');imagefit(c,P/'reviews/whole-site-v3/01_whole_site_plan.png',36,72,W-72,H-138)
txt(c,48,55,'阅读重点：西侧城镇与生产主轴、能源算力带、绕山向东的门户联系。色块为条件性预留。',12,MUT);c.showPage()
base(c,2,'02  /  三个节点的位置与联系');imagefit(c,D/'node-locator.png',35,74,W-70,H-136)
txt(c,48,55,'三个节点都位于西南首批街区：共同检验生产如何回馈生活、城市如何避让洪水，以及酷热中的公共生活。',11,MUT);c.showPage()
nodeinfo=[('N05','算力与余热利用','生产设施怎样回馈城市，而不争夺生活用水？','首批街区南侧，算力设施与加工维修带相邻。','干式散热降低冷却用水，接受炎热时段更高的耗电与算力调节。','把余热交给合作干燥车间，并以计量记录验证接收量。','站在余热接收车间一侧，望向后方算力设施。','余热先找到接收方，回收才有意义。'),('N07','季节河道公园','河道大部分时间是干的，城市怎样仍为洪水留出空间？','首批街区西北侧，连接干沟道与东侧高地。','低处保留行洪空间，遇上游预警关闭季节步道。','水文课堂位于高地边缘；步行活动退让，不靠景观水面成立。','从高地公共路径看水文课堂；画面不是蓄水湖泊。','河道可以干，行洪空间不能被填掉。'),('N10','遮阴公共空间','炎热和风沙到来时，人们还愿意在哪里停留？','住宅东侧的公共核心，靠近公共厨房与图书馆。','连续遮阴屋盖围合可停留的公共场所，连接住宅日常路径。','以公共设施、饮水与必要的室内避暑点支撑日常使用。','从公共路径进入遮阴场所，观看停留、会面与日常交往。','让公共生活先成立，再谈城市增长。')]
for num,(nid,name,question,where,design,relation,view,sentence) in enumerate(nodeinfo,3):
 base(c,num,f'{num:02d}  /  {nid}');txt(c,44,H-95,nid+'  '+name,31,C[nid]);txt(c,46,H-124,question,16,MUT)
 imagefit(c,P/'media'/f'{nid}-eye-day.png',44,182,820,515)
 txt(c,46,166,'成品概念效果图  /  '+view,11,MUT)
 x=904;minimap(c,x,529,240,155,nid)
 y=480
 for label,body in [('在哪里',where),('关键空间动作',design),('与城市的联系',relation)]:
  txt(c,x,y,label,15,C[nid]);y=wrap(c,x,y-25,body,240,13,21)-20
 wrap(c,46,105,sentence,1060,26,35)
 txt(c,46,53,'效果图沿用已登记的概念表现；不是现场照片或工程承诺。平面、剖面及体量校核见独立技术附件。',10,MUT);c.showPage()
base(c,6,'06  /  实施顺序与关键指标');txt(c,45,H-100,'先让第一片城市独立运行，再有条件地扩展',29)
cols=[(48,'P1','完整首批街区','#B97657','先落实合法可靠的水、电与道路接入，建设住房、学校、诊所、公共厨房和生产维护。既定农光场、既定生活区保持不变。'),(432,'P2','西侧城镇与生产主轴','#526F7A','供水余量、入住与服务资金满足条件后，逐段开放城镇和生产预留。每段都有本地服务与加工维护，不依赖远期全线建成。'),(816,'P3','东向服务镇与门户','#72896B','道路水文工程、贸易需求和资源承载成立后，启动东部门户。通过山北侧通道联系，避免虚构穿山道路。')]
for x,k,t,col,body in cols:
 c.setFillColor(HexColor(col));c.rect(x,H-176,324,5,fill=1,stroke=0);txt(c,x,H-159,k,22,col);txt(c,x,H-212,t,20,col);wrap(c,x,H-249,body,320,15,26)
c.setStrokeColor(HexColor('#D2D3C8'));c.line(45,365,W-45,365);txt(c,47,333,'以下指标仅针对新增首批街区，不代表全场地最终规模',15,MUT)
for x,value,label in [(48,'2,400','新增居民目标'),(332,'960','新增住宅'),(616,'12 MW','首批算力峰值'),(900,'62.432%','全年完全匹配小时占比')]:
 txt(c,x,265,value,35);txt(c,x,230,label,14,MUT)
wrap(c,48,166,'尚待深化：东部门户严格筛选候选约2.64 km²，低于任务书约7 km²意向；既定生活区需求、全域水权与道路工程仍需核实。',1080,14,23)
wrap(c,48,99,'主册负责讲清设计。土地账、计算、平剖面、体量图、来源和检查记录均在独立技术附件中。自动合规通过不等于工程或设计审批。',1080,12,20,MUT)
c.save()
# Appendix begins with a readable index, then extracts evidence/process pages rather than repeating main presentation.
cover=D/'appendix-cover.pdf';a=canvas.Canvas(str(cover),pagesize=(W,H));base(a,1,'技术附件 / 与主展示分开');txt(a,48,H-125,'有限水城  /  技术与过程附件',34);txt(a,48,H-165,'用于核对、复算和进一步深化；不是主展示阅读顺序。',17,MUT)
y=H-245
for title,desc in [('A  任务与指标','任务覆盖、空间结构、总体边界、土地使用与密度、交通、水文、分期、指标复算。'),('B  三节点技术证据','每个节点的平面、剖面、使用时序与体量校核。原始成品/体量对照留在这里。'),('C  假设、来源与状态','水电、人口、工程假设、资料来源与限制，以及本版须继续核实的事项。')]:
 txt(a,48,y,title,22);y=wrap(a,48,y-38,desc,1040,16,27)-48
wrap(a,48,135,'资料来自本方案V3技术图册的第8-24、26-27页；保持原技术证据页，不冒称此次重新完成设计。主展示为独立6页文件。',1060,13,22,MUT);a.save()
r=PdfReader(P/'drawings/a3-booklet.pdf');assert len(r.pages)==27
w=PdfWriter();w.append(str(cover));w.add_outline_item('任务与空间、指标',1)
for i in list(range(7,24))+[25,26]:w.add_page(r.pages[i])
w.add_metadata({'/Title':'有限水城 | V4 独立技术附件','/Author':'Jingyuan Huang / Codex'})
with app.open('wb') as f:w.write(f)
for f in [main,app]:shutil.copy2(f,O/f.name)
shutil.copy2(D/'node-locator.png',O/'node-locator.png')
for n in ['N05','N07','N10']:shutil.copy2(P/'media'/f'{n}-eye-day.png',O/f'{n}.png')
shutil.copy2(P/'reviews/whole-site-v3/01_whole_site_plan.png',O/'whole-site.png')
# Source adaptation is attributed; Haidian's schema, standards, site, mandatory media and scheduling are not imported.
ref=dict(source='https://github.com/open-city-ai/haidian/tree/main/skills/urban-design-ai-submission',read_on='2026-10-26',adopted=['Human-readable design narrative separate from full evidence layer','Three nested scope levels and clear key-area locations','Each figure has a clear purpose; meaningful finished media rather than raw debug output'],not_imported=['Haidian site constraints and professional standards','Haidian JSON schema or bilingual gate','Community posting, account settings, automations or PR actions'],our_editorial_decision='Six-page main booklet plus independent twenty-page technical appendix; no mandated six-page layout was found in the reference',geometry_changed=False)
(D/'reference-adaptation.json').write_text(json.dumps(ref,ensure_ascii=False,indent=2))
page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>有限水城 V4 主展示</title><style>body{margin:0;background:#f8f6f0;color:#263d44;font:17px/1.7 -apple-system,sans-serif}main{max-width:1400px;padding:32px;margin:auto}h1,h2{font-weight:500}img{max-width:100%;display:block}a{color:#526f7a}.card{margin:45px 0;padding-top:15px;border-top:1px solid #d2d3c8}.body{max-width:850px}.hint{color:#667773;font-size:14px}summary{cursor:pointer}nav{display:flex;gap:18px;flex-wrap:wrap}</style><main><h1>有限水城 · V4 主展示</h1><p class="body">先看全场地，再找到三个节点，最后看它们的成品效果图。体量、平剖面与校核资料已独立收进技术附件。</p><nav><a href="AGUA-FINITA-presentation-v4.pdf">下载6页主展示册</a><a href="AGUA-FINITA-technical-appendix-v4.pdf">下载20页技术附件</a><a href="#location">直接看三个节点在哪里</a></nav><section class="card"><h2>01 全场地总体结构</h2><img src="whole-site.png" alt="全场地的城镇、能源算力生产带及东部门户结构图"></section><section id="location" class="card"><h2>02 三个节点在哪里</h2><img src="node-locator.png" alt="从全场地定位西南首批街区，再放大标出南侧N05、西北侧N07和住宅东侧N10"></section>'''
for n,name,q,where,design,relation,view,sentence in nodeinfo:
 page+=f'<section class="card"><h2>{n} {name}</h2><p class="body">{where}{design}{relation}</p><img src="{n}.png" alt="{name}成品概念效果图：{view}"><p class="hint">概念效果图，沿用已登记的表现图，非现场照片。{view}</p></section>'
page+='<section class="card"><h2>06 实施与指标</h2><p class="body">先落实首批街区的水、电、道路和完整服务，再有条件打开西侧主轴，最后启动东部门户。新增首批街区：2400居民、960住宅、12MW算力峰值；完全匹配小时占比62.432%。这些数字不代表全域最终规模。</p><details><summary>查看技术附件与参考方法</summary><p><a href="AGUA-FINITA-technical-appendix-v4.pdf">技术与过程附件</a></p><p>参考海淀项目提交技能的人工阅读层/机器证据层组织方法，使用XCITY原有场地与指标。六页编排是本轮编辑选择，并非该技能的固定页数要求。</p><a href="https://github.com/open-city-ai/haidian/tree/main/skills/urban-design-ai-submission">参考技能原文</a></details></section></main></html>'
(O/'index.html').write_text(page)
qa=dict(main_pages=len(PdfReader(main).pages),appendix_pages=len(PdfReader(app).pages),main_images=['V3 whole-site diagram','V4 geometry-derived node locator','media/N05-eye-day.png','media/N07-eye-day.png','media/N10-eye-day.png'],low_poly_control_views_in_main=False,geometry_changes=False,reference=ref['source'])
(D/'presentation-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False,indent=2));print(O)
