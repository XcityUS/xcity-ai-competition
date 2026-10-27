# -*- coding: utf-8 -*-
import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[2];data=Path(__file__).resolve().parent;countries=json.loads((data/'countries.geojson').read_text())['features'];provinces=json.loads((data/'argentina.json').read_text())['features'];site=json.loads((R/'brief/site-package/boundaries/scope_9_13.geojson').read_text())['features']
def transform(bounds,rect):
 x0,y0,x1,y1=bounds;x,y,w,h=rect
 return lambda a,b:(x+(a-x0)/(x1-x0)*w,y+h-(b-y0)/(y1-y0)*h)
def path(g,T):
 rings=g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p] if g['type']=='MultiPolygon' else []
 return ' '.join('M'+' L'.join('%.2f,%.2f'%T(*p[:2]) for p in ring)+' Z' for ring in rings)
for lang in ['en','zh']:
 T=transform((-84,-57,-33,14),(50,65,390,540));U=transform((-72.7,-34.3,-66,-27.8),(650,70,480,535));v=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 690"><defs><clipPath id="regional"><rect x="650" y="70" width="480" height="535"/></clipPath></defs><g font-family="Arial, sans-serif">']
 def label(x,y,s,size=15,c='#ddd8c8'):v.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{c}">{html.escape(s)}</text>')
 def draw(g,t,fill,stroke,width=.7):v.append(f'<path d="{path(g,t)}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" fill-rule="evenodd"/>')
 for f in countries:
  if f['properties'].get('CONTINENT')=='South America':draw(f['geometry'],T,'#958c75' if f['properties'].get('ADMIN')=='Argentina' else '#363936','#77776c')
 sj=next(f for f in provinces if 'San Juan' in f['properties'].get('name',''))
 draw(sj['geometry'],T,'#cfac5b','#edcc7b',1)
 a,b=T(-72.7,-34.3);c,d=T(-66,-27.8)
 v.append(f'<rect x="{a}" y="{d}" width="{c-a}" height="{b-d}" fill="none" stroke="#d1ad60" stroke-width="1.5"/>')
 v.append(f'<path d="M{c},{(b+d)/2} H620 m-8,-5 l8,5 -8,5" stroke="#b99b5b" fill="none" stroke-width="1.5"/>')
 v.append('<g clip-path="url(#regional)">')
 for f in countries:draw(f['geometry'],U,'#242a27','#6e7267',1)
 for f in provinces:draw(f['geometry'],U,'#5c5b48' if f is sj else '#303932','#80836f',1)
 for f in site:draw(f['geometry'],U,'#dfb75e','#ffe4a1',1.2)
 v.append('</g>')
 for lon,lat,name in [(-68.536,-31.537,'San Juan'),(-68.845,-32.89,'Mendoza'),(-70.669,-33.449,'Santiago'),(-71.343,-29.953,'Coquimbo')]:
  x,y=U(lon,lat);v.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#e8e2d0"/>');label(x+9,y+5,name,14)
 x,y=U(-68.19,-31.17);v.append(f'<path d="M{x+5},{y-12} V{y-53} H{x-55}" stroke="#e2bd6a" fill="none"/>');label(x-55,y-65,'XCITY 场地' if lang=='zh' else 'XCITY SITE',18,'#f2ce80')
 label(50,35,'南美洲 → 阿根廷' if lang=='zh' else 'SOUTH AMERICA → ARGENTINA',17)
 label(650,35,'圣胡安省及周边区域' if lang=='zh' else 'SAN JUAN AND THE SURROUNDING REGION',17)
 label(50,660,'区域定位示意 · 放大图比例不同' if lang=='zh' else 'REGIONAL ORIENTATION · SCALES DIFFER BETWEEN VIEWS',13,'#9a9d8c')
 v.append('</g></svg>');(R/f'media/home-regional-context-{lang}.svg').write_text('\n'.join(v))
p=R/'index.html';s=p.read_text();a=s.index('<div class="regional-maps">') if '<div class="regional-maps">' in s else s.index('<div class="regional-diagram">');b=s.index('<p class="regional-credit">',a)
s=s[:a]+'''<div class="regional-diagram"><img class="zh-only" src="media/home-regional-context-zh.svg?v=20261027-city-label" alt="从南美洲定位至圣胡安省的放大区位图，标出XCITY场地" loading="lazy"><img class="en-only" src="media/home-regional-context-en.svg?v=20261027-city-label" alt="Connected regional diagram from South America to San Juan, locating the XCITY site" loading="lazy"></div>'''+s[b:]

if '.regional-diagram{width:100%' not in s:s=s.replace('.regional-background{','.regional-diagram{width:100%;margin:24px 0}.regional-diagram img{width:100%;height:auto}.regional-background{',1)
p.write_text(s)
