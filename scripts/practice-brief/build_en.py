from pathlib import Path
import json,shutil,re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent; F=O/'assets/en'; IMG=O/'assets/products'; OUT=ROOT/'brief/design-practice-brief.en.pdf'
pdfmetrics.registerFont(TTFont('Arial','/System/Library/Fonts/Supplemental/Arial.ttf'))
W,H=841.92,595.92;BG='#F7F5F0';INK='#262626';BODY='#363634';GRAY='#8A877F';LINE='#D2CFC6';page=0;checks=[];c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('XCITY | Masterplanning and Urban Design Competition | Professional Practice Design Brief');c.setAuthor('XCITY');c.setSubject('Initial ideas of up to 10 pages; five shortlisted teams; US$300,000 in design honoraria and awards')
def rect(x,y,w,h,col,stroke=None):
 c.setFillColor(HexColor(col));c.setStrokeColor(HexColor(stroke or col));c.setLineWidth(.5);c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
def txt(s,x,y,size=11,color=BODY):
 assert not re.search('[\u4e00-\u9fff]',s),s
 c.setFillColor(HexColor(color));c.setFont('Arial',size);c.drawString(x,H-y-size,s)
def ph(s,w,size=10.5):
 p=Paragraph(s.replace('\n','<br/>'),ParagraphStyle('p',fontName='Arial',fontSize=size,leading=size*1.4,textColor=HexColor(BODY),splitLongWords=False));_,h=p.wrap(w,2000);return p,h
def para(s,x,y,w,size=10.5,color=BODY):
 assert not re.search('[\u4e00-\u9fff]',s),s
 p,h=ph(s,w,size);p.style.textColor=HexColor(color);p.drawOn(c,x,H-y-h);checks.append((page,s[:35],x,y,w,h));assert y+h<550,(page,s[:45],y+h);return h
def line(y,x=50,w=742,color=LINE):rect(x,y,w,.5,color)
def base(section,title):
 global page
 if page:c.showPage()
 page+=1;rect(0,0,W,H,BG);txt(section,50,41,8,GRAY)
 size=25
 if pdfmetrics.stringWidth(title,'Arial',size)>742:size=742/pdfmetrics.stringWidth(title,'Arial',1)
 txt(title,50,67,size,INK);txt('XCITY · PROFESSIONAL PRACTICE TRACK · DESIGN BRIEF · 26 OCT 2026',50,564,7,GRAY);txt(f'{page-1:02}',783,564,7,GRAY)
 c.bookmarkPage(f'p{page}');c.addOutlineEntry(title or 'XCITY',f'p{page}',0)
def image(name,x,y,w,h):
 p=Path(name);p=p if p.is_absolute() else F/p
 c.drawImage(str(p),x,H-y-h,w,h,preserveAspectRatio=True,anchor='c',mask='auto')
def image_frame(path,x,y,w,h):
 im=ImageReader(str(path));iw,ih=im.getSize();sc=max(w/iw,h/ih);dw,dh=iw*sc,ih*sc;c.saveState();clip=c.beginPath();clip.rect(x,H-y-h,w,h);c.clipPath(clip,stroke=0,fill=0);c.drawImage(im,x+(w-dw)/2,H-y-h+(h-dh)/2,dw,dh,mask='auto');c.restoreState()
def table(headers,rows,widths,y=140,size=10,minh=35):
 x=50
 for h,w in zip(headers,widths):txt(h,x,y,10,INK);x+=w
 line(y+23,color=INK);y+=28
 for row in rows:
  hh=max(ph(s,w-15,size)[1] for s,w in zip(row,widths))+16;hh=max(hh,minh);x=50
  for s,w in zip(row,widths):para(s,x,y+5,w-15,size);x+=w
  line(y+hh-2);y+=hh
 assert y<551,(page,'table bottom',y)
 return y

def columns(items,y=143,size=11):
 for x,(title,body) in zip([50,435],items):txt(title,x,y,12,INK);line(y+28,x,357,INK);para(body,x,y+43,357,size)
# 01
base('X C I T Y · SAN JUAN, ARGENTINA','')
image('site-context.png',375,0,467,H)
txt('XCITY',50,151,31,INK);txt('International',50,206,26,INK);txt('Masterplanning &',50,241,26,INK);txt('Urban Design Competition',50,276,23,INK);txt('Professional Practice Track',50,331,14,GRAY)
para('Design Brief\nApproximately 1,656 km²\nSite-wide framework · Phase 1 · Focus areas',50,409,290,10)
para('Initial ideas of up to 10 pages → Five shortlisted teams\nTotal design honoraria and awards: US$300,000',50,490,300,9)
# 02
base('CONTENTS','Contents')
items=[('01','Competition overview'),('02','The design challenge'),('03','Regional context'),('04','The site'),('05','Existing conditions'),('06','Vision and objectives'),('07','Design scope'),('08','Programme and development metrics'),('09','Site constraints'),('10','Design considerations'),('11','Phasing and delivery'),('12','Submission requirements'),('13','Evaluation criteria'),('14','Competition procedure'),('A','Site information')]
for i,(n,t) in enumerate(items):
 col=i//8;row=i%8;x=50+col*385;y=131+row*46;txt(n,x,y,10,GRAY);txt(t,x+45,y,11.5,INK);line(y+30,x,352)
