#!/usr/bin/env python3
"""Reproduce the organiser-authorised internal seam closure; never buffer the external edge.
Optional export dependencies: pip install pyshp ezdxf. Original input is archived once.
"""
from pathlib import Path
import json, shutil, hashlib, zipfile, tempfile
import xml.etree.ElementTree as ET
from shapely.geometry import shape, mapping, Polygon, LineString
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, transform
from pyproj import Geod, Transformer, CRS
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'brief/site-package'; B=SITE/'boundaries'; VERSION='2026-10-27-open-seam-closure'
G=Geod(ellps='WGS84'); UTM=Transformer.from_crs(4326,32719,always_xy=True).transform
area=lambda g:abs(G.geometry_area_perimeter(g)[0])/1e6
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
archive=B/'archive/2026-10-26';archive.mkdir(parents=True,exist_ok=True)
for name in ['parcels_9_13.geojson','scope_9_13.geojson']:
 if not (archive/name).exists():shutil.copyfile(B/name,archive/name)
# Preserve the previously published v1.4.0 state before this corrective revision.
prior_archive=B/'archive/2026-10-27-v1.4.0'
if not prior_archive.exists():
 prior_archive.mkdir(parents=True)
 for item in B.iterdir():
  if item.name=='archive':continue
  if item.is_dir():shutil.copytree(item,prior_archive/item.name)
  elif item.is_file():shutil.copyfile(item,prior_archive/item.name)
 for rel in ['datapackage.json','areas.json','evidence-index.json','terrain/terrain_summary_9_13.json']:
  src=SITE/rel;dest=prior_archive/'site-package'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
original=json.loads((archive/'parcels_9_13.geojson').read_text()); a,b=[shape(f['geometry']) for f in original['features']]
u=unary_union([a,b]); assert u.geom_type=='Polygon'
# First close enclosed holes; the previous revision stopped here and missed an
# externally connected white seam. Close that specific mouth with the two issued
# upper tips, never with an indiscriminate buffer.
internal_closed=Polygon(u.exterior)
aa=list(a.exterior.coords);bb=list(b.exterior.coords)
join=LineString([aa[23],aa[24]]).intersection(LineString([bb[20],bb[21]]))
assert join.geom_type=='Point'
open_patch=Polygon([aa[22],aa[23],join.coords[0],bb[21]])
assert open_patch.is_valid and open_patch.area>0
combined=internal_closed.union(open_patch)
# GEOS can leave a zero-area ring at the exact intersection (3e-15 degree roundoff).
assert all(abs(Polygon(r).area)<1e-15 for r in combined.interiors)
closed=Polygon(combined.exterior);corrected_b=closed.difference(a)
assert corrected_b.geom_type=='Polygon' and corrected_b.is_valid and closed.is_valid
assert not closed.interiors and closed.covers(open_patch.representative_point())
assert a.intersection(corrected_b).area<1e-14
out=json.loads(json.dumps(original))
for f,g,label in zip(out['features'],[a,corrected_b],['Parcel A','Parcel B']):
 f['geometry']=mapping(g);f['properties'].update(name_en=label,area_km2=round(area(g),6),boundary_revision=VERSION,geometry_source='owner-supplied KML; organiser-authorised internal and open-seam closure, only the explicitly recorded seam patch changes the external outline',confidence='issued competition boundary; not surveyed/cadastral verification')
write(B/'parcels_9_13.geojson',out)
scope=json.loads((archive/'scope_9_13.geojson').read_text());scope['features'][0]['geometry']=mapping(closed)
scope['features'][0]['properties'].update(area_km2=round(area(closed),6),area_9_km2=round(area(a),6),area_13_km2=round(area(corrected_b),6),boundary_revision=VERSION,geometry_source='union of revised competition parcels; internal holes and externally connected seam closed with recorded four-point patch',confidence='issued competition boundary; not surveyed/cadastral verification')
write(B/'scope_9_13.geojson',scope)
report={
 'revision':VERSION,
 'authorisation':'Organiser explicitly instructed closure of the visible open seam between the two supplied parcels and synchronisation of every issued format. Competition-data topology correction, not cadastral certification.',
 'method':'Start from archived owner-supplied parcels; fill original two enclosed seam holes, then union the explicitly recorded four-point open-seam patch. Retain Parcel A unchanged, assign all corrected seam land to Parcel B and remove original overlap. No buffering. All land outside the original scope plus these authorised seam patches is unchanged.',
 'original_parcel_ids':{'main':'Parcel A (original 9)','south-west':'Parcel B (original 13)'},
 'original_scope_geodesic_km2':area(u),
 'previous_internal_only_scope_geodesic_km2':area(internal_closed),
 'revised_scope_geodesic_km2':area(closed),
 'added_internal_seam_geodesic_km2':area(internal_closed)-area(u),
 'added_open_seam_geodesic_km2':area(closed)-area(internal_closed),
 'added_total_geodesic_km2':area(closed)-area(u),
 'open_seam_patch':mapping(open_patch),
 'open_seam_mouth_lonlat':[aa[22],bb[21]],
 'open_seam_patch_sources':'A original vertices 22,23; intersection of A original edge 23-24 with B original edge 20-21; B original vertex 21. Zero-based indexes refer to archive/2026-10-26/parcels_9_13.geojson.',
 'removed_external_area_km2':0,
 'projected_exchange_note':'SHP/DXF EPSG:32719 chord representation; shared seam reconciled in that CRS. Symmetric-difference tolerance against directly projected WGS84 parcels is 20 m2. Exported parcel union equals scope and parcel overlap is zero within 0.01 m2.',
 'external_outline_unchanged':False,
 'external_outline_change_limit':'Only the authorised open-seam patch connects the previous open mouth; every other exterior edge is retained. Internal-hole closure alone was insufficient and is superseded.',
 'original_hole_count':len(u.interiors),'revised_hole_count':0,
 'original_holes_projected_m2':[transform(UTM,Polygon(r)).area for r in u.interiors],
 'original_overlap_projected_m2':transform(UTM,a.intersection(b)).area,'revised_overlap_m2':0,
 'parcels_geodesic_km2':[area(a),area(corrected_b)],
 'archive':'archive/2026-10-26','superseded_revision_archive':'archive/2026-10-27-v1.4.0',
 'sha256':{name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in ['parcels_9_13.geojson','scope_9_13.geojson']}
}
write(B/'boundary-revision.json',report)
areas=json.loads((SITE/'areas.json').read_text())
for f in areas['figures']:
 if f['key'] in ['site','parcel_main','parcel_southwest']:
  f['km2']=round({'site':area(closed),'parcel_main':area(a),'parcel_southwest':area(corrected_b)}[f['key']],1);f['boundary_revision']=VERSION
