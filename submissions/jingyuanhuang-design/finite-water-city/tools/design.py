"""Original reproducible geometry. Run from repository root."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import shape,mapping,box,LineString,Point
from shapely.ops import transform,unary_union,nearest_points
from pyproj import Transformer
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parents[1];S=R/'brief/site-package'
t=Transformer.from_crs(4326,32719,always_xy=True).transform;inv=Transformer.from_crs(32719,4326,always_xy=True).transform
load=lambda f:unary_union([transform(t,shape(x['geometry'])) for x in json.loads((S/f).read_text())['features']])
scope=load('boundaries/scope_9_13.geojson');pilot=load('pilot-area/pilot_area.geojson');flood=load('water/flood_sensitive_dem.geojson');channels=load('water/channels_dem.geojson')
def poly(g):
 if g.geom_type in ('Polygon','MultiPolygon'):return g
 return unary_union([q for q in g.geoms if q.geom_type in ('Polygon','MultiPolygon')])
def ft(g,**p):return dict(type='Feature',geometry=mapping(transform(inv,g)),properties=p)
def write(n,fs):(P/'geometry'/f'{n}.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=fs)))
def ll(x,y):return list(inv(x,y))
master=box(571500,6552000,575500,6555000);assert scope.contains(master)
write('master_area',[ft(master,name='Agua Finita / first watershed settlement')])
land=[];remaining=master
zones=[(master.intersection(flood.buffer(100)),'open_space','Seasonal wash / no permanent construction'),(box(573100,6552100,574700,6552750),'compute','Dry compute and heat workshops'),(box(573100,6552750,575300,6553050),'industry','Repair, drying and water services'),(box(573100,6553150,574250,6554150),'residential','Patio neighbourhoods'),(box(574250,6553150,574700,6554150),'civic','Shade commons / school / clinic'),(box(573100,6554250,574700,6554800),'agriculture','Drip nursery and field trials'),(box(574800,6553200,575400,6554800),'energy','PV and storage precinct')]
for g,u,n in zones:
 q=poly(g.intersection(remaining))
 if not q.is_empty:land.append(ft(q,use=u,name=n));remaining=remaining.difference(q)
land.append(ft(poly(remaining),use='open_space',name='Unirrigated desert commons and circulation'));
for f in land:
 if f['properties']['use'] in ['open_space','civic','residential']:f['properties']['name']='Hard mineral ground / '+f['properties']['name']
write('land_use',land)
dem=np.array(Image.open(S/'terrain/dem_9_13_utm19s_60m.png')).astype(float);gy,gx=np.gradient(dem,60);slope=np.hypot(gx,gy)*100
buildings=[];screen=[]
def building(x,y,w,h,use,floors,name,**extra):
 g=box(x,y,x+w,y+h)
 if not master.contains(g) or g.intersects(flood.buffer(30)) or g.intersects(channels.buffer(150)) or g.intersects(pilot):return False
 row=int((6608973.7-y-h/2)/60);col=int((x+w/2-559572.4)/60)
 screen.append(dict(name=name,elevation_m=float(dem[row,col]),cell_slope_pct=float(slope[row,col])))
 buildings.append(ft(g,use=use,floors=floors,name=name,**extra));return True
for i in range(8):
 for j in range(6):
  for dy in [0,48]:building(573450+i*100,6553200+j*150+dy,42,16,'residential',3,f'Patio {i+1}-{j+1}-{dy//48+1}',dwellings=10,height_m=10.5)
for i in range(8):building(573150+i*130,6553290,78,8,'civic',1,'Neighbourhood shade arcade',form='canopy',height_m=4.5)
for i in range(3):building(573350+i*300,6552230,180,75,'compute',1,f'Compute hall {i+1}',height_m=9)
for i in range(4):building(573200+i*280,6552820,150,50,'industry',1,f'Repair and drying workshop {i+1}',height_m=7)
for x,y,w,h,n in [(574300,6553240,85,45,'Primary school'),(574450,6553240,70,40,'Clinic and care'),(574300,6553510,80,40,'Public kitchen and market'),(574470,6553510,80,40,'Library and audit room'),(574300,6553830,110,50,'Training and community hall'),(574480,6553830,65,40,'Night cafe and shelter')]:building(x,y,w,h,'civic',2,n,height_m=7)
for x,y,w,h in [(574285,6553590,270,12),(574285,6553730,270,12),(574285,6553602,12,128),(574543,6553602,12,128)]:building(x,y,w,h,'civic',1,'Shade commons roof',form='canopy',height_m=5)
building(573150,6554440,80,30,'civic',1,'Wash observatory / water classroom',height_m=4.5);write('buildings',buildings)
people=[LineString([(573050,y),(574750,y)]) for y in [6553100,6554200]]+[LineString([(x,6553050),(x,6554300)]) for x in [573100,573620,574140,574650]]
people +=[LineString([(574140,6553650),(574650,6553650)]),LineString([(573620,6554300),(573200,6554500),(572500,6554500),(572250,6554700)]),LineString([(573100,6553100),(573100,6552600),(574600,6552600)])]
machine=[LineString([(574750,6552050),(574750,6554900)]),LineString([(573000,6552750),(575350,6552750)]),LineString([(573000,6553050),(574750,6553050)]),LineString([(573000,6552050),(573000,6553050)]),LineString([(571550,6554900),(574750,6554900)])]
entry=nearest_points(scope.boundary,Point(571550,6554900))[0];access=LineString([entry,(571550,6554900)])
if scope.buffer(.01).covers(access):machine.append(access)
mov=[ft(g,network='people',shaded=(i!=7),name='Seasonal dry-wash trail' if i==7 else 'Shaded public route') for i,g in enumerate(people)]+[ft(g,network='machine',shaded=False,name='Service / emergency access',width_m=8) for g in machine]
pts=[]
for a in people:
 for b in machine:
  q=a.intersection(b)
  if q.is_empty:continue
  for z in list(q.geoms) if hasattr(q,'geoms') else [q]:
   if z.geom_type=='Point' and all(z.distance(v)>.1 for v in pts):pts.append(z)
for i,q in enumerate(pts):mov.append(ft(q,kind='interface',name=f'Gated crossing {i+1}',control='Pedestrian priority; locked gates; manual refuge release'))
write('movement',mov)
# Continuous built shade roofs for the designated shaded public network.
for i,line in enumerate(people):
 if i==7:continue
 roof=poly(line.buffer(2,cap_style=2).intersection(master).difference(flood.buffer(30)))
 if not roof.is_empty:buildings.append(ft(roof,use='civic',floors=1,name='Continuous public shade roof',form='canopy',height_m=4.5))
write('buildings',buildings)
nd=[('N05',box(573150,6552150,574500,6553000),'Heat without thirst','Dry cooling and cooperative herb drying share a metered heat loop',(573550,6552520),(573650,6552300)),('N07',box(571850,6554100,573350,6554850),'The absent river','Dry channel stays open and paths retreat to high ground',(573150,6554480),(572200,6554500)),('N10',box(574250,6553450,574620,6553800),'The right to shade','Public kitchen and library make a commons without ornamental water',(574420,6553660),(574480,6553510))]
nodes=[]
for nid,g,n,why,eye,target in nd:
 x0,y0,x1,y1=g.bounds;cx=(x0+x1)/2;cy=(y0+y1)/2
 nodes.append(ft(g,node_id=nid,name=n,why=why,eye_from=ll(*eye),eye_to=ll(*target),aerial_from=ll(x1+300,y0-400),section=[ll(x0,cy),ll(x1,cy)],section_b=[ll(cx,y0),ll(cx,y1)],render_note='Mineral plaster, pale aggregate, dry gravel, deep shade, accessible paths. No lawns, canals or lush forest. Children, elders and shift workers use the public spaces.',day=[dict(time='06:00',people='Morning market and shaded walk',machines='Freight remains in service yard'),dict(time='14:00',people='Cooled refuge opens; wash closes on flood warning',machines='Flexible compute sheds load'),dict(time='21:00',people='Kitchen and sheltered paths remain open',machines='Deliveries transfer at gates')]))
write('nodes',nodes)
parts={k:[] for k in ['reserve','agri_production','energy_compute']}
for x in range(562000,630001,2000):
 for y in range(6544000,6606001,2000):
  cell=box(x,y,x+2000,y+2000).intersection(scope)
  if cell.is_empty:continue
  row=max(0,min(dem.shape[0]-1,int((6608973.7-y-1000)/60)));col=max(0,min(dem.shape[1]-1,int((x+1000-559572.4)/60)))
  k='reserve' if slope[row,col]>5 or dem[row,col]>850 else ('energy_compute' if 580000<x<600000 and y>6570000 else 'agri_production');parts[k].append(cell)
remaining=scope;sf=[];future2=box(574000,6580000,576500,6582500).intersection(scope);future3=box(610000,6573000,612500,6575500).intersection(scope);port=box(620800,6560200,622200,6562200).intersection(scope);ind=box(621000,6557200,622400,6559200).intersection(scope)
for g,k,n in [(pilot,'agri_production','Fixed pilot / unchanged'),(flood.buffer(150).intersection(scope),'reserve','DEM wash corridors'),(master,'living','First settlement'),(future2,'living','Second settlement reservation'),(future3,'living','Third settlement reservation'),(port,'port','Conditional eastern gateway'),(ind,'industry','Conditional eastern industry')]:
 q=poly(g.intersection(remaining))
 if not q.is_empty:sf.append(ft(q,system=k,name=n));remaining=remaining.difference(q)
for k,gs in parts.items():
 q=poly(unary_union(gs).intersection(remaining))
 if not q.is_empty:sf.append(ft(q,system=k,name='Terrain-screened '+k+' reservation'));remaining=remaining.difference(q)
write('structure',sf)
write('phasing',[ft(master,phase=1,name='Complete first settlement'),ft(future2,phase=2,name='Second settlement',trigger='12 months audited water headroom 20%; 80% occupancy; school and clinic funded'),ft(poly(unary_union([future3,port,ind])),phase=3,name='Third settlement and gateway',trigger='Flood and access studies accepted; binding export demand; water reserve retained; approvals obtained')])
(P/'tools/terrain_screen.json').write_text(json.dumps(dict(method='60m DEM centre-cell slope screening; survey needed',buildings=screen),indent=2))
print('Buildings',len(buildings),'residential',sum(b['properties']['use']=='residential' for b in buildings),'interfaces',len(pts),'master',master.area/1e6,'entry',ll(entry.x,entry.y))
