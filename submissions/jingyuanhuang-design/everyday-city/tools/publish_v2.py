"""Compose English visual-first V2 booklet, A0 and separate technical evidence."""
import json,io,shutil,hashlib,html,math
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib;matplotlib.use('Agg')
from matplotlib.font_manager import findfont,FontProperties
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/redesign-v2';D=O/'diagrams';M=P/'media/v2';OUT=R.parents[1]/'outputs/everyday-city-v2';OUT.mkdir(parents=True,exist_ok=True)
qa=json.loads((O/'design-account.json').read_text());program=qa['programme'];cams=json.loads((O/'camera-registry.json').read_text());BG='#F7F4EC';INK='#263F46';MUT='#6B766F';ACC='#B67351';BLUE='#356C86';GREEN='#91AA79'
for name,w in [('Body','normal'),('Bold','bold')]:pdfmetrics.registerFont(TTFont(name,findfont(FontProperties(family='DejaVu Sans',weight=w))))
W,H=420*mm,297*mm;style=ParagraphStyle('body',fontName='Body',fontSize=10,leading=14,textColor=HexColor(INK))
def text(c,x,y,s,size=10,bold=False,color=INK):c.setFont('Bold' if bold else 'Body',size);c.setFillColor(HexColor(color));c.drawString(x*mm,y*mm,str(s))
def para(c,x,y,w,s,size=10):
 st=ParagraphStyle('p',parent=style,fontSize=size,leading=size*1.42);p=Paragraph(s,st);ww,hh=p.wrap(w*mm,2000);p.drawOn(c,x*mm,y*mm-hh);return hh/mm

def pic(c,p,x,y,w,h,cover=False):
 im=Image.open(p);iw,ih=im.size;scale=max(w*mm/iw,h*mm/ih) if cover else min(w*mm/iw,h*mm/ih);dw,dh=iw*scale,ih*scale;src=str(p)
 if Path(p).parent.name in ['v2','renders']:
  b=io.BytesIO();im.convert('RGB').save(b,format='JPEG',quality=95,subsampling=0);b.seek(0);src=ImageReader(b)
 c.saveState();q=c.beginPath();q.rect(x*mm,y*mm,w*mm,h*mm);c.clipPath(q,stroke=0,fill=0);c.drawImage(src,x*mm+(w*mm-dw)/2,y*mm+(h*mm-dh)/2,dw,dh,mask='auto');c.restoreState()
def background(c,w=W,h=H):c.setFillColor(HexColor(BG));c.rect(0,0,w,h,fill=1,stroke=0)
def head(c,title,sub=''):
 background(c);text(c,17,281,'THE EVERYDAY CITY / CITY DESIGN',9,True,ACC);text(c,17,263,title,22,True)
 if sub:para(c,17,252,386,sub,9)