write(SITE/'areas.json',areas)
# Every exchange format is exported from these same in-memory issued geometries.
ns='http://www.opengis.net/kml/2.2'; ET.register_namespace('',ns)
k=ET.Element('{'+ns+'}kml');doc=ET.SubElement(k,'{'+ns+'}Document');ET.SubElement(doc,'{'+ns+'}name').text='XCITY competition boundary '+VERSION
pilot_fields=[shape(f['geometry']) for f in json.loads((SITE/'pilot-area/pilot_area.geojson').read_text())['features']]
pilot_living=[shape(f['geometry']) for f in json.loads((SITE/'pilot-area/pilot_living_area.geojson').read_text())['features']]
for name,g in [('Competition site',closed),('Parcel A',a),('Parcel B',corrected_b)]+[(f'Fixed pilot field {i+1}',g) for i,g in enumerate(pilot_fields)]+[(f'Fixed living area {i+1}',g) for i,g in enumerate(pilot_living)]:
 pm=ET.SubElement(doc,'{'+ns+'}Placemark');ET.SubElement(pm,'{'+ns+'}name').text=name
 ET.SubElement(pm,'{'+ns+'}description').text='Competition-data topology revision; not cadastral certification. '+VERSION
 poly=ET.SubElement(pm,'{'+ns+'}Polygon');ring=ET.SubElement(ET.SubElement(poly,'{'+ns+'}outerBoundaryIs'),'{'+ns+'}LinearRing');ET.SubElement(ring,'{'+ns+'}coordinates').text=' '.join(f'{x:.15g},{y:.15g},0' for x,y in orient(g,1).exterior.coords)
