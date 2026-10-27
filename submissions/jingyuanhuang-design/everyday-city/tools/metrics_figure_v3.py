import json
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path('submissions/jingyuanhuang-design/everyday-city');m=json.loads((p/'metrics.json').read_text())['metrics'];f,a=plt.subplots(figsize=(12,10),facecolor='#F7F4EC');a.axis('off');rows=[[v['key'],str(v['value']),v['unit'],v['evidence']] for v in m if not isinstance(v['value'],dict)];t=a.table(cellText=rows,colLabels=['Metric / scope in metrics.json','Value','Unit','Evidence'],colWidths=[.44,.25,.13,.18],loc='center',cellLoc='left');t.auto_set_font_size(False);t.set_fontsize(7.5);t.scale(1,1.4)
for (r,c),v in t.get_celld().items():v.set_facecolor('#E5DCCB' if r==0 else '#F7F4EC');v.set_edgecolor('#D1CEC3');v.set_linewidth(.3)
a.set_title('EVERYDAY CITY V2 / CURRENT METRIC RECORD\nP1 metrics except explicitly named full-build-out quantities; not design approval',fontsize=13,color='#263F46',pad=20);f.savefig(p/'figures/fig-07-metrics.png',dpi=180,bbox_inches='tight');plt.close(f)
for name in ['everyday-city-design-review.pdf','everyday-city-technical-appendix.pdf']:
 src=p/'drawings'/name
 if src.exists():
  dest=p/'reviews/withdrawn-v1/drawings'/name;dest.parent.mkdir(parents=True,exist_ok=True);src.replace(dest)
print('Current metrics figure; obsolete duplicate PDFs archived')