# 03
base('01 · COMPETITION OVERVIEW','Competition overview')
para('XCITY proposes a new city in San Juan Province, Argentina, with energy, computing and productive land at its foundation. This competition invites professional practices and multidisciplinary consortia to develop a site-wide framework, a Phase 1 urban design and proposals for key places within the city.',50,121,742,11)
table(['Item','Requirement'],[
['Location and site','San Juan Province, in the Andean foothills of western Argentina. Competition area: approximately 1,656 km².'],
['Early works area','Fixed pilots: agrivoltaic fields 01–03 (13.9 km²) and the Phase 1 living quarter (2.48 km², outline only). XCITY delivers both; proposals connect to them without redesigning them.'],
['Participation','Registration is free. All applicants follow the same application requirements, eligibility review and selection criteria.'],
['Stage 1','Apply online, then return the emailed qualification application form with evidence and initial ideas of up to 10 pages. Eligibility is checked before ideas, experience and team are assessed to select five teams.'],
['Stage 2','The five shortlisted teams develop full proposals after appointment and receipt of the brief and common site information package. Briefings and Q&A will be online.'],
['Honoraria and award','Each valid Stage 2 submission earns US$50,000. One winner receives an additional US$50,000. Total: US$300,000.'],
['Further services','Any subsequent design commission, fees and rights to adapt or implement the work will be negotiated under a separate agreement.']],[115,627],y=184,size=9.6,minh=41)
#04
base('02 · THE DESIGN CHALLENGE','The design challenge')
para('XCITY proposes a new city in San Juan where energy, computing, agriculture and related industries form the economic foundation. The challenge is to show how these activities can sustain jobs, permanent homes, public services and everyday life, and how a city can take shape on this particular site.',50,127,742,11.5)
txt('THE CENTRAL QUESTION',50,205,11,GRAY)
para('How can this land become a city people choose to live in?\nWhere should it begin, and how can the first phase bring production and everyday life together within available resources?',50,235,720,19,INK)
for i,(title,body) in enumerate([
('01 From production to urban life','Identify who will work and live here, and how economic activity creates jobs and demand for services. Relate population, housing and public provision to credible energy, computing and agricultural capacity.'),
('02 Let the site shape the plan','Water availability, terrain, seasonal drainage, intense sun, wind and dust should determine siting, density, streets and open space. Explain where to build, where to produce and what to protect.'),
('03 Make the first phase work','Provide access, water, power, productive activity, housing and services in an operational first phase. Show how it can function if later development is delayed and what should trigger expansion.')]):
 x=50+i*255;txt(title,x,354,11.5,INK);line(384,x,232,INK);para(body,x,403,232,10.1)