ET.ElementTree(k).write(B/'xcity_site_boundary.kml',encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(B/'xcity_site_boundary.kmz','w',zipfile.ZIP_DEFLATED) as z:z.write(B/'xcity_site_boundary.kml','doc.kml')
import shapefile, ezdxf
exports=B/'exchange';exports.mkdir(exist_ok=True)
# Projection represents curved WGS84 edges as UTM chords. Reconcile the shared
# seam in the target CRS as well, avoiding millimetre-width self-intersections.
projected_scope=transform(UTM,closed)
projected_a=transform(UTM,a).intersection(projected_scope)
projected_b=projected_scope.difference(projected_a)
projected={id(closed):projected_scope,id(a):projected_a,id(corrected_b):projected_b}
def projected_geometry(g):return projected.get(id(g),transform(UTM,g))
for name,gg in [('parcels',[a,corrected_b]),('site_boundary',[closed]),('pilot_fields',pilot_fields),('pilot_living',pilot_living)]:
 w=shapefile.Writer(str(exports/name),shapeType=shapefile.POLYGON);w.field('name','C',32);w.field('revision','C',48);w.field('area_km2','N',18,6)
 for i,g in enumerate(gg):w.poly([list(orient(projected_geometry(g),-1).exterior.coords)]);w.record(('Parcel '+chr(65+i)) if name=='parcels' else 'Competition site',VERSION,area(g))
 w.close();(exports/(name+'.prj')).write_text(CRS.from_epsg(32719).to_wkt('WKT1_ESRI'));(exports/(name+'.cpg')).write_text('UTF-8')
d=ezdxf.new('R2010');d.units=6;m=d.modelspace()
for name,gg in [('SITE_BOUNDARY',[closed]),('PARCELS',[a,corrected_b]),('PILOT_FIELDS',pilot_fields),('PILOT_LIVING',pilot_living)]:
 d.layers.new(name)
 for g in gg:m.add_lwpolyline(list(projected_geometry(g).exterior.coords)[:-1],close=True,dxfattribs={'layer':name})
d.saveas(exports/'xcity_site_boundary_utm19s.dxf')
print(json.dumps(report,indent=2))
# Retain the issued screening analysis; update its coverage only where the revised
# site adds cells. No new flood-risk classification is invented for these cells.
import numpy as np
from PIL import Image
from shapely import contains_xy
terrain=SITE/'terrain'; baseline=archive/'terrain_summary_9_13.json'
if not baseline.exists():shutil.copyfile(terrain/'terrain_summary_9_13.json',baseline)
stats=json.loads(baseline.read_text()); rb=stats['files']['hillshade_utm_bounds_m']
dem=np.asarray(Image.open(terrain/'dem_9_13_utm19s_60m.png')).astype(float);h,w=dem.shape
xx,yy=np.meshgrid(np.linspace(rb[0]+30,rb[2]-30,w),np.linspace(rb[3]-30,rb[1]+30,h))
added_cells=contains_xy(transform(UTM,closed),xx,yy)&~contains_xy(transform(UTM,u),xx,yy)
dy,dx=np.gradient(dem,60);slope=np.hypot(dx,dy)*100;pad=np.pad(slope,2,mode='edge');slope=sum(pad[i:i+h,j:j+w] for i in range(5) for j in range(5))/25
increments={k:float(((slope>=lo)&(slope<hi)&added_cells).sum()*.0036) for k,lo,hi in [('lt_2pct',0,2),('2_5pct',2,5),('5_15pct',5,15),('15_25pct',15,25),('ge_25pct',25,1e9)]}
for key,value in increments.items():stats['slope_km2'][key]=round(stats['slope_km2'][key]+value,1)
stats['site_km2']=round(stats['site_km2']+float(added_cells.sum()*.0036),1)
stats['boundary_revision']=VERSION
stats['boundary_revision_note_en']='Original terrain classification retained; added cell centres inside the closed internal seam classified from the same issued 60 m DEM. Flood-sensitive/HAND screening was not rerun; newly included internal and open-seam land is hydrologically unclassified. Flat-not-flood area remains the pre-revision screening result, not an expanded developable-land claim.'
stats['seam_added_cells_60m']=int(added_cells.sum());stats['seam_added_raster_km2']=float(added_cells.sum()*.0036);stats['seam_slope_increments_km2']=increments
stats['flood_screen_boundary_revision']='original-before-seam-closure';stats['flood_screen_unclassified_added_km2']=area(closed)-area(u)
write(terrain/'terrain_summary_9_13.json',stats)
for f in areas['figures']:
 if f['key'].startswith('slope_'):
  key={'slope_lt_2pct':'lt_2pct','slope_2_5pct':'2_5pct','slope_5_15pct':'5_15pct','slope_15_25pct':'15_25pct','slope_ge_25pct':'ge_25pct'}[f['key']];f['km2']=stats['slope_km2'][key];f['boundary_revision']=VERSION
 if f['key'] in ['flood_sensitive','flat_lt2pct_not_flood']:f['coverage_note']='Pre-seam-closure screening extent; added internal seam land remains hydrologically unclassified.'
 if f['key']=='site':f.update(nominal_area_km2=1656,geometry_area_km2=area(closed),say='1,656 km² (nominal project area)')
write(SITE/'areas.json',areas)
registry=json.loads((SITE/'datapackage.json').read_text());registry['version']='1.5.0';registry['boundary_revision']=VERSION
for resource in registry['resources']:
 p=SITE/resource['path']
 if p.is_file():resource['hash']='sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()
 if resource['path']=='boundaries/parcels_9_13.geojson':resource['description']='Two issued competition parcels; internal seam closure, not cadastral verification'
 if resource['path'].startswith('boundaries/'):resource['boundary_revision']=VERSION
write(SITE/'datapackage.json',registry)

index=json.loads((SITE/'evidence-index.json').read_text())
def update_metadata(value):
 if isinstance(value,dict):
  for key,item in value.items():
   if key=='precision' and str(value.get('path','')).startswith('boundaries/'):
    value[key]='Owner-derived competition topology correction: two enclosed holes and the externally connected seam are filled using the recorded four-point patch. Parcel A unchanged; only the open-seam patch changes the previous exterior, all other exterior edges retained. Survey accuracy not supplied.'
   elif key=='boundary_revision':value[key]=VERSION
   elif key=='geometry_area_km2':value[key]=area(closed)
   elif key=='revised_scope_geodesic_km2':value[key]=area(closed)
   else:update_metadata(item)
 elif isinstance(value,list):
  for item in value:update_metadata(item)
update_metadata(index);write(SITE/'evidence-index.json',index)
# Refresh hashes after all metadata writes without downgrading the node catalogue.
for resource in registry['resources']:
 path=SITE/resource['path']
 if path.is_file():resource['hash']='sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()
write(SITE/'datapackage.json',registry)
