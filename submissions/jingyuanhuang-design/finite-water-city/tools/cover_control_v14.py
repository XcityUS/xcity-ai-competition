"""Native geometry control for the whole-territory aerial cover."""
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=(P/'tools/overall_axon_v12.py').read_text()
pre=s.split('f=plt.figure')[0]
exec(compile(pre,str(P/'tools/overall_axon_v12.py'),'exec'))
O=P/'reviews/cover-v14';O.mkdir(exist_ok=True)
f=plt.figure(figsize=(16,10),facecolor='#E4DDC9');a=f.add_axes([.025,.025,.95,.95])
body=s.split('a=f.add_axes',1)[1].split('b=f.add_axes',1)[0]
body=body[body.index('tiles=[]'):]
body=body.split('for g,p in v[\'regions\']:\n c=g.representative_point()')[0]
exec(compile(body,'native-territorial-control','exec'))
a.autoscale();a.set_aspect('equal');a.axis('off')
f.savefig(O/'whole-territory-control.png',dpi=160,facecolor=f.get_facecolor());plt.close(f)
print(O/'whole-territory-control.png')
