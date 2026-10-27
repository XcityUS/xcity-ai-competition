"""Explicit proposed agrivoltaic crops; no alteration to protected pilot interiors."""
exec((__import__('pathlib').Path(__file__).parent/'operating_revision_v2.py').read_text().split("b=load(G/'buildings.geojson')")[0])
import hashlib
assets=load(G/'assets.geojson');crops=[];drip=[]
for g,p in assets:
 if p.get('type')!='pv_row':continue
 p.update(panel_width_m=4,centre_height_m=3.8,fixed_tilt_degrees=20,minimum_edge_clearance_m=3.1,trial_status='Proposed cultivated stage, gated by lawful water, soil and electrical safety tests')
 i=sum(1 for _,v in crops if v['field']==('C02' if p['id'].startswith('F-PV') else 'MAIN'))
 field='C02' if p['id'].startswith('F-PV') else 'MAIN';species='forage' if i%2==0 else 'jojoba';x0,y0,x1,y1=g.bounds;y=g.centroid.y
 crop=box(x0,y-1,x1,y+1)
 crops.append((crop,dict(id='CROP-'+p['id'],field=field,species=species,phase=1,band_width_m=2,pruned_height_m=1.2 if species=='jojoba' else .35,status='Proposed planted stage; not existing or authorised abstraction',annual_irrigation_m3_ha_assumed=4000 if species=='forage' else 2000,male_female_trial_ratio='1:8 provisional, seasonal wind trial required' if species=='jojoba' else 'not applicable')))
 drip.append((LineString([(x0,y),(x1,y)]),dict(id='DRIP-'+p['id'],type='irrigation_lateral',phase=1,isolation='Field meter and shutoff valve; separate from electrical service trenches',status='proposed')))
assets=[(g,p) for g,p in assets if p.get('type')!='irrigation_lateral']+drip
write(G/'assets.geojson',assets);write(G/'crops.geojson',crops)
area={s:sum(g.area for g,p in crops if p['species']==s)/10000 for s in ['forage','jojoba']};water=area['forage']*4000+area['jojoba']*2000
rec=dict(crop_area_ha=area,total_crop_area_ha=sum(area.values()),annual_irrigation_m3_assumed=water,irrigation_allowance_m3_ha_y=dict(forage=4000,jojoba=2000),dimensions='2m crop bands;4m fixed-tilt panels at3.8m centre /3.1m minimum edge;18m C02 /20m main row pitch;100m C02 end headlands;1.2m pruned jojoba;2.6m high x2.5m wide service vehicle, all assumed',pollination='Jojoba wind pollination: provisional1:8 male:female trial, distributed along rows and both ends; refine with seasonal wind and flowering observations; no bee dependence.',water_gate='No planting or occupied-stage approval before lawful supply and soil trial. No commercial yield credited. Account includes new fields only; protected pilot demand additional unknown.',planting_map='geometry/crops.geojson')
(O/'agriculture-account.json').write_text(json.dumps(rec,indent=2))
r=json.loads((O/'operational-conditions.json').read_text());r['farm'].update(planting_status=rec['water_gate'],crop_account=rec,main_row_pitch_m=20);(O/'operational-conditions.json').write_text(json.dumps(r,indent=2))
a=json.loads((P/'assumptions.json').read_text());a['assumptions']=[v for v in a['assumptions'] if v['id']!='V2-AGRICULTURE'];a['assumptions'].append(dict(id='V2-AGRICULTURE',topic='Agrivoltaic crop and water scenario',value=json.dumps(rec),basis='Entrant assumptions implementing confirmed forage/jojoba programme; agronomic demand, yield, seasonal wind, safety and lawful water require verification.'));(P/'assumptions.json').write_text(json.dumps(a,indent=2))
print(rec)
