#!/usr/bin/env python3
"""Fetch an unlabelled public Esri basemap and draw the current issued site geometry.
No old annotated screenshot is reused. API input bbox is WGS84; the returned image
extent is Web Mercator and is used for the exact same projection of the overlay.
The imagery is a multi-date mosaic, never a source for cadastral surveying.
"""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
import json,io,textwrap
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform
O=Path(__file__).resolve().parent;R=O.parents[1];B=R/'brief/site-package/boundaries'
SERVICE='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer'
ACCESSED='2026-10-27'
def get_json(url):
 with urlopen(url,timeout=60) as response:return json.load(response)
info=get_json(SERVICE+'?f=pjson')
assert 'Map' in info.get('capabilities',''),'Public service does not support export'
credit=info.get('copyrightText') or 'Source: Esri and the GIS User Community'
revision=json.loads((B/'boundary-revision.json').read_text())['revision']
geom=shape(json.loads((B/'scope_9_13.geojson').read_text())['features'][0]['geometry'])
project=Transformer.from_crs(4326,3857,always_xy=True).transform
site=transform(project,geom);west,south,east,north=geom.bounds
font_path='/System/Library/Fonts/Supplemental/Arial.ttf'
font=ImageFont.truetype(font_path,22);small=ImageFont.truetype(font_path,18)
metadata={'service':SERVICE,'copyright':credit,'accessed':ACCESSED,'boundary_revision':revision,'limitations':'Multi-date satellite mosaic; acquisition dates differ. Not a site survey or cadastral evidence. Outline generated from the current issued scope GeoJSON. No roads or infrastructure are invented.','images':[]}
for filename,bbox,size in [('satellite-region.jpg',[west-.55,south-.5,east+.4,north+.25],(1100,1200)),('satellite-site.jpg',[west-.045,south-.045,east+.045,north+.045],(1600,830))]:
 params={'bbox':','.join(map(str,bbox)),'bboxSR':4326,'imageSR':3857,'size':','.join(map(str,size)),'format':'jpg','f':'pjson'}
 export_url=SERVICE+'/export?'+urlencode(params);response=get_json(export_url)
 if 'error' in response:raise RuntimeError('Imagery export failed: '+str(response['error']))
 with urlopen(response['href'],timeout=60) as stream:image=Image.open(io.BytesIO(stream.read())).convert('RGB')
 extent=response['extent'];xmin,ymin,xmax,ymax=[extent[k] for k in ['xmin','ymin','xmax','ymax']]
 def pixel(pt):return ((pt[0]-xmin)/(xmax-xmin)*image.width,(ymax-pt[1])/(ymax-ymin)*image.height)
 draw=ImageDraw.Draw(image)
 for polygon in ([site] if site.geom_type=='Polygon' else site.geoms):
  points=[pixel(p) for p in polygon.exterior.coords];draw.line(points,fill='#231c0d',width=9,joint='curve');draw.line(points,fill='#ffda52',width=5,joint='curve')
 # Label only what is actually supplied; no invented road alignments or cities.
 title='Regional context — current site outline' if 'region' in filename else 'Current competition boundary'
 draw.rectangle((10,10,image.width-10,48),fill='#181a18');draw.text((22,17),title,font=font,fill='white')
 footer_lines=[*textwrap.wrap(credit,width=85 if image.width>1300 else 70),f'Accessed {ACCESSED} | multi-date mosaic, not a site survey',f'Boundary: {revision}']
 footer_height=24*len(footer_lines)+14
 output=Image.new('RGB',(image.width,image.height+footer_height),'#f7f5f0');output.paste(image,(0,0));fd=ImageDraw.Draw(output)
 for i,line in enumerate(footer_lines):fd.text((14,image.height+8+i*24),line,font=small,fill='#30302e')
 for language in ['en','zh']:
  destination=O/'assets'/language/filename;output.save(destination,quality=94,subsampling=0)
 metadata['images'].append({'file':filename,'input_bbox_wgs84':bbox,'output_image_extent':extent,'source_image_pixels':[image.width,image.height],'export_url':export_url})
 print('Updated',filename,'from unlabelled API imagery and current scope')
(O/'assets/imagery-source.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