para('Translate changes in work, services and movement enabled by AI agents, robotics and autonomous vehicles into the design of streets, blocks and key places.',50,520,742,9,GRAY)
#05
base('03 · REGIONAL CONTEXT','Regional context')
regional=[('Population','San Juan Province had 822,853 residents in the 2022 census, around 20% more than in 2010. Population is concentrated in Greater San Juan.'),('Mining','Mineral exports reached US$1.467 billion in 2024, accounting for 81.2% of provincial exports. Gold mining and emerging copper projects form an important regional economic base.'),('Agriculture','San Juan is Argentina’s second-largest wine-growing province, with 19.8% of national vineyard area in 2024. Pistachios, olives and related processing are also relevant to the region.'),('Energy','The source brief records 21 operating solar plants and 547.4 MW of installed capacity at the end of 2024. Solar generation supplied approximately 54% of provincial electricity demand that year.'),('Water','Irrigated agriculture depends on the San Juan River and reservoirs including Los Caracoles, Punta Negra and Ullum. Drought and variable supply make water availability a central planning consideration.'),('Connections and seismic risk','RN 150 connects towards Chile via the high-altitude Agua Negra pass. Seasonal access must be distinguished from future tunnel proposals. San Juan’s earthquake history makes resilience and emergency access essential.')]
for i,(title,body) in enumerate(regional):
 x=50+(i%3)*255;y=139+(i//3)*180;txt(title,x,y,13,INK);line(y+27,x,232,INK);para(body,x,y+43,232,10.2)
para('Regional background is retained from the source brief, with the stated reference years. Provincial totals are context, not evidence of water rights, grid capacity or demand available to the project.',50,520,742,8,GRAY)
#06
base('04 · THE SITE','Location')
image('location-continent.png',50,128,180,300);image('location-region.png',244,128,310,300)
para('South America · San Juan Province',50,436,180,8,GRAY);para('San Juan and the surrounding region',244,436,310,8,GRAY)
para('The site lies northeast of San Juan city, in the Andean foothills of western Argentina. Its regional relationships include existing settlements, agriculture, mining services and transport links across Argentina and towards Chile.',580,145,212,11)
para('Explain how Phase 1 will share services, jobs, procurement and transport with existing places. Regional studies may extend beyond the site; this does not imply development rights outside it.',580,324,212,10.5)
para('Base maps: Natural Earth. Provincial boundaries: amCharts geodata. Competition boundary: XCITY project information. For regional orientation only.',50,514,742,8,GRAY)
#07
base('04 · THE SITE','Location and access')
image('satellite-region.jpg',50,125,345,378);image('satellite-site.jpg',425,125,367,190)
roads=json.loads((O/'analysis.json').read_text())['road_straight_distance_km']
for i,(a,b,k) in enumerate([('RN 40','North–south regional route','RN40'),('RN 20','San Juan and eastern links','RN20'),('RN 141','Eastern regional connection','RN141'),('RN 150','Regional connection towards Chile','RN150'),('RP 510','Eastern provincial road','RP510')]):
 y=330+i*30;txt(a,425,y,9);txt(b,485,y,8.6);txt(f'{roads[k]:.1f} km',735,y,9);line(y+23,425,367)
para('Distances are the shortest straight-line measurements from the site boundary to each road, not driving distances. Proposals must assess access routes, rights and enabling works.',425,491,367,8.5)
para('Satellite mosaic: Esri World Imagery; credits are shown on the image. Accessed 26 October 2026. Acquisition dates vary across the mosaic. The yellow line marks the competition display boundary.',50,512,345,7.5,GRAY)
c.linkURL('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer',(50,H-545,395,H-510))
#08
base('04 · THE SITE','Early works area')
image('lead-zone.png',50,122,420,405)
para('Fixed pilot areas\nAgrivoltaics: 13.9 km²\nLiving quarter: 2.48 km²',510,152,282,19,INK)
para('XCITY delivers both pilots separately. Keep their boundaries and internal layouts unchanged. Show the land-use, street, water, energy and service connections. Fields 01–03 are numbered on the map; L marks the living-quarter outline.',510,254,282,11)
para('Assess these interfaces when selecting Phase 1. Do not treat early works as background scenery or assume that every facility shown in the reference information is already operating.',510,395,282,10.5)
#09
base('05 · EXISTING CONDITIONS','Climate')
para('The region is arid, with little rainfall and marked temperature variation. Heat, intense sun, windblown dust and the Zonda wind should inform street orientation, shade, public space, equipment air intakes, maintenance and cleaning-water demand.',50,121,742,11)
image('climate.png',50,179,742,260)
for x,n,t in [(50,'90.5 mm','Annual precipitation'),(305,'18.0 °C','Annual mean temperature'),(560,'27.3 / 7.5 °C','January / July mean temperature')]:txt(n,x,445,21,INK);txt(t,x,478,9,GRAY)
para('Source: Argentina’s National Meteorological Service (SMN), SAN JUAN AERO, 1991–2020 normals; station elevation 597 m. The line shows monthly mean temperature, not mean daily maximum. These regional observations do not resolve the site’s elevation and local microclimates.',50,513,742,7.8,GRAY)
c.linkURL(json.loads((O/'climate.json').read_text())['source'],(50,H-545,792,H-510))
#10
base('05 · EXISTING CONDITIONS','Terrain and slope')
image('elevation.png',50,130,348,300);image('slope.png',444,130,348,300)
txt('Elevation: approximately 636–1,354 m',50,436,10,INK);txt('5th–95th percentiles; maximum approximately 2,658 m',50,461,9);txt('Minimum DEM elevation: approximately 606 m',50,484,9)
txt('Slope classes within the competition area',444,436,10,INK)
for i,(col,t) in enumerate([('#DAD7AD','<2%: ~1,183.6 km²'),('#A7B790','2–5%: ~182 km²'),('#A88B61','5–15%: ~132 km²'),('#666254','>15%: ~158 km²')]):
 x=444+(i%2)*177;y=465+(i//2)*26;rect(x,y+3,10,8,col);txt(t,x+16,y,9)
para('Boundary seams closed; external outline unchanged. Geometry 1,656.684 km²; project nominal area 1,656 km². This is not cadastral verification. Terrain: Copernicus GLO-30 DEM, 60 m grid, 300 m slope smoothing; raster areas are indicative.',50,520,742,7.7,GRAY)
#11
base('05 · EXISTING CONDITIONS','Hydrology and preliminary development suitability')
for i,(name,title) in enumerate([('drainage.png','Seasonal drainage'),('flood-screen.png','Flood sensitivity screening'),('buildable-screen.png','Preliminary suitability screening')]):
 x=50+i*255;txt(title,x,126,10,INK);image(name,x,150,232,269)
para('Drainage lines are classified by DEM-derived upstream catchment area. They show potential flow paths and connectivity, not perennial water availability.',50,425,232,9.5)
para('Approximately 503 km² falls within 1.5 km of channels draining at least 100 km², and less than 3 m above the channel bed.',305,425,232,9.5)
para('Approximately 686 km² has slopes below 2% outside the issued sensitivity screen. This screening does not establish development rights or exclude all other land from design.',560,425,232,9.5)
para('Issued package method: 60 m DEM, D8 flow routing and height above nearest drainage (HAND). Upstream flows beyond the analysis extent are excluded. The 503 km² screen is not a surveyed flood limit or a blanket no-build zone. Newly closed seams are unclassified by this prior flood screen. Check water, geology, ecology, land rights and hazards; keep permanent buildings out of dry channel beds.',50,509,742,8,GRAY)
#12
base('06 · VISION AND OBJECTIVES','Five urban systems')
image('systems-overview.png',50,125,302,385)
sy=[('Energy and computing','Locate with reliable power, communications and maintenance access. Test cooling, water access, flood safety and buffers to residential areas.'),('Agricultural production','Connect agrivoltaics, other crops, irrigation, processing and storage. Match the scale of production to resources and servicing needs.'),('Housing and public life','Compact settlements support services and shared streets. Low-density estates must account for land take, access and service costs.'),('Industry and automation','Provide processing, manufacturing, repair and internal logistics with each phase. Gateway industries depend on external access and resources.'),('Trade and logistics gateways','Study freight, storage, transfer and future trade functions. Customs, bonded or free-trade status depends on the relevant approvals.')]
for i,(a,b) in enumerate(sy):
 y=133+i*73;txt(a,380,y,11,INK);para(b,380,y+22,412,9.5);line(y+66,380,412)
para('Indicative positions from the issued site package, not fixed sites or land-use boundaries. Proposals may retain, move or challenge them with reasons. Halos show broad intentions, not measured land allocations.',50,517,742,7.7,GRAY)
#13
base('06 · VISION AND OBJECTIVES','Five urban systems · Individual diagrams')
short=['Energy and computing','Agriculture','Housing and public life','Industry and automation','Trade and logistics']
for i,(name,(title,body)) in enumerate(zip(['compute','agri','living','industry','port'],sy)):
 x=50+i*151;txt(short[i],x,132,9.3,INK);image('system-'+name+'.png',x,162,138,197);para(body,x,378,138,9)
para('Solid markers show indicative positions from the issued package; hollow markers indicate potential later functions. Halos are not land-use boundaries. Gateway access and timing require testing. The diagrams do not prescribe land-use percentages.',50,511,742,8,GRAY)
#14
base('06 · VISION AND OBJECTIVES','Project systems and reference typologies')
para('The project combines agrivoltaics with modular computing facilities. Retain the system logic while testing spatial, resource and operational interfaces. The images below are project and product references, not photographs of existing facilities on the site.',50,121,742,10)
for name,x in [('X344.jpg',50),('X345.jpg',236),('X441.jpg',435),('X442.jpg',621)]:image_frame(IMG/name,x,176,171,96)
columns([('Agrivoltaics · Under panels and beyond','The source concept combines jojoba, rosemary, fodder cactus, alpacas and supplementary feed. Keep taller crops and vines outside the panel array. Test mature plant height, solar access, maintenance, animal movement and equipment protection. Agronomic performance requires evidence.'),('Computing · POD modules and clusters','Use XCITY POD’s modular, factory-integrated and distributed deployment principles to test power, water, fibre, transport, maintenance, fire access and buffers. Relate capacity, cooling and expansion to resource availability, and identify credible users of recovered heat.')],y=307,size=9.7)
for x,label in [(50,'Solar generation'),(240,'Crops and fodder'),(430,'Grazing and processing'),(620,'Composting and soil')]:
 line(487,x,171,INK);txt(label,x,498,10.5,INK)
 if x<620:txt('→',x+176,495,13,GRAY)
#15
base('06 · VISION AND OBJECTIVES','Vision and objectives')
para('Develop a city where energy, computing and agriculture support productive activity and a complete public life. AI agents and robots should contribute to a coherent urban environment, rather than appear as isolated technologies or showcase buildings.',50,129,742,12)
table(['Objective','What proposals must demonstrate'],[
['Resources and capacity','Derive population, jobs, housing and loads from credible water, energy and economic assumptions. Distinguish opening, Phase 1 completion and longer-term capacity.'],
['Shared use of land','Combine energy, agriculture, facilities and urban uses where appropriate, without double-counting land or resources.'],
['Complete public life','Establish education, healthcare, shops, social spaces and leisure for residents and operating staff.'],
['Operational phases','The first phase must function if later development is delayed. State its essential facilities and external dependencies.'],
['People and machines','Make automation compatible with safety, accessibility, public responsibility and the quality of everyday space.']],[145,597],y=226,size=10,minh=51)
para('Common Phase 1 reference: 50,000 residents; 20,000 jobs; 200 MW computing load; 1–3 GW solar. Water is not secured: state the assumed source. Teams justify longer-term capacity.',50,524,742,8,GRAY)
#16
base('07 · DESIGN SCOPE','Scope and level of detail')
table(['Level','Extent and purpose','Required evidence'],[
['Site-wide framework','Cover the full competition area of approximately 1,656 km². Study regional connections beyond the boundary where necessary.','Positioning, development capacity, the five systems, ecology, water, transport, utilities and phasing. Indicative drawing scales: 1:50,000–1:100,000.'],
['Phase 1 urban design','Select and justify the location and extent. No fixed focus-area size is prescribed. Establish a complete first phase that can operate.','Masterplan, land use, streets, public services, open space, utility interfaces, density, height and delivery. Indicative scales: 1:10,000–1:5,000.'],
['Urban design studies','Choose a coherent area or connected areas. Explain the selection, capacity and relationship to the wider systems.','Blocks, plots, building massing, public frontages, servicing, key sections and consistent metrics that test the Phase 1 plan.'],
['Focus areas and strategies','Address the topics on the following page. Combine related topics where useful; isolated landmarks do not substitute for urban design.','Local plans, sections, spatial prototypes, circulation and operational relationships. Indicative local scales: 1:1,000–1:500, with larger sections where needed.']],[132,300,310],y=139,size=10,minh=88)
para('Choose scales to suit the drawing and its purpose. Include boundaries, north arrows, scales, legends and key dimensions. This is a concept planning and urban design competition; statutory submissions, surveys, detailed engineering and construction documents are outside its scope.',50,520,742,8,GRAY)
#17
base('07 · DESIGN SCOPE','Focus areas and strategic topics')
para('Choose three of the six spatial topics for detailed design. Address the other three and all five strategic topics in principle: three in depth, eight in principle. Place every topic within the overall plan and its phase; related topics may share drawings.',50,123,742,10.5)
left=['City entrances and arrival sequences','Residential communities and housing types','Foothill retreats and spaces for contemplation','Logistics hubs and future trade interfaces','Computing facilities and heat recovery','Streets shared by people and autonomous vehicles'];right=['Drone landing and docking networks','Agrivoltaics and the urban edge','Seasonal channels and park systems','Places for art and culture','Public space in heat, strong sun and windblown dust']
for x,title,items in [(50,'Six spatial topics · choose three',left),(435,'Five strategic topics · answer all',right)]:
 txt(title,x,190,12,INK);line(220,x,357,INK)
 for i,s in enumerate(items):txt(f'{i+1:02}',x,238+i*33,9,GRAY);para(s,x+27,237+i*33,330,9.6)
para('Show local plans and programme, building–landscape–infrastructure interfaces, access and servicing, key sections and spatial prototypes. Use representative views to explain the proposal; the same number of renderings is not required for every topic.',50,457,357,9.5)
para('Explain the location, principles, users, stage and system interfaces. Plans, axonometrics, sections, process diagrams and system drawings may be used as appropriate.',435,424,357,9.5)
#18
base('08 · PROGRAMME AND DEVELOPMENT METRICS','Programme and development metrics')
para('Provide the following functions and establish the metrics for the proposed population, economic activity and resource scenario. State the area, phase, units, sources and calculation method behind each figure.',50,122,742,10.5)
table(['Function','Programme','Metrics and evidence'],[
['Housing and services','Housing, education, healthcare, shops, culture and administration','Population, homes, land and floor area, service capacity and provision standards.'],
['Computing','Module clusters, cooling, buffers and heat recovery','Phased loads, power supply, cooling method, water demand and heat users.'],
['Energy','Solar generation, storage, distribution and resilience','Installed capacity, energy supply, storage, night and winter operation and disruption response.'],
['Agriculture','Agrivoltaics, other crops, processing and storage','Land, overlapping uses, crops, irrigation and production services.'],
['Industry and logistics','Settlement-based production and internal logistics; future gateway functions','Jobs, land, freight, servicing, connections and triggers for later development.'],
['Transport','Regional access, streets, public transport and active travel','Hierarchy, dimensions, accessibility, coverage and human–machine interfaces.'],
['Utilities','Water, treatment, reuse, communications and waste','Capacity, service areas, prerequisites and sequence of expansion.']],[115,300,327],y=185,size=9.8,minh=44)
#19
base('09 · SITE CONSTRAINTS','Site constraints')
table(['Constraint','Design requirement'],[
['Channels and flooding','Do not place permanent buildings in dry channel beds. Sensitivity mapping supports site comparison; it is not a statutory flood boundary. Explain safe closure, evacuation and recovery at crossings and activity areas.'],
['Early works','Keep both fixed pilots unchanged: agrivoltaic fields 01–03 and the Phase 1 living-quarter outline. Do not add buildings or redesign within them; show streets, water and service interfaces.'],
['Slopes and hills','Maintain catchment and ecological continuity. Foothill development must address contours, hard surfaces, runoff, access and evacuation. Slope alone does not establish development suitability.'],
['Site boundary','Use the same owner-supplied competition boundary throughout. Graphic connections do not add land or confer cadastral rights.'],
['Water','Separate legal rights, available supply, demand and reuse. Identify unconfirmed conditions as assumptions, with their consequences and verification needs.'],
['Seismic risk and lighting','Plan for emergency access and recovery, with subsequent design subject to applicable local seismic requirements. Control glare, upward light spill and operational lighting.']],[132,610],y=142,size=10,minh=57)
#20
base('10 · DESIGN CONSIDERATIONS','Design considerations')
topics=[('Industry and programme','Explain the economic relationship between energy, computing, agriculture, manufacturing and logistics, including Phase 1 jobs and skills.'),('Spatial structure','Test a single-city, multi-settlement or combined approach. Explain centres, neighbourhoods, public services and directions of growth.'),('Movement and access','Address regional connections, enabling access works, streets, freight, public transport, walking, cycling, autonomous vehicles and drones.'),('Utilities and energy','Integrate water and reuse; solar generation, storage and distribution; cooling and recovered heat; communications, waste and backup systems.'),('Ecology and landscape','Address seasonal channels, flood sensitivity, hills and catchments, drought-adapted planting, shade and the productive urban edge.'),('Urban form and character','Relate density, height and public frontages to heat, wind, dust, earthquakes and evacuation. Include lighting and dark-sky protection.'),('Delivery','Identify the first works and services, expansion triggers, temporary and permanent facilities, and early decisions that are difficult to reverse.')]
for i,(a,b) in enumerate(topics):
 x=50+(i%2)*385;y=135+(i//2)*99;txt(f'{i+1} · {a}',x,y,12,INK);para(b,x,y+28,357,10.5)
#21
base('10 · DESIGN CONSIDERATIONS','Key technical questions')
tech=[('Water','Quantify domestic, cooling, agricultural, landscape and industrial demand. Distinguish abstraction, reuse and consumption, and identify priorities under reduced supply.'),('Jobs and population','Relate opening and Phase 1 jobs, residents and housing. Account for households, commuting, shifts, skills and service populations; do not assume one resident per job.'),('Night and winter energy','Explain generation, storage and backup arrangements and their implications for facilities, housing, streets and essential services.'),('People and machines','Show where autonomous vehicles, robots and pedestrians meet. Demonstrate separation, sharing or time-based access through dimensions and operating scenarios.'),('Expansion triggers','Identify observable conditions for the next phase and hard-to-reverse decisions concerning primary routes, facilities and protected spaces.'),('Hazard response','Address flooding, earthquakes and strong winds through evacuation, shutdown and recovery strategies. Keep permanent buildings out of dry channel beds.')]
for i,(a,b) in enumerate(tech):
 x=50+(i%2)*385;y=140+(i//2)*128;txt(f'{i+1} · {a}',x,y,12,INK);para(b,x,y+30,357,10.5)
#22
base('11 · PHASING AND DELIVERY','Phasing and delivery')
para('XCITY will deliver the early works area separately. Proposals must establish the location, extent, content and triggers for urban development phases. Phase 1 should connect to early facilities and provide the production, housing, services and resources needed to operate.',50,129,742,11)
for x,n,title,body in [(50,'01','Opening and Phase 1','First jobs, homes and public services.\nAccess, energy, water and operations.'),(310,'02','Subsequent expansion','Growth in residents and economic activity.\nResource and infrastructure thresholds.'),(570,'03','Continued adaptation','Review capacity and risk at each stage.\nProtect land and retain system flexibility.')]:
 txt(n,x,231,26,GRAY);line(276,x,222,INK);txt(title,x,294,14,INK);para(body,x,333,222,11)
 if x<570:txt('→',x+232,280,17,GRAY)
para('For each phase, show its boundary, capacity, essential works, users, prerequisites and expansion triggers. Distinguish a target timetable from the conditions that enable development. Explain how the city operates if later phases are delayed and how temporary facilities are replaced.',50,431,742,11)
para('Identify the questions for subsequent specialist work. Future engineering commitments do not substitute for a clear spatial, resource and delivery strategy in this competition.',50,516,742,9,GRAY)
#23
base('12 · SUBMISSION REQUIREMENTS','Submission requirements')
para('Stage 1: initial ideas of up to 10 pages, submitted as a PDF, which may be exported from PowerPoint. Eligibility documents, team details and references are separate and do not count towards the 10-page limit. A full design is not required; Stage 1 is unpaid.',50,122,742,10.5)
table(['Stage 2 deliverable','Required content'],[
['Site-wide framework','Regional and site analysis; spatial structure; the five systems; ecology and water; transport and logistics; utilities and phasing; development capacity and its basis.'],
['Phase 1 urban design','Masterplan; land use and programme; streets and public transport; services and open space; utility interfaces; density, height and delivery plan.'],
['Urban design studies','Blocks and plots; building massing and frontages; service routes; key sections; design guidance and metrics for the same area.'],
['Focus areas and strategies','Local plans; building, landscape and infrastructure interfaces; key sections; use and operating scenarios; representative spatial views.'],
['Technical information','Editable metrics and supporting calculations; resource and phasing analysis; assumptions and sources; the CAD/GIS files and models used, with coordinates, layers and viewing instructions.'],
['Summary and presentation','Six landscape A0 boards; A3 report up to 60 pages including appendices and a requirement-to-drawing index; design statement up to 800 words; one preview image; principal-led online presentation and Q&A.']],[155,587],y=196,size=10,minh=47)
para('Stage 2: English; anonymous boards without practice names or logos. Supply an XLSX metrics workbook and CAD/GIS files. Video and physical models are optional; extra media earn no marks. Include north arrows, scales, dimensions and sources.',50,520,742,8.5,GRAY)
#24
base('13 · EVALUATION CRITERIA','Evaluation criteria')
txt('Stage 1 · Selection of initial ideas',50,128,13,INK)
table(['Criterion','What the panel will assess'],[
['Site understanding and direction','Does the initial ideas submission identify the site’s constraints and resources and offer a coherent direction for its systems and first phase?'],
['Relevant work and proposed team','The quality of reference projects, experience with comparable challenges, actual responsibilities, specialist collaboration and team commitment.'],
['Method and deliverability','A clear approach to the questions and evidence that need testing. Rendering quantity and brand recognition do not replace professional judgement.']],[170,572],y=159,size=9.6,minh=44)
txt('Stage 2 · Evaluation of full proposals',50,338,13,INK)
for i,(a,b) in enumerate([('Site and spatial structure','Site conditions shape siting, centres, corridors and growth.'),('Systems and resources','Water, energy, computing, population and services support one another.'),('Urban and spatial quality','Streets, blocks, centres and public spaces serve different users.'),('Phasing and delivery','Phase 1 operates independently; dependencies and triggers are credible.'),('Interfaces and further work','Disciplines are coordinated and verification needs are identified.'),('Communication','Drawings, figures and explanations are clear and consistent.')]):
 y=370+i*26;txt(a,50,y,9.4,INK);txt(b,240,y,9.4);line(y+21)
para('Criterion weights will be published with the formal rules.',50,537,742,8,GRAY)
#25
base('14 · COMPETITION PROCEDURE','Eligibility and qualifications')
para('The competition is open to professional practices and consortia worldwide. Applicants may prepare their ideas with the rest of the application. Eligibility is reviewed before the ideas are assessed; registration does not secure a Stage 2 place.',50,141,742,10.5)
table(['Requirement','Evidence'],[
['Legal status','A legally registered practice or consortium. Provide a certificate, business registration or an official registry lookup URL; ordinary electronic copies or scans are sufficient.'],
['Professional standing','Provide applicable planning, architectural or landscape permissions, or explain the local regime. The team must cover masterplanning, urban design and landscape/ecological expertise.'],
['Equivalent evidence','Where there is no equivalent practice accreditation system, provide registration, applicable individual professional credentials and evidence of the permitted scope of business.'],
['Experience and team','Identify relevant planning and design work, the team’s actual role, the principal designer and participating staff. Explain specialist input for water, energy, transport and delivery.'],
['Consortia and duplicate entries','Provide an agreement or a statement naming the lead entity, members and responsibilities. A member may not also apply independently or join another consortium in this competition.']],[145,597],y=200,size=10,minh=55)
para('Credentials establish professional standing. References, the proposed team and initial ideas of up to 10 pages inform selection. All information must be truthful and verifiable. Disclose relationships or interests involving the organiser or panel members.',50,518,742,8.5,GRAY)
#26
base('14 · COMPETITION PROCEDURE','Registration and email application')
para('Apply online: xcityus.github.io/xcity-ai-competition/practice.html#apply',50,139,742,11,INK)
c.linkURL('https://xcityus.github.io/xcity-ai-competition/practice.html#apply',(50,H-167,792,H-137))
for i,(a,b) in enumerate([
('Apply online','Applications are open. Complete institution, country or jurisdiction, contact and email on the official practice page. No attachments are needed in this form.'),
('Receive the application form','We will email the qualification application form and materials checklist to the address provided. Complete the form and gather the applicable evidence and initial ideas.'),
('Reply with the form and materials','Complete the emailed form. Attach registration evidence or registry URL, applicable professional evidence or an explanation, team and portfolio or project references, and an ideas PDF of up to 10 pages. Reply to competition@xcity.ai.'),
('Stage-one review','Apply online by 31 December 2026, 23:59 UTC. Return the complete form and materials by 31 January 2027, 23:59 UTC. Five teams are selected in February 2027. Completing the online form alone does not complete stage one or mean shortlisting.')]):
 y=207+i*76;txt(f'0{i+1}',50,y,18,GRAY);txt(a,93,y,12,INK);para(b,93,y+25,699,9.6)
para('Ordinary electronic copies or scans are accepted; no notarisation is requested. Follow the attachment instructions in the application email. Contact: competition@xcity.ai.',50,526,742,8,GRAY)
#27
base('14 · COMPETITION PROCEDURE','Stage 1 · Initial ideas of up to 10 pages')
para('Use up to 10 pages to explain your reading of the site, your initial urban proposition and what you would test if shortlisted. This stage is about direction and approach, not a completed masterplan. The five topics below are suggested; allocate the pages as needed.',50,124,742,11)
table(['Suggested topic','What it should communicate'],[
['1 Site reading and key questions','Identify the terrain, water, climate, resources and regional relationships that matter most, and the questions you would address first.'],
['2 Site-wide and system ideas','Use a simple diagram to show how energy and computing, agriculture, public life, industry and logistics could work together across the site.'],
['3 Phase 1 rationale','Suggest a starting location or selection principles. Explain how production, housing, public services and essential infrastructure could support one another.'],
['4 A spatial idea or sketch','Illustrate one representative spatial proposition through a sketch, relationship diagram or section. Show how it tests the wider idea; polished renderings are not required.'],
['5 Method and collaboration','Outline your design approach, key assumptions, questions for verification and proposed specialist collaboration.']],[155,587],y=181,size=10,minh=45)
columns([('Format and workload','Submit a PDF of up to 10 pages, which may be exported from PowerPoint. Credentials, team details and references are separate. A complete masterplan, engineering calculations and additional renderings are not required.'),('Selection and use of ideas','The panel will select five teams using the criteria in Section 13, considering the ideas, reference work and proposed team. Stage 1 is unpaid. Unselected ideas do not grant rights to adaptation or implementation.')],y=454,size=9.4)
#28
base('14 · COMPETITION PROCEDURE','Stage 2 · Design honoraria and winner’s award')
para('The five shortlisted teams begin full design work after signing the participation agreement and receiving the complete brief and common site information package. Shortlisting establishes eligibility for the Stage 2 honorarium; it does not trigger an advance payment.',50,123,742,10.5)
table(['Payment','Allocation','Payment condition'],[
['Stage 2 design honoraria','5 teams × US$50,000\nSubtotal: US$250,000','Payable following a complete, valid Stage 2 submission in accordance with the brief and participation agreement, irrespective of ranking.'],
['Additional winner’s award','1 team × US$50,000','Paid to the winning team after the result is announced, in addition to its Stage 2 honorarium.'],
['Total','US$300,000','The winner receives US$100,000 in total. Each of the other four teams receives US$50,000.']],[155,240,347],y=203,size=10.3,minh=64)
columns([('What counts as a valid submission','Submit the required Stage 2 material and respond substantively to the design task. Eligibility is reviewed beforehand. Completeness checks and design evaluation are separate; a lower ranking does not remove the honorarium.'),('What the payments cover','Stage 1 is unpaid and there is no Stage 2 advance. No separate design-development award is offered. Later design services are outside these payments. Tax treatment, payment documents and settlement procedures are governed by the participation agreement.')],y=449,size=9.4)
#29
base('14 · COMPETITION PROCEDURE','Briefings, jury process and use of submissions')
columns([('Online briefings and common information','No site visit will be organised. The organiser will provide a common site information package, an online briefing and coordinated Q&A. Material clarifications and updates will be shared with every participant in the relevant stage.'),('Jury process','A jury of qualified experts will evaluate submissions against the published criteria. Jurors must disclose conflicts of interest and recuse themselves where appropriate. Jury details will be shared through the competition’s official contact channel once confirmed.')],y=129,size=10.5)
line(300,color=INK);txt('Publicity and terms',50,321,13,INK)
para('Authors retain copyright and are responsible for originality and third-party permissions. Stage 2 participants grant the organiser a non-exclusive licence to use submissions for competition evaluation, exhibition, publication and publicity, with credit. This does not automatically include adaptation, implementation or unrelated commercial use. Stage 1 ideas are for selection only; public display requires the author’s consent.',50,359,742,10.5)
para('The organiser may invite the winning team to discuss a further design commission. Scope, fees and rights to adapt or implement the work will be agreed separately. Winning does not itself create a further appointment. Honoraria and awards will not be deducted from separately agreed fees for subsequent services.',50,455,742,10.5)
#30
base('APPENDIX · SITE INFORMATION','Site information')
table(['Information','Use and limitations'],[
['Boundary and early works','A common set of spatial files and accuracy notes. Competition area: approximately 1,656 km²; fixed pilots: agrivoltaics 13.9 km² and a living quarter 2.48 km².'],
['Location and imagery','Regional context, satellite imagery and roads. Credit imagery sources and distinguish a multi-date mosaic from a site survey.'],
['Terrain and hydrology','Elevation, slope, seasonal drainage, flood sensitivity and preliminary suitability screening, with methods and limitations.'],
['Systems and references','Indicative system locations, agrivoltaic concepts and POD images. Reference concepts do not establish fixed locations or verified performance.'],
['Versions and assumptions','Identify the version and source of information used. Record uncertainty and unconfirmed resource conditions, with their implications.']],[165,577],y=145,size=10.5,minh=66)
para('Site information, answers and amendments will be issued through a common channel. Maps do not replace cadastral, water-rights, hydrological or specialist verification. Gaps in organiser-supplied information are not, in themselves, grounds for marking down an applicant or proposal.',50,514,742,8.5,GRAY)
#31
base('CONTACT','Contact')
txt('XCITY',50,193,32,INK);txt('International Masterplanning and Urban Design Competition',50,254,17)
para('Online applications are open on the official practice page. Apply there and return the emailed qualification application form with supporting materials. All applicants follow the same application requirements, eligibility review and selection criteria. Common documents, clarifications and notices are issued through the official competition channels. Contact the competition team below for questions.',50,325,650,12)
para('Online application: xcityus.github.io/xcity-ai-competition/practice.html#apply',50,414,742,10)
c.linkURL('https://xcityus.github.io/xcity-ai-competition/practice.html#apply',(50,H-434,792,H-412))
txt('Email:',50,465,10,GRAY);txt('competition@xcity.ai',83,463,12,INK);c.linkURL('mailto:competition@xcity.ai',(83,H-460,333,H-440))
c.save()
r=PdfReader(OUT);full='\n'.join(p.extract_text() or '' for p in r.pages)
assert len(r.pages)==31,len(r.pages)
assert not re.search('[\u4e00-\u9fff]',full),'Chinese text remains in English PDF'
for value in ['US$300,000','US$50,000','US$100,000','competition@xcity.ai','up to 10 pages','emailed form']:assert value in full,value
for value in ['US$75,000','parcel 9','parcel 13','TBC','TBD']:assert value not in full,value
(O/'validation-english.json').write_text(json.dumps({'pages':31,'paragraph_boxes_checked':len(checks),'chinese_text_characters':0,'native_pdf_text':True,'site_area_km2':1656,'stage_1_pages':10,'shortlisted_teams':5,'honorarium_usd':50000,'winner_additional_usd':50000,'total_usd':300000},indent=2))
print(OUT)
