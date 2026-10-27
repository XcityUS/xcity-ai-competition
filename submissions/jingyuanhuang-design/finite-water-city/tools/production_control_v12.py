import runpy
from pathlib import Path
import matplotlib.pyplot as plt
from shapely.geometry import box
P=Path(__file__).resolve().parents[1];v=runpy.run_path(str(P/'tools/overall_axon_v12.py'));f=plt.figure(figsize=(16,12),facecolor='#D8D0BA');a=f.add_axes([.02,.02,.96,.96]);clip=box(573050,6552000,574800,6554800)
for g,p in v['v']['land']:
 q=g.intersection(clip)
 if not q.is_empty:v['shape'](a,q,v['v']['C'].get(p['use'],'#D8D4C3'),flat=True)
for g,p in v['M']:
 q=g.intersection(clip)
 if not q.is_empty:v['line'](a,q,'#9CABA0',3,True)
for g,p in v['assets']:
 q=g.intersection(clip)
 if not q.is_empty:
  if p['type']=='pv_row':v['line'](a,q,'#375E69',1.1,True)
  elif p['type']=='pv_field':v['shape'](a,q,'#BAC18A',flat=True,edge='#9E8B3C')
for g,p in v['plant']:v['shape'](a,g,'#8FA78E',flat=True)
for g,p in sorted(v['B'],key=lambda t:t[0].centroid.y,reverse=True):
 if clip.covers(g):v['hall'](a,g,p,True)
a.autoscale();a.set_aspect('equal');a.axis('off');f.savefig(v['O']/'production-aerial-control.png',dpi=140,facecolor='#D8D0BA');plt.close(f)
