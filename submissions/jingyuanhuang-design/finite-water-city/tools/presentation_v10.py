"""V10 geometry-linked presentation assets; render controls before image editing."""
import json,sys,shutil,math,hashlib
from pathlib import Path
from shapely.geometry import shape,mapping,box,LineString,Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];V9=P/'reviews/complete-city-v9';O=P/'reviews/presentation-v10';SC=O/'scene';G=SC/'geometry'
for d in [O,G,O/'controls',O/'media']:d.mkdir(parents=True,exist_ok=True)
T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
ll=lambda xy:list(I(*xy))
for p in (V9/'geometry').glob('*.geojson'):shutil.copy2(p,G/p.name)
def feature(g,p):return dict(type='Feature',geometry=mapping(transform(I,g)),properties=p)
def read(name):return json.loads((G/name).read_text())
def write(name,d):(G/name).write_text(json.dumps(d,separators=(',',':'))+'\n')
b=read('buildings.geojson');m=read('movement.geojson');land=read('land_use.geojson')
def canopy(x,y,w,h,nid,phase):
 b['features'].append(feature(box(x,y,x+w,y+h),dict(id=nid,use='civic',floors=1,form='canopy',height_m=4.5,phase=phase,name=nid,capacity_basis='Unoccupied open shade structure; no additional homes or jobs')))
canopy(574040,6556165,70,6,'A03-south-shade',1);canopy(574040,6556229,70,6,'A03-north-shade',1)
canopy(573460,6552578,280,6,'B03-worker-walk-shade',1)
# Removable shade on the eastern bank; no occupied building within the source channel screen.
canopy(572960,6557150,40,6,'C03-removable-edge-shade',2)
for ln,nid,ph in [(LineString([(573420,6552588),(573780,6552588)]),'B03-separated-worker-path',1),(LineString([(573500,6557160),(573030,6557160),(573030,6557300),(572980,6557300),(572980,6557160)]),'C03-edge-path',2)]:
 m['features'].append(feature(ln,dict(id=nid,network='people',width_m=4,shaded=False,phase=ph,name=nid)))
# Source-based visitor edge uses dry mineral paving; no water, forest, or new homes.
land['features'].append(feature(box(572948,6557138,573015,6557178),dict(id='C03-viewing-apron',use='public_commons',name='Removable dry viewing apron',phase=2)))
write('buildings.geojson',b);write('movement.geojson',m);write('land_use.geojson',land)
nodes=read('nodes.geojson')
for f in nodes['features']:
 p=f['properties'];nid=p['node_id']
 p['official_topic']={'A03':'Public space in heat and Zonda wind','B03':'A compute campus and its waste heat','C03':'A seasonal river park'}[nid]
 p.update({'A03':dict(eye_from=ll((574054,6556181)),eye_to=ll((574088,6556248))), 'B03':dict(eye_from=ll((573695,6552589)),eye_to=ll((573570,6552440))), 'C03':dict(eye_from=ll((572983,6557165)),eye_to=ll((572795,6557135)))}[nid])
write('nodes.geojson',nodes)
# Render extent is a local camera study, not a redefinition of the V9 design scope.
local=box(572000,6551500,576500,6559500)
write('master_area.geojson',dict(type='FeatureCollection',features=[feature(local,dict(name='Southwest scene extent only; full-site and N/E geometry retained separately'))]))
(SC/'manifest.json').write_text(json.dumps(dict(title='AGUA FINITA / V10 camera controls',scene_seed=910,scene_generation=dict(procedural_vegetation=False,procedural_pv=False,illustrative_entourage=False))))
# Remove zero-area clipping debris; preserve every polygonal area.
def polygonal(g):
 if g.geom_type in ['Polygon','MultiPolygon']:return g
 return unary_union([polygonal(q) for q in getattr(g,'geoms',[]) if not polygonal(q).is_empty])
for name in ['structure','land_use','phasing','movement']:
 d=read(name+'.geojson');clean=[]
 for f in d['features']:
  g=shape(f['geometry'])
  if name!='movement':g=polygonal(g)
  if g.is_empty:continue
  f['geometry']=mapping(g);clean.append(f)
 d['features']=clean;write(name+'.geojson',d)
