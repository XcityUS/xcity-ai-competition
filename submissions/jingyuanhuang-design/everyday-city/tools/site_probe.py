import json
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import shape,box
from shapely.ops import transform,unary_union
from pyproj import Transformer
R=Path(__file__).resolve().parents[4];S=R/'brief/site-package'
t=Transformer.from_crs(4326,32719,always_xy=True).transform
G=lambda f:unary_union([transform(t,shape(v['geometry'])) for v in json.loads((S/f).read_text())['features']])
scope=G('boundaries/scope_9_13.geojson');pilot=G('pilot-area/pilot_area.geojson');living=G('pilot-area/pilot_living_area.geojson');flood=G('water/flood_sensitive_dem.geojson');channels=G('water/channels_dem.geojson')
dem=np.array(Image.open(S/'terrain/dem_9_13_utm19s_60m.png')).astype(float);dy,dx=np.gradient(dem,60);slope=np.hypot(dx,dy)*100
flood=flood.intersection(box(569000,6550000,581000,6562000)).simplify(3);scope=scope.simplify(1);channels=channels.intersection(box(569000,6550000,581000,6562000));rows=[]
for x in range(570000,577001,500):
 for y in range(6551500,6559501,500):
  g=box(x,y,x+1900,y+1400)
  if not scope.covers(g) or g.intersects(pilot.buffer(100)) or g.intersects(living.buffer(100)) or g.intersects(channels.buffer(150)):continue
  r0=int((6608973.7-y-1400)/60);r1=int((6608973.7-y)/60);c0=int((x-559572.4)/60);c1=int((x+1900-559572.4)/60)
  mean=float(slope[r0:r1,c0:c1].mean());wet=g.intersection(flood).area/g.area
  rows.append((wet*100+mean+g.distance(pilot)/3000,x,y,round(wet,3),round(mean,2),round(g.distance(pilot))))
print(sorted(rows)[:15])
