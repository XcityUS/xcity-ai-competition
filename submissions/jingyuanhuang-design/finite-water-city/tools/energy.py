"""Illustrative hourly dispatch, NOT a weather forecast or achieved performance."""
import math,csv,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
raw=[]
for h in range(8760):
 d=h//24;hr=h%24
 raw.append(max(0,math.sin(math.pi*(hr-6)/12))*(1+.22*math.cos(2*math.pi*(d-15)/365))*(.2 if d%60 in [0,1,2] else 1))
scale=40*.25*8760/sum(raw);soc=480;reserve=216/.95;rows=[]
for h,r in enumerate(raw):
 pv=r*scale;it=12 if 6<=h%24<18 else 6;load=it*1.25+2
 direct=min(load,pv);surplus=max(0,pv-load);charge=min(surplus,75,(480-soc)/.95);soc+=charge*.95
 discharge=min(max(0,load-direct),75,max(0,soc-reserve)*.95);soc-=discharge/.95
 grid=load-direct-discharge
 rows.append([h,round(pv,6),it,load,round(soc,6),round(grid,6),round(surplus-charge,6)])
with (P/'tools/hourly_dispatch.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['hour','pv_mw','it_mw','load_mw','battery_mwh','grid_mw','curtailed_mw']);w.writerows(rows)
# Initial battery has no credited origin. Subtract entire possible starting usable energy conservatively.
load=sum(r[3] for r in rows);grid=sum(r[5] for r in rows);initial=(480-reserve)*.95
out=dict(hourly_cfe_match_pct=round(100*(load-grid-initial)/load,3),annual_load_mwh=load,annual_pv_mwh=round(sum(r[1] for r in rows),2),grid_mwh=round(grid,2),peak_grid_mw=max(r[5] for r in rows),it_mwh=sum(r[2] for r in rows),note='Assumed synthetic annual profile; initial storage energy excluded; physical solar+storage supply fraction, unmatched imports have zero CFE credit. Not a site climate simulation.')
(P/'tools/energy_result.json').write_text(json.dumps(out,indent=2));print(out)