sys.path.insert(0,str(R/'scripts'));import make_scene as ms;import xcity_common as xc
class Controlled(ms.Scene):
 def views(self):
  specs=[('city-core-aerial',(575450,6555500,700),(574600,6556850,0),50,'Southwest city / central and southern precincts / local aerial'),('city-overall',(579300,6550100,6200),(574300,6555500,0),42,'Southwest complete city + independent productive system'),('A03-aerial',(574360,6555880,300),(574075,6556200,0),43,'A03 market commons'),('A03-eye',(574054,6556181,1.6),(574088,6556248,2),62,'A03 public life'),('B03-aerial',(574500,6551600,900),(573850,6552500,0),44,'B03 eight compute halls and repair'),('B03-eye',(573695,6552589,1.6),(573570,6552440,3),62,'B03 protected worker approach'),('C03-aerial',(573440,6556650,650),(572950,6557210,0),44,'C03 eastern visitor edge and source seasonal wash'),('C03-eye',(572983,6557165,1.6),(572795,6557135,0),62,'C03 dry wash visitor edge')]
  views=[];records=[]
  for vid,pos,target,fov,title in specs:
   views.append(dict(id=vid,label=title,time='day',fov=fov,pos=[*self.L(*pos[:2]),pos[2]],target=[*self.L(*target[:2]),target[2]],shadow_radius=450 if 'eye' in vid else 4500))
   records.append(dict(id=vid,position_utm19s=pos,target_utm19s=target,fov_degrees=fov,aspect_ratio=1.6,eye_height_above_terrain_m=pos[2] if 'eye' in vid else None,phase='Hypothetical full build-out' if vid in ['city-overall','city-core-aerial'] else ('Phase 2' if vid.startswith('C03') else 'Phase 1 node structure shown at full design extent'),label=title,scope='Southwestern built settlement; not full competition territory' if vid=='city-overall' else ('Central and southern urban precincts; local aerial crop, not whole site' if vid=='city-core-aerial' else 'Node camera crop'),geometry_source='scene/geometry/',control_image='controls/'+vid+'.png'))
  for r in records:
   if r['id'].startswith('B03'):r['phase']='P1-P3 full build-out; halls are staged 2 / 4 / 8 MW'
   elif r['id'].startswith('A03'):r['phase']='Phase 1 node core with full-build-out urban context'
   elif r['id']=='city-core-aerial':r['status']='rejected_trial_not_used_in_presentation'
  (O/'camera-registry.json').write_text(json.dumps(records,indent=2)+'\n');return views
sc=Controlled(str(SC));sc.near=local.buffer(800);data=sc.build()
# Explicitly sourced V9 module rows, not automatic solar generation.
a=json.loads((V9/'geometry/assets.geojson').read_text())
data['pv_rows']=[]
for f in a['features']:
 if f['properties'].get('type')=='pv_row':
  g=transform(T,shape(f['geometry']));c=g.centroid;data['pv_rows'].append([*sc.L(c.x,c.y),g.length])
# Preserve site source terrain and camera geometry. An AI finish may change materials and light only.
data['input_sha256']=xc.scene_input_hash(str(SC));(SC/'visual').mkdir(exist_ok=True)
renderer=(R/'scripts/scene/scene.js').read_text()
renderer=renderer.replace("(b.form === 'canopy' ? hs.reduce((a, c) => a + c, 0) / hs.length : Math.min(...hs))",'Math.max(...hs)')
renderer=renderer.replace('new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 0, 1), tilt)','new T.Quaternion().setFromEuler(new T.Euler(-tilt, Math.PI / 2, 0))')
renderer=renderer.replace('color: 0xf7f0e2','color: 0xb5a693')
(O/'renderer-v10.js').write_text(renderer)
doc=ms.page(sc.man['title'],data).replace((R/'scripts/scene/scene.js').read_text(),renderer)
(SC/'visual/index.html').write_text(doc)
(O/'scene-fingerprint.json').write_text(json.dumps(dict(input_sha256=data['input_sha256'],renderer_sha256=hashlib.sha256(renderer.encode()).hexdigest(),rendering_assumption='Building platforms referenced to maximum sampled corner elevation to prevent clipping; grading/plinths are conceptual and require civil design. Explicit PV rows follow source east-west alignments.',scene_policy='No procedural vegetation, PV or entourage; PV rows are explicit V9 assets. Four new open canopies and two pedestrian links are declared V10 details; capacity unchanged.'),indent=2))
print('SCENE',O)
