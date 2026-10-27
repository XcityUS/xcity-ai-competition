import sys,json,hashlib,shutil
from pathlib import Path
from shapely.geometry import box,shape,mapping
from shapely.ops import transform
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/redesign-v2';T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
sys.path.insert(0,str(R/'scripts'));import make_scene as ms;import xcity_common as xc
m=json.loads((P/'manifest.json').read_text());m['scene_generation']=dict(procedural_vegetation=False,procedural_pv=False,illustrative_entourage=False);m['scene_seed']=20261027;(P/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
a=next(transform(T,shape(f['geometry'])).centroid for f in json.loads((P/'geometry/nodes.geojson').read_text())['features'] if f['properties']['node_id']=='A01');ax,ay=a.coords[0]
class Controlled(ms.Scene):
 def views(self):
  specs=[('city-overall',(572100,6550500,2300),(574100,6553000,0),52,'Complete southwest settlement system / full build-out'),('city-centre',(575600,6554300,1050),(574500,6555470,0),48,'Town civic band and living districts / local aerial'),('A01-aerial',(ax+220,ay-240,260),(ax,ay,0),46,'A01 open-court housing / local aerial'),('A01-eye',(ax-28,ay-30,1.7),(ax+8,ay+50,2),63,'A01 shared court / eye-level'),('B03-aerial',(574950,6552000,580),(574340,6552460,0),44,'B03 four modular industrial halls and repair / local aerial'),('B03-eye',(574340,6552373,1.7),(574210,6552390,3),64,'B03 protected worker spine / eye-level'),('C02-aerial',(574000,6550800,750),(573400,6551300,0),45,'C02 new trial field and learning edge / local aerial'),('C02-eye',(573410,6551330,1.7),(573290,6551200,2),63,'C02 public shade edge facing new trial rows / eye-level')]
  views=[];records=[]
  for id,pos,tar,fov,label in specs:
   views.append(dict(id=id,label=label,time='day',fov=fov,pos=[*self.L(*pos[:2]),pos[2]],target=[*self.L(*tar[:2]),tar[2]],shadow_radius=500 if 'eye' in id else 5000))
   records.append(dict(id=id,position_utm19s=pos,target_utm19s=tar,fov_degrees=fov,aspect_ratio=1.6,scope=label,phase='Full build-out scenario; node core enabled in Phase 1',control_image='renders/'+id+'.png',geometry_source='geometry/'))
  (O/'camera-registry.json').write_text(json.dumps(records,indent=2));return views
sc=Controlled(str(P));sc.near=box(572500,6550500,576500,6557200).buffer(500);data=sc.build();data['pv_rows']=[]
for f in json.loads((P/'geometry/assets.geojson').read_text())['features']:
 if f['properties'].get('type')!='pv_row':continue
 g=transform(T,shape(f['geometry']));p=g.centroid;data['pv_rows'].append([*sc.L(p.x,p.y),g.length,f['properties'].get('centre_height_m',1.7)])
data['crop_bands']=[];data['jojoba']=[]
for f in json.loads((P/'geometry/crops.geojson').read_text())['features']:
 g=transform(T,shape(f['geometry']));v=f['properties'];data['crop_bands'].append(dict(**ms.rings(g,sc.o),species=v['species']))
 if v['species']=='jojoba':
  x0,y0,x1,y1=g.bounds
  for x in range(int(x0)+5,int(x1)-4,5):data['jojoba'].append([*sc.L(x,g.centroid.y)])
data['input_sha256']=xc.scene_input_hash(str(P));raw=(R/'scripts/scene/scene.js').read_text();renderer=raw.replace("(b.form === 'canopy' ? hs.reduce((a, c) => a + c, 0) / hs.length : Math.min(...hs))",'Math.max(...hs)').replace('new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 0, 1), tilt)','new T.Quaternion().setFromEuler(new T.Euler(-tilt, Math.PI / 2, 0))').replace('color: 0xf7f0e2','color: 0xb5a693');renderer=renderer.replace('new T.BoxGeometry(2.3, 0.06, 1)','new T.BoxGeometry(4, 0.06, 1)').replace('hAt(r[0], r[1]) + 1.7','hAt(r[0], r[1]) + (r[3] || 1.7)').replace('new T.BoxGeometry(0.1, 1.6, 0.1)','new T.BoxGeometry(0.1, 1, 0.1)').replace('hAt(r[0], r[1]) + 0.8','hAt(r[0], r[1]) + (r[3] || 1.7) / 2').replace('s.set(1, 1, r[2]); }, false);','s.set(1, (r[3] || 1.7), r[2]); }, false);');renderer=renderer.replace('D.washes.forEach',"(D.crop_bands || []).forEach(gr => flat(gr, new T.MeshStandardMaterial({color: gr.species === 'forage' ? 0x7d9258 : 0x9a876a, roughness:1}), .10, 10));\n  D.washes.forEach")
renderer=renderer.replace('// trees: 0 broad',"instanced(new T.IcosahedronGeometry(1,1), new T.MeshStandardMaterial({color:0x77805b,roughness:1}), D.jojoba || [], (r,p,q,s)=>{p.set(r[0],hAt(r[0],r[1])+.6,-r[1]);q.identity();s.set(1,.6,1);});\n  // trees: 0 broad")
(O/'renderer.js').write_text(renderer);(P/'visual/index.html').write_text(ms.page('THE EVERYDAY CITY / V2',data).replace(raw,renderer));(O/'scene-fingerprint.json').write_text(json.dumps(dict(input_sha256=data['input_sha256'],renderer_sha256=hashlib.sha256(renderer.encode()).hexdigest(),assumptions='Maximum-corner conceptual building plinths; proposed forage/jojoba crop bands only in geometry/crops.geojson; no decorative water, lawn or implicit rooftop PV; irrigation rights unverified.'),indent=2));print('Generated V2 scene with',len(data.get('buildings',[])),'buildings')