def footer(c,n):text(c,17,12,'JINGYUAN HUANG / 27 OCT 2026 / V2 / CONCEPT DESIGN',7,color=MUT);text(c,385,12,f'{n:02d}',8)
def table(c,x,y,w,rows,weights=None,size=9):
 sty=ParagraphStyle('cell',parent=style,fontSize=size,leading=size*1.3);data=[[Paragraph(html.escape(str(v)),sty) for v in row] for row in rows];weights=weights or [1]*len(rows[0]);t=Table(data,colWidths=[w*mm*v/sum(weights) for v in weights],repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#E5DCCB')),('GRID',(0,0),(-1,-1),.3,HexColor('#CAC7BB')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));ww,hh=t.wrap(w*mm,2000);t.drawOn(c,x*mm,y*mm-hh)
# Numeric scenario, kept separate from source claims and fixed-pilot demands.
res=qa['residents'];jobs=qa['jobs'];dom=res*85*365/1000;civic=res*15*365/1000;work=jobs*35*300/1000;compute=8*8760*1.3*.1;agri=22968;gross=dom+civic+work+compute+agri;reuse=100000;fresh=(gross-reuse)/.92
resources=dict(domestic_gross_m3y=dom,civic_gross_m3y=civic,work_gross_m3y=work,compute_makeup_m3y=compute,gross_use_m3y=gross,reuse_m3y=reuse,fresh_abstraction_m3y=fresh,distribution_loss_fraction=.08,full_it_mw=8,pue_assumed=1.3,solar_mwp=26.784,solar_yield_kwh_kwp_y=1800,solar_mwh_y=26.784*1800,compute_mwh_y=8*1.3*8760,fixed_pilot_water='Additional and unknown; no supply entitlement confirmed',agriculture_m3y=agri,trial_irrigation='7.656ha new crop bands;22968m3/y assumed irrigation, no lawful supply or commercial yield established')
(O/'resource-scenarios.json').write_text(json.dumps(resources,indent=2))
main=P/'drawings/a3-booklet.pdf';c=canvas.Canvas(str(main),pagesize=(W,H));c.setTitle('THE EVERYDAY CITY | V2 city design');c.setAuthor('Jingyuan Huang');pages=[]
def page(title,section,fn):
 n=len(pages)+1;fn(c);footer(c,n);c.showPage();pages.append(dict(page=n,title=title,section=section))
def cover(c):
 background(c);text(c,17,269,'THE EVERYDAY CITY',30,True);text(c,17,256,'A COMPLETE TOWN / SHARED GROUND / PRODUCTIVE EDGES',11,True,ACC);pic(c,M/'city-centre.png',17,42,386,203,True);text(c,20,47,'TOWN CENTRE + LIVING DISTRICTS / LOCAL AERIAL / FULL BUILD-OUT SCENARIO',7,True);para(c,17,33,385,'A continuous town of homes, schools and daily services. Production supports the city from its own campus. The local cover view is located within the full-site territorial plan.',10)
page('Cover','cover',cover)
def thesis(c):
 head(c,'Make ordinary life the organising structure','The complete settlement is designed before the three detailed places. Buildings, roads, capacities, stages and camera controls share the same coordinates.')
 pic(c,D/'system-layout.png',17,29,165,210)
 for i,(t,b) in enumerate([('01 / A town with identifiable districts','West, East and North living districts form a continuous 2.4 x 2.4 km town. A civic band and dry commons connect them; housing is not scattered around compute halls.'),('02 / Production with a civic boundary','The productive estate sits 1.1 km south of town; its serviced campus is 1.45 km from town. Public arrival and production servicing take different approaches. No residential heat network is assumed.'),('03 / A useful working landscape','A new farm-learning interface is outside both fixed pilots. New trial rows can test the interface without claiming new irrigation rights or modifying the existing fields.')]):
  y=231-i*64;text(c,201,y,t,13,True);para(c,201,y-10,197,b,11)
page('The organising decision','argument',thesis)
def whole(c):
 head(c,'The whole issued site has a named role','Base zoning is mutually exclusive. Gross district area is not serviced construction, installed PV, irrigated agriculture or approved development.')
 pic(c,D/'whole-site.png',17,29,260,213)
 for i,p in enumerate(qa['regions']):
  y=235-i*21;text(c,292,y,p['id']+' / '+p['name'],8,True);text(c,292,y-6,f"{p['area_km2']:,.1f} km2 gross / design or fixed context",7,color=MUT)
 para(c,292,38,111,'Dashed blue routes are preliminary regional corridor studies. Thin green lines are source-derived seasonal channels. Neither implies a surveyed road right or permanent water.',8)
page('Whole-site zoning','whole_site',whole)
def ground(c):
 head(c,'Choose a coherent town, then accept its distances','The earlier compact all-functions rectangle is withdrawn. The new scheme keeps the southwest access basin while giving housing a complete and independently serviced urban footprint.')
 pic(c,D/'system-layout.png',17,27,180,215)
 items=[('The selected urban ground',f"Town: {qa['town_km2']:.2f} km2; median screened slope {qa['town_ground_screen']['median_slope_pct']}%, 95th percentile {qa['town_ground_screen']['p95_slope_pct']}%. Three housing cells touching the preliminary flood screen are held without capacity."),('The cost of an independent campus','A compact co-location could shorten utilities and staff trips. The selected 1.1 km edge separation protects coherent residential streets and permits an operating boundary, but adds bus, utility and maintenance obligations.'),('What could reverse this decision','Geotechnical conditions, a lawful access corridor, measured noise/dust, utility connection costs or actual demand may change the town or campus boundary. The 150 m channel test is a declared screening distance, not a statutory setback.')]
 for i,(t,b) in enumerate(items):y=229-i*66;text(c,215,y,t,13,True);para(c,215,y-10,187,b,10)
page('Ground and alternative','site_reading',ground)
def system(c):
 head(c,'One settlement system, several operating territories','City scale / true relative coordinates / all phases. The study footprint totals 8.635 km2; it is distinct from the full competition territory.')
 pic(c,D/'system-layout.png',17,29,185,210)
 for i,(t,b) in enumerate([('TOWN / residents and public life','Homes, shops, care and schools are organised by living district. The civic band is a shared destination; the north-south dry commons is public ground, not a lake.'),('WORKS / production and utility services','Four covered modular-service groups at2 MW operating IT each are released 2 + 1 + 1. Repair, metered local drying trials and utilities have their own servicing. The adjacent 26.784 MWp PV scenario is conditional on module layout and grid study.'),('FARM / public learning and testing','Two farm-service sheds and a public shade promenade face eight new trial rows. Their small trial capacity is excluded from the main city PV account; crop bands have an explicit assumed water budget; commercial yields remain uncredited.')]):y=230-i*65;text(c,218,y,t,12,True);para(c,218,y-10,184,b,10)
page('Complete system layout','overall_layout',system)
def overall(c):
 head(c,'The town and its productive edges','Complete southwestern settlement / hypothetical full build-out / physical camera control retained. This image does not depict the entire competition territory.')
 pic(c,M/'city-overall.png',17,31,386,207);para(c,17,26,386,'The town, independent productive campus, solar study and farm-learning edge retain their actual relative coordinates. Distant territorial districts remain in the full-site plan rather than being invented into the view.',8)
page('Overall spatial view','overall_layout',overall)
def thematic(title,file,body,section):
 def draw(c):head(c,title);pic(c,D/(file+'.png'),17,29,255,217);para(c,291,231,111,body,11)
 page(title,section,draw)
thematic('Districts, blocks and the civic band','city-composite','<b>Three living districts.</b><br/>The West is the first complete occupation area; the East extends the same service logic; the North completes the town.<br/><br/><b>Two public axes.</b><br/>The east-west civic band holds shared destinations. The north-south dry commons gives a continuous public address.<br/><br/><b>Different housing grain.</b><br/>Three-storey open court bars alternate with two-storey terrace lanes. The all-phase inventory yields 7,872 dwellings, a capacity ceiling rather than a proven market.', 'urban_design')
thematic('A hierarchy of streets and public movement','city-mobility','<b>Blue: streets.</b><br/>The 32 m civic Main Street and 28 m north-south avenue organise 20 m local streets. Widths are design reservations, pending engineering.<br/><br/><b>Rust: bus/walking study.</b><br/>Stops mark a proposed network; frequency, accessibility and funding are not yet secured.<br/><br/><b>Outside the town.</b><br/>A public southwest approach serves the farm and worker bus link. Production freight approaches on the east. Final junctions and emergency routes require transport review.', 'street_mobility')
thematic('Dry commons and a shade network','city-landscape','<b>Landscape has different roles.</b><br/>Dry parks and the commons provide public ground. Source seasonal channels remain landscape/conveyance studies at territorial scale.<br/><br/><b>Green dashed links are proposals.</b><br/>They identify future walking/shade opportunities on real street alignments, not established trees or guaranteed continuous shade.<br/><br/><b>Engineered shade first.</b><br/>Courtyard, civic, worker and learning canopies are modelled explicitly. No irrigated lawn, decorative lake or mature planting capacity is credited.', 'ecology_landscape')
thematic('Schools, care and daily destinations','city-services','<b>Services precede homes.</b><br/>Two southern schools reserve 750 places each. Four northern schools reserve 400 each. The 3,100-place scenario exceeds an assumed 15% of 19,680 residents (2,952); demand, staffing and age mix need verification.<br/><br/><b>Four daily centres.</b><br/>Care and neighbourhood shops supplement the larger markets, library, sports and health uses in the civic band.<br/><br/><b>No blanket five-minute claim.</b><br/>Some trips across the 2.4 km town need the proposed bus and a measured safe-route audit.', 'public_space_services')
def homes(c):
 head(c,'A block is shared ground, not an employer compound','Two original housing types / build-out capacity from modelled buildings / detailed dwelling accessibility and tenure design remain next work.')
 pic(c,D/'A01-plan.png',17,82,207,158);pic(c,D/'A01-section.png',17,29,207,48)
 text(c,244,231,'OPEN COURT BARS',13,True);para(c,244,219,157,'Four separate bars define an open court. The two long bars each carry 30 dwellings; the two short bars each carry 18: 96 homes per court-block at three storeys. Corner gaps preserve public access; a 6 m deep canopy offers a shared address.',11)
 text(c,244,149,'TERRACE LANES',13,True);para(c,244,137,157,'Four two-storey rows each carry 12 dwellings: 48 homes per block. They offer a lower-rise counterpart, not a translated copy of the courtyard. Street frontage, emergency access and maintenance remain shared municipal obligations.',11)
 para(c,244,69,157,'Both counts are declared design capacities, not sale plots, guaranteed household demand or surveyed building permissions. Landscape furniture and people in the finished images are illustrative.',9)
page('Housing grammar','urban_design',homes)
def locator(c):
 head(c,'Three places test three city promises','The nodes are located by the same coordinates as the master plan, not assembled into a fictional single view.')
 pic(c,D/'system-layout.png',17,29,180,211)
 for i,(t,b) in enumerate([('A01 / OPEN-COURT HOMES','West living district / P1. A complete residential court tests shared daily space, corner access and housing independent of an employer.'),('B03 / COMPUTE + REPAIR','Southern Works campus / P1-P3. Four staged modular groups test independent servicing and a limited local heat recipient. No claim that low-grade heat powers residential life.'),('C02 / FARM LEARNING EDGE','Southwest new trial campus / P1. Teaching, servicing and a public shade edge are arranged on new land outside the fixed pilots; the pilot interiors remain unchanged.')]):y=231-i*66;text(c,216,y,t,13,True);para(c,216,y-11,185,b,11)
page('Three-node locator','node_locator',locator)
NODES=[('A01','Open-court homes','Three-storey housing, shared mineral court and an explicit shade band. Local aerial; full-build-out context.'),('B03','An independent productive campus','Four staged modular-service groups, repair sheds, utility servicing and a separate worker shade spine. Local aerial; all stages shown.'),('C02','A working farm-learning edge','Two new service sheds, an accessible public promenade and eight trial PV rows. Outside fixed pilots; proposed forage and jojoba cultivation; irrigation entitlement unconfirmed.')]
for nid,title,sub in NODES:
 def aerial(c,nid=nid,title=title,sub=sub):head(c,nid+' / '+title,sub);pic(c,M/(nid+'-aerial.png'),17,29,386,210)
 page(nid+' aerial','node:'+nid,aerial)
 def experience(c,nid=nid,title=title):
  head(c,nid+' / use, access and spatial detail','A separate geometry-derived eye-level camera, plan and conceptual section; image details are illustrative, not capacity evidence.')
  pic(c,M/(nid+'-eye.png'),17,105,240,135,True);pic(c,D/(nid+'-section.png'),17,46,240,51);pic(c,D/(nid+'-plan.png'),271,103,131,137)
  stories={'A01':'Residents enter through the open corners and meet under the existing shade structure. A housing cooperative or municipal operator must fund cleaning, accessible paving, lighting and canopy inspections. No cars are routed through the shared court.','B03':'Workers reach the protected internal spine from the bus link. Freight takes the perimeter and service spurs. The registered human/machine interfaces are geometric flags, not proven-safe crossings. IT interruption contracts protect water/power limits; service budgets cannot depend on uninterrupted output.','C02':'Visitors use the public promenade while farm technicians and deliveries use the rear/side service road. Forage and pruned jojoba occupy alternating declared bands below raised panels. Planting requires lawful water and soil/wind trials; visitors stay outside the working lanes.'}
  para(c,17,37,386,stories[nid],9)
 page(nid+' eye plan section','node:'+nid,experience)
 if nid=='B03':
  def operation(c):
   head(c,'B03 / compact modules and shared campus services','0.35 km2 serviced campus within1.56 km2 gross estate;1.21 km2 is unserviced future reserve with no capacity credit.')
   pic(c,D/'B03-operating-plan.png',17,29,185,210);pic(c,D/'B03-module-group.png',215,119,188,115)
   para(c,215,108,187,'Four80 x40m covered groups each contain eight conceptual dual-container positions. Operating IT is assumed250kW/position: P1/P2/P3 =4/6/8MW. Public XPOD reference:6 racks x56kW =336kW simple rack nameplate;1MW power-block rating is not1MW IT.<br/><br/>50m side gaps and60m between-row service space reserve delivery, replacement, shared plant/fibre/thermal routes and worker shade. Vendor layout, fire access and crane envelopes remain engineering checks. Heat rejection is provided; local drying earns no useful-heat credit yet.',10)
  page('B03 modules and operating interfaces','node:B03',operation)
 if nid=='C02':
  def agriculture(c):
   head(c,'C02 / agriculture under the photovoltaic rows','Production, maintenance and visitors have distinct ground. This is proposed cultivation, not an existing planted field or a redesign of the protected pilots.')
   pic(c,D/'C02-operating-plan.png',17,109,228,128);pic(c,D/'C02-operating-section.png',17,28,228,75)
   para(c,263,232,139,'<b>Two compatible crop systems.</b><br/>Alternating2m bands carry forage and pruned jojoba. Four-metre panels have3.8m centre height and about3.1m minimum edge clearance; jojoba is held at1.2m. C02 has18m pitch,14m clear lanes and100m end headlands. All dimensions are assumed.<br/><br/><b>Wind and water.</b><br/>Jojoba is wind-pollinated: provisional1:8 male/female trial distribution along rows and both ends requires measured seasonal wind. Metered drip has separate valves and electrical isolation.<br/><br/><b>Real production budget.</b><br/>New C02 plus main-field crop bands total3.828ha forage +3.828ha jojoba. Irrigation allowances4000 /2000m3/ha/year give22,968m3/year. These are screening assumptions; lawful supply, soil and crop trials gate planting. No commercial yield credited.',10)
  page('C02 panel crop and service relationship','node:C02',agriculture)

def phases(c):
 head(c,'Build a complete first phase; expand only when it works','Relative periods are scenarios. Phasing boundaries, homes, jobs and service obligations reconcile to the same building inventory.')
 pic(c,D/'city-phasing.png',17,28,248,213)
 for i,p in enumerate(program):
  y=229-i*65;text(c,286,y,'P'+str(p['phase'])+' / '+p['period'],12,True);text(c,286,y-12,f"{int(p['cumulative_residents']):,} residents / {p['cumulative_dwellings']:,} homes",10,True);para(c,286,y-22,116,p['objective']+'. Funding and resource gates precede occupancy.',9)
def commissioning(c):
 head(c,'Commission operation, isolate the next works','Rust dashed routes reserve eastern/northern construction access; grey buildings remain unopened. These maps share the phase geometry and do not certify delivery rights.')
 for x,ph in zip([17,148,279],[1,2,3]):
  text(c,x,234,'PHASE '+str(ph),13,True);pic(c,D/('commissioning-P'+str(ph)+'.png'),x,44,124,182)
 para(c,17,34,386,'Campus commissioning:16 /24 /32 positions at assumed250kW operating IT each. Module delivery and essential-service testing precede energisation. Occupied West retains public access while future East/North works are fenced and bypassed.',10)
page('Construction isolation and commissioning','phasing',commissioning)
page('Construction phases','phasing',phases)
def first(c):
 head(c,'The first neighbourhood must operate on its own','P1 scenario: 1,776 dwellings, 4,440 residents, 905 modelled jobs. These are separate capacities; no employment-demand balance is assumed.')
 pic(c,D/'system-layout.png',17,28,182,213)
 for i,(t,b) in enumerate([('Before the first keys','Lawful external access, water abstraction/supply, treatment, power and emergency access must be secured. The western school (750 places), care/shops and the western civic band open with occupied homes.'),('An operating budget, not a promise','Ring-fenced housing/public-service funding covers education, healthcare, street/shade maintenance and worker travel. Compute downtime cannot remove essential city services.'),('If later investment stops','The western neighbourhood retains its own school, daily care, markets, utility modules and access. Eastern/northern works are gated. The mismatch between 19,680 eventual residents and 2,150 modelled jobs remains a demand/employment verification need, not an assumed commuter solution.')]):y=230-i*66;text(c,215,y,t,12,True);para(c,215,y-10,185,b,10)
page('Independent first operation','phasing_operation',first)
def resourcespage(c):
 head(c,'Resource gates define what can be occupied','All figures below are declared scenarios derived from capacity; no water entitlement, grid contract, yield or climate measurement is supplied by these calculations.')
 text(c,18,225,'WATER / FULL BUILD-OUT',14,True);text(c,18,207,f"{gross/1000:,.1f} thousand m3/y gross use",18,True);para(c,18,191,173,f"85 L/person/day domestic + 15 L/person/day civic, 35 L/job per workday and an indicative 0.1 L/kWh compute makeup assumption. Reuse: 100,000 m3/y scenario. After 8% distribution loss, required fresh abstraction is {fresh:,.0f} m3/y.<br/><br/>New forage/jojoba bands total7.656ha and include22,968m3/y assumed irrigation. Fixed pilot demand remains additional and unknown. No landscape irrigation or commercial crop yield is credited.",11)
 text(c,224,225,'POWER / FULL BUILD-OUT',14,True);text(c,224,207,'8 MW IT / four staged modular groups',18,True);para(c,224,191,178,f"P1/P2/P3 installed IT scenario: 4 / 6 / 8 MW. At assumed PUE 1.3, continuous full IT would use {resources['compute_mwh_y']/1000:.1f} GWh/y before town loads.<br/><br/>Explicit main PV rows reserve 26.784 MWp at an assumed 4 m panel width and 0.2 kWp/m2. At a synthetic 1,800 kWh/kWp/y yield, this is {resources['solar_mwh_y']/1000:.1f} GWh/y; it does not prove hourly matching or firm power.<br/><br/>Grid capacity, storage, weather and measured heat demand require independent study. No clean-energy percentage is claimed.",11)
page('Resource capacities and gates','key_metrics',resourcespage)
def trade(c):
 head(c,'What this city chooses, and what it must still prove','The proposal trades shortest productive routes and maximum uninterrupted IT output for independent housing, public services and a clearer operating boundary.')
 for i,(t,b) in enumerate([('A public-life decision','Living districts and the public band come first. Compute and production are arranged where service access can be controlled. This creates additional travel, utility cost and maintenance instead of claiming every adjacency is beneficial.'),('A capacity ceiling, not an instant new city','7,872 dwellings / 19,680 residents is the complete design capacity. Actual occupation requires housing demand, employment/livelihood evidence and independently funded services; the current 2,150 modelled jobs do not settle that question.'),('The next review has concrete questions','Survey and civil ground fit; lawful access and resource rights; noise, dust and emergency separation; an accessible walking/bus audit; crossing and canopy engineering; metered local drying demand; school staffing and annual operating budgets.'),('Traceable without overwhelming the presentation','Original controls, cameras, prompts, area/phase accounts and sources are in the separate technical appendix and machine files. Earlier V1 geometry is withdrawn from recommendation and retained for comparison. Neither polished images nor automatic file checks are independent design approval.')]):
  x=17 if i%2==0 else 218;y=229 if i<2 else 125;text(c,x,y,t,13,True);para(c,x,y-12,184,b,11)
page('Choices and next verification','conclusion',trade);c.save()
# A0: only spatial diagrams, selected capacities and short conditional stage captions. No table() call.
a0=P/'drawings/a0-board.pdf';c=canvas.Canvas(str(a0),pagesize=(1189*mm,841*mm));c.setTitle('THE EVERYDAY CITY | V2 A0');background(c,1189*mm,841*mm)
text(c,25,806,'THE EVERYDAY CITY',48,True);text(c,25,785,'CONTINUOUS LIVING DISTRICTS / SHARED PUBLIC GROUND / INDEPENDENT PRODUCTIVE EDGES',17,True,ACC)
pic(c,M/'city-centre.png',25,494,655,278,True);text(c,30,501,'TOWN CENTRE / LOCAL AERIAL / FULL BUILD-OUT CONCEPT',11,True)
text(c,706,771,'WHOLE-SITE ZONING + ROAD FRAMEWORK',15,True);pic(c,D/'whole-site.png',700,491,460,267)
# Three coordinated maps read together, while the whole-city true-distance locator prevents a misleading crop.
for x,file,title in [(25,'city-composite','DISTRICTS + CIVIC BAND'),(315,'city-mobility','STREETS + PUBLIC MOVEMENT'),(605,'city-landscape','DRY COMMONS + SHADE LINKS')]:
 text(c,x,475,title,14,True);pic(c,D/(file+'.png'),x,239,273,225)
text(c,911,475,'THREE CONDITIONAL STAGES',14,True);pic(c,D/'city-phasing.png',911,332,246,131)
for i,p in enumerate(program):
 y=315-i*30;text(c,911,y,f"P{p['phase']} / {int(p['cumulative_residents']):,} residents / {p['cumulative_dwellings']:,} homes",11,True);para(c,911,y-7,245,p['period']+'; access, resources, demand and funded services first.',9)
text(c,25,224,'THREE LOCATED PLACES / A01 WEST HOUSING / B03 SOUTHERN WORKS / C02 NEW FARM-LEARNING CAMPUS',14,True)
for x,(nid,title,sub) in zip([25,416,807],NODES):
 text(c,x,207,nid+' / '+title,15,True);pic(c,M/(nid+'-aerial.png'),x,89,181,108,True);pic(c,M/(nid+'-eye.png'),x+186,89,181,108,True);text(c,x,82,'LOCAL AERIAL',8,True);text(c,x+186,82,'EYE LEVEL',8,True);para(c,x,71,365,sub,10)
para(c,25,35,1135,'7,872 homes / 19,680 residents are full-build-out design capacities, not proven demand. Town-to-compute edge separation: 1.1 km; no residential heat pipe. Green diagram links are proposed dry-landscape/walking/shade opportunities, not mature trees. All images are illustrative finishes over registered geometry controls. Full source, phase and resource accounts are in the technical appendix; no spreadsheet tables appear on this board.',10)
text(c,1018,19,'JINGYUAN HUANG / V2 / 27 OCT 2026',9,True);c.save()
# Technical appendix: controls and accounts do not compete with the finished public narrative.
tech=P/'drawings/a3-technical-appendix.pdf';c=canvas.Canvas(str(tech),pagesize=(W,H));c.setTitle('THE EVERYDAY CITY | V2 technical appendix');tc=0

def endtech():
 global tc
 tc+=1;footer(c,tc);c.showPage()
head(c,'Technical record: boundaries, ground and limits','Version V2. Planar UTM19S figures are distinguished from geodesic machine metrics. Screening data is preliminary; image review is not engineering certification.')
rows=[['Test / capacity','Value / method']]+[[k,str(qa[k])] for k in ['whole_site_km2','master_km2','town_km2','dwellings','residents','jobs','housing_blocks','school_places','building_fixed_overlap_m2','building_channel_screen_overlap_m2','building_flood_screen_overlap_m2','base_gap_m2','base_overlap_m2','land_partition_gap_m2']];table(c,17,235,386,rows,[1,1],9);endtech()
head(c,'Exclusive territorial account','Gross area and current district edge logic; fixed context is unchanged and is not counted again as new development.')
rows=[['District / primary use','Area km2','Edge / basis']]+[[v['id']+' / '+v['name']+' / '+v['primary_use'],f"{v['area_km2']:.3f}",v['edge_logic']] for v in qa['regions']];table(c,17,235,386,rows,[1.4,.4,2.2],8);endtech()
head(c,'Complete construction capacity account','New / cumulative capacities, from current building inventory; household ratio 2.5 is assumed. Regional research districts receive no invented resident or job capacity.')
rows=[['Phase','Homes new / total','Residents new / total','Jobs new / total','Objective']]+[[p['phase'],f"{p['new_dwellings']} / {p['cumulative_dwellings']}",f"{p['new_residents']:g} / {p['cumulative_residents']:g}",f"{p['new_jobs']} / {p['cumulative_jobs']}",p['objective']] for p in program];table(c,17,235,386,rows,[.4,.8,.9,.8,2],9)
para(c,17,115,385,'Per-zone detail is in phasing_programme.json and the phased geometry. P1 has one 750-place school for an assumed 666 pupils; P2 has 1,500 for 1,458; P3 has 3,100 for 2,952. This arithmetic does not establish service staffing, age mix, school funding, employment demand or a lawful settlement entitlement.',11);endtech()
head(c,'Resource scenarios: water and power','Recomputable arithmetic; new crop irrigation is included; fixed-pilot consumption remains additional and unknown.')
rows=[['Scenario variable','Value']]+[[k,str(v)] for k,v in resources.items()];table(c,17,235,386,rows,[1,1.8],8);endtech()
for cam in cams:
 id=cam['id'];head(c,id+' / control and finished image',cam['scope']+' / '+cam['phase']);pic(c,P/'renders'/f'{id}.png',17,93,188,140);pic(c,M/f'{id}.png',215,93,188,140);text(c,17,83,'ORIGINAL GEOMETRY CONTROL',9,True);text(c,215,83,'SELECTED FINISHED CONCEPT',9,True);para(c,17,70,385,f"Camera UTM19S: {cam['position_utm19s']}; target {cam['target_utm19s']}; FOV {cam['fov_degrees']} degrees. Terrain and cameras come from the current model. Maximum-corner conceptual building plinths prevent terrain clipping and require civil design. AI materials, small people, furniture and mechanical details are illustrative; exact geometry fidelity needs continued independent review.",9);endtech()
head(c,'P1 operations and the 30 percent water stress test','Phase-one gross demand and the proposed public-service rules; all operating inputs remain declared scenarios.')
table(c,17,235,386,[['P1 water use','m3/year / assumed basis'],['Domestic + civic','162,060 / 4,440 people x100L/day'],['Compute makeup','4,555.2 / 4MW IT, PUE1.3, WUE0.1L/kWh'],['Industry + panel cleaning','10,502.5 / worker use plus1,000 panel cleaning'],['New forage / jojoba irrigation','22,968 / 7.656ha explicit crop bands, screening allowance'],['Gross total','200,085.7 / fixed-pilot consumption additional unknown'],['30 percent shortfall','60,025.71 / remaining140,059.99']],[1,2],10)
para(c,17,132,185,'<b>Water stress sequence.</b> Halt new occupation. First curtail the assumed agricultural allocation(22,968), with crop losses and critical plant survival reviewed by an agronomist. Then stop nonessential panel cleaning(1,000), compute makeup(4,555.2) and nonessential work use(7,330.5). Halving civic use saves12,154.5; the remaining12,017.51 reduction would reduce the domestic allowance from85 to about77.6L/person/day. Essential-service allocation and recovery must be independently verified before restrictions; normal public life is not assumed to continue.',10)
para(c,218,132,185,'<b>Firm obligations.</b> The proposed public/cooperative utility owns essential interfaces; compute is a replaceable concession with a decommissioning bond. Publish daily aggregate meters, monthly accounts and a quarterly independent audit. Household traces stay private. P1 assumes an unsecured12MW grid connection;0hours storage and0% hourly clean matching are credited. Occupancy requires actual income, utility and service-funding evidence.',10)
endtech()
head(c,'Source record and visual review','Public package: original model, cameras, controls, prompts, selected illustrations and dated review remain available separately.')
para(c,17,232,385,'<b>Issued sources.</b> Scope and fixed pilots: brief/site-package/boundaries and pilot-area. Terrain: Copernicus DEM GLO-30 source package, with its supplied licence and credits. Channels/flood bands: organiser DEM-derived studies, not surveyed limits. External roads: supplied OpenStreetMap extract; no on-site national/provincial road is asserted.<br/><br/><b>Retained original work.</b> The earlier Everyday City terrain-cost regional corridor study and steep/high terrain study are retained with attribution to reviews/withdrawn-v1. No other entry\'s urban layout is copied. All town, housing, campus, farm-edge and phase geometry is new for V2.<br/><br/><b>Visual review.</b> Eight distinct geometry cameras support two city views and aerial/eye-level pairs at A01, B03 and C02. The first overall finish invented planted trees and was rejected; the selected revision removes them. Controls never substitute for finished public views. Canopy members, access, building gaps, four compute halls and two farm sheds have been visually compared; this is not a pixel-level or construction certification.<br/><br/><b>Remaining verification.</b> Survey, detailed grading, noise/dust and thermal impacts, accessible routes, junction/crossing design, canopy engineering, resource rights, hourly grid/storage modelling, school operation and demand/employment evidence. Status remains an authorised public preview; automatic checks and content review are reported separately.',11);para(c,17,64,385,'Terrain derived products: produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA; all rights reserved. Road extract (c) OpenStreetMap contributors, ODbL1.0. Full licence statements: sources.json.',8);endtech();c.save()
sections=[]
for key in ['whole_site','node_locator','node:A01','node:B03','node:C02','phasing','key_metrics']:sections.append(dict(id=key,document='main',pages=[p['page'] for p in pages if p['section']==key]))
(P/'drawings/presentation-index.json').write_text(json.dumps(dict(schema_version=1,layout_version=2,documents=dict(main=dict(path='drawings/a3-booklet.pdf',pages=len(pages)),technical=dict(path='drawings/a3-technical-appendix.pdf',pages=tc)),sections=sections,pages=pages,note='Visual-first A0; no dense tables. Detailed accounts and controls are separate. No design approval.'),indent=2))
for src,name in [(main,'everyday-city-v2-booklet.pdf'),(a0,'everyday-city-v2-a0.pdf'),(tech,'everyday-city-v2-technical-appendix.pdf')]:shutil.copy2(src,OUT/name)
print('DELIVERED',len(pages),'main pages,',tc,'technical pages; outputs',OUT)
