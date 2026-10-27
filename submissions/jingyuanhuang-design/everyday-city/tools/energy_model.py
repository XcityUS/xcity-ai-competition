import json,math,csv
from pathlib import Path
P=Path(__file__).resolve().parents[1];rows=[];soc=72/.95;total=clean=matched=gridtotal=0;peak=0
for h in range(8760):
 hour=h%24;day=h//24;it=8 if 7<=hour<19 else 4;load=it*1.3+(1.4 if 7<=hour<23 else .8);pv=20*max(0,math.sin(math.pi*(hour-6)/12))*(.8+.2*math.cos((day-15)*2*math.pi/365))*(.6 if day%45 in [0,1] else 1)
 direct=min(pv,load);surplus=max(0,pv-load);charge=min(surplus,30,(180-soc)/.95);soc+=charge*.95;need=load-direct;dis=min(need,30,max(0,soc-72/.95)*.95);soc-=dis/.95;grid=need-dis;assert grid<=20;total+=load;clean+=direct+dis;matched+=grid<1e-7;gridtotal+=grid;peak=max(peak,grid);rows.append([h,load,pv,soc,dis,grid])
with open(P/'report/hourly-energy.csv','w') as f:
 w=csv.writer(f);w.writerow(['hour','load_mw','pv_mw','battery_mwh','discharge_mw','grid_mw']);w.writerows(rows)
(P/'report/energy-results.json').write_text(json.dumps({'fully_matched_hours_pct':100*matched/8760,'clean_energy_share_pct':100*clean/total,'total_mwh':total,'grid_import_mwh':gridtotal,'peak_grid_mw':peak,'limits':'Synthetic hourly PV profile, not measured climate; starting battery at protected reserve, no clean credit from grid'},indent=2))
