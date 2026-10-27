import sys,json,hashlib,shutil
from pathlib import Path
from shapely.geometry import box,shape,mapping
from shapely.ops import transform
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/redesign-v2';T=Transformer.from_crs(4326,32719,always_xy=True).transform;I=Transformer.from_crs(32719,4326,always_xy=True).transform
sys.path.insert(0,str(R/'scripts'));import make_scene as ms;import xcity_common as xc
m=json.loads((P/'manifest.json').read_text())
extra_sources=['geometry/assets.geojson','geometry/crops.geojson','geometry/courtyard_details.geojson','geometry/interface_landscape.geojson','tools/scene_v2.py']
extra_hash=hashlib.sha256(b''.join((P/f).read_bytes() for f in extra_sources)).hexdigest()
m['render_note']=m.get('render_note','').split(' | explicit-geometry-sha256:')[0]+' | explicit-geometry-sha256:'+extra_hash
m['scene_generation']=dict(procedural_vegetation=False,procedural_pv=False,illustrative_entourage=False);m['scene_seed']=20261027;(P/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
a=next(transform(T,shape(f['geometry'])).centroid for f in json.loads((P/'geometry/nodes.geojson').read_text())['features'] if f['properties']['node_id']=='A01');ax,ay=a.coords[0]
class Controlled(ms.Scene):
 def views(self):
  specs=[('city-overall',(573000,6552900,1800),(574300,6554800,0),52,'Compact southwest town edge and productive landscape / partial local view / full-build-out scenario'),('city-centre',(575600,6554300,1050),(574500,6555470,0),48,'Town civic band and living districts / local aerial'),('A01-aerial',(ax+220,ay-240,260),(ax,ay,0),46,'A01 open-court housing / local aerial'),('A01-eye',(ax-28,ay-30,1.7),(ax+8,ay+50,2),63,'A01 shared court / eye-level'),('B03-aerial',(574950,6553050,580),(574340,6553510,0),44,'B03 four modular industrial halls and repair / local aerial'),('B03-eye',(574340,6553423,1.7),(574210,6553440,3),64,'B03 protected worker spine / eye-level'),('C02-aerial',(573740,6552070,340),(573430,6552340,0),46,'C02 close local aerial / central crop rows and workshop forecourts; field ends cropped'),('C02-eye',(573385,6552363,1.7),(573190,6552385,2),63,'C02 occupied shade promenade and connected workshop forecourt / eye-level')]
  views=[];records=[]
  for id,pos,tar,fov,label in specs:
   views.append(dict(id=id,label=label,time='day',fov=fov,pos=[*self.L(*pos[:2]),pos[2]],target=[*self.L(*tar[:2]),tar[2]],shadow_radius=500 if 'eye' in id else 5000))
   records.append(dict(id=id,position_utm19s=pos,target_utm19s=tar,fov_degrees=fov,aspect_ratio=1.6,scope=label,phase='Full build-out scenario; node core enabled in Phase 1',control_image='renders/'+id+'.png',geometry_source='geometry/'))
  whole=next(v for v in super().views() if v['id']=='whole-site-aerial');views.append(whole)
  (O/'camera-registry.json').write_text(json.dumps(records,indent=2));return views
sc=Controlled(str(P));sc.near=box(572500,6550500,576500,6557200).buffer(500);data=sc.build();data['pv_rows']=[];data['pv_posts']=[]
for f in json.loads((P/'geometry/assets.geojson').read_text())['features']:
 if f['properties'].get('type')!='pv_row':continue
 g=transform(T,shape(f['geometry']));p=g.centroid;data['pv_rows'].append([*sc.L(p.x,p.y),g.length,f['properties'].get('centre_height_m',1.7)])
for f in json.loads((P/'geometry/assets.geojson').read_text())['features']:
 if f['properties'].get('type')!='pv_row':continue
 g=transform(T,shape(f['geometry']))
 for dd in range(0,int(g.length)+1,20):
  q=g.interpolate(dd);data['pv_posts'].append([*sc.L(q.x,q.y),f['properties'].get('centre_height_m',3.8)])
data['crop_bands']=[];data['jojoba']=[]
for f in json.loads((P/'geometry/crops.geojson').read_text())['features']:
 g=transform(T,shape(f['geometry']));v=f['properties'];data['crop_bands'].append(dict(**ms.rings(g,sc.o),species=v['species']))
 if v['species']=='jojoba':
  x0,y0,x1,y1=g.bounds
  for x in range(int(x0)+5,int(x1)-4,5):data['jojoba'].append([*sc.L(x,g.centroid.y)])
data['court_surfaces']=[];data['court_fences']=[];data['court_benches']=[]
for f in json.loads((P/'geometry/courtyard_details.geojson').read_text())['features']:
 g=transform(T,shape(f['geometry']));data['court_surfaces'].append(dict(**ms.rings(g,sc.o),material=f['properties']['material']))
for f in json.loads((P/'geometry/assets.geojson').read_text())['features']:
 v=f['properties'];g=transform(T,shape(f['geometry']))
 if v.get('type')=='farm_public_fence':data['court_fences'].append([[*sc.L(x,y)] for x,y in g.coords])
 if v.get('type')=='bench':data['court_benches'].append([*sc.L(g.centroid.x,g.centroid.y),g.length])
data['input_sha256']=xc.scene_input_hash(str(P));raw=(R/'scripts/scene/scene.js').read_text();renderer=raw.replace("(b.form === 'canopy' ? hs.reduce((a, c) => a + c, 0) / hs.length : Math.min(...hs))",'Math.max(...hs)').replace('new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 0, 1), tilt)','new T.Quaternion().setFromEuler(new T.Euler(-tilt, Math.PI / 2, 0))').replace('color: 0xf7f0e2','color: 0xb5a693');renderer=renderer.replace('new T.BoxGeometry(2.3, 0.06, 1)','new T.BoxGeometry(4, 0.06, 1)').replace('hAt(r[0], r[1]) + 1.7','hAt(r[0], r[1]) + (r[3] || 1.7)').replace('new T.BoxGeometry(0.1, 1.6, 0.1)','new T.BoxGeometry(0.1, 1, 0.1)').replace('hAt(r[0], r[1]) + 0.8','hAt(r[0], r[1]) + (r[3] || 1.7) / 2').replace('s.set(1, 1, r[2]); }, false);','s.set(1, (r[3] || 1.7), r[2]); }, false);');renderer=renderer.replace('D.washes.forEach',"(D.crop_bands || []).forEach(gr => flat(gr, new T.MeshStandardMaterial({color: gr.species === 'forage' ? 0x7d9258 : 0x9a876a, roughness:1}), .10, 10));\n  D.washes.forEach")
renderer=renderer.replace('// trees: 0 broad',"instanced(new T.IcosahedronGeometry(1,1), new T.MeshStandardMaterial({color:0x77805b,roughness:1}), D.jojoba || [], (r,p,q,s)=>{p.set(r[0],hAt(r[0],r[1])+.6,-r[1]);q.identity();s.set(1,.6,1);});\n  // trees: 0 broad")
renderer=renderer.replace('D.washes.forEach',"(D.court_surfaces || []).forEach(gr => flat(gr, new T.MeshStandardMaterial({color:gr.material === 'mineral_pavers' ? 0xc7b99e : gr.material === 'stabilised_gravel' ? 0xa69b85 : 0xb19b7c,roughness:1}), .18, 10));\n  D.washes.forEach")
renderer=renderer.replace('// trees: 0 broad',"instanced(new T.BoxGeometry(1,.45,.6),new T.MeshStandardMaterial({color:0x91785e,roughness:1}),D.court_benches || [],(r,p,q,s)=>{p.set(r[0],hAt(r[0],r[1])+.225,-r[1]);q.identity();s.set(r[2],1,1);});\n  (D.court_fences || []).forEach(line=>{const pts=line.map(r=>new T.Vector3(r[0],hAt(r[0],r[1])+.9,-r[1]));scene.add(new T.Line(new T.BufferGeometry().setFromPoints(pts),new T.LineBasicMaterial({color:0x75674d})));});\n  // trees: 0 broad")
import re
renderer=re.sub(r'instanced\(new T.BoxGeometry\(0.1, 1, 0.1\), postMat, pvRows,.*?\}, false\);',"instanced(new T.CylinderGeometry(.08,.08,1,6),postMat,D.pv_posts || [],(r,p,q,s)=>{p.set(r[0],hAt(r[0],r[1])+r[2]/2,-r[1]);q.identity();s.set(1,r[2],1);},false);",renderer)
(O/'renderer.js').write_text(renderer);(P/'visual/index.html').write_text(ms.page('THE EVERYDAY CITY / V5',data).replace(raw,renderer));(O/'scene-fingerprint.json').write_text(json.dumps(dict(input_sha256=data['input_sha256'],renderer_sha256=hashlib.sha256(renderer.encode()).hexdigest(),assumptions='Maximum-corner conceptual building plinths; proposed forage/jojoba crop bands only in geometry/crops.geojson; no decorative water, lawn or implicit rooftop PV; irrigation rights unverified.'),indent=2));print('Generated V2 scene with',len(data.get('buildings',[])),'buildings')
