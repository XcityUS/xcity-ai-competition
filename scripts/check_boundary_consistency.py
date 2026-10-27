#!/usr/bin/env python3
"""Verify the issued GeoJSON, Google Earth, GIS, CAD and ZIP contain one geometry revision.
Optional dependencies: pyshp, ezdxf. Does not modify submissions or data.
"""
from pathlib import Path
import json,xml.etree.ElementTree as ET,zipfile
import shapefile,ezdxf
from shapely.geometry import shape,Polygon,Point,LineString
from shapely.ops import transform,unary_union
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];B=R/'brief/site-package/boundaries';t=Transformer.from_crs(4326,32719,always_xy=True).transform
parcels=[shape(f['geometry']) for f in json.loads((B/'parcels_9_13.geojson').read_text())['features']];scope=shape(json.loads((B/'scope_9_13.geojson').read_text())['features'][0]['geometry'])
old=shape(json.loads((B/'archive/2026-10-26/scope_9_13.geojson').read_text())['features'][0]['geometry'])
assert scope.is_valid and scope.geom_type=='Polygon' and len(scope.interiors)==0
original_parcels=[shape(f['geometry']) for f in json.loads((B/'archive/2026-10-26/parcels_9_13.geojson').read_text())['features']]
original_union=unary_union(original_parcels);internal_closed=Polygon(original_union.exterior)
report=json.loads((B/'boundary-revision.json').read_text())
assert report['revision']=='2026-10-27-open-seam-closure'
aa=list(original_parcels[0].exterior.coords);bb=list(original_parcels[1].exterior.coords)
join=LineString([aa[23],aa[24]]).intersection(LineString([bb[20],bb[21]]))
patch=Polygon([aa[22],aa[23],join.coords[0],bb[21]])
assert patch.is_valid and patch.area>0
assert patch.equals(shape(report['open_seam_patch']))
expected=Polygon(internal_closed.union(patch).exterior)
assert scope.symmetric_difference(expected).area<1e-13,'Correction differs from the explicitly authorised patch and original holes'
assert original_union.difference(scope).area<1e-13,'Original site land removed'
assert parcels[0].equals(original_parcels[0]),'Parcel A changed'
allowed=unary_union([patch]+[Polygon(r) for r in original_union.interiors])
assert scope.difference(original_union).difference(allowed).area<1e-13,'Land outside the authorised correction was added'
# A no-hole check alone misses an externally connected slit. Check the actual mouth
# and 25 interior points distributed down five cross-sections of the missing seam.
mouth=LineString([aa[22],bb[21]])
assert mouth.difference(scope).length<1e-12,'The open seam mouth remains unclosed'
samples=[]
for f in [.05,.25,.5,.75,.95]:
 left=LineString([aa[22],aa[23]]).interpolate(f,normalized=True)
 right=LineString([bb[21],join.coords[0]]).interpolate(f,normalized=True)
 cross=LineString([left,right])
 for at in [.05,.25,.5,.75,.95]:
  point=cross.interpolate(at,normalized=True);samples.append(point)
  assert scope.covers(point),'White slit sample still outside corrected scope'
assert any(not internal_closed.covers(point) for point in samples),'Regression test no longer samples the previously missed open slit'
assert unary_union(parcels).symmetric_difference(scope).area<1e-14
assert parcels[0].intersection(parcels[1]).area<1e-14
assert parcels[0].boundary.intersection(parcels[1].boundary).length>0,'No shared seam'
ns={'k':'http://www.opengis.net/kml/2.2'}
kml=ET.parse(B/'xcity_site_boundary.kml');geoms=[]
for item in kml.findall('.//k:Placemark',ns):
 coords=item.find('.//k:coordinates',ns).text;ring=[tuple(map(float,p.split(',')[:2])) for p in coords.split()]
 assert ring[0]==ring[-1], 'KML ring not explicitly closed'
 geoms.append(Polygon(ring))
for expected,actual in zip([scope]+parcels,geoms[:3]):assert expected.hausdorff_distance(actual)<1e-11
assert all(geoms[0].covers(point) for point in samples),'KML still contains the open slit'
with zipfile.ZipFile(B/'xcity_site_boundary.kmz') as z:assert z.read('doc.kml')==(B/'xcity_site_boundary.kml').read_bytes()
for name,gg in [('site_boundary',[scope]),('parcels',parcels)]:
 reader=shapefile.Reader(str(B/'exchange'/name));assert len(reader)==len(gg)
 for expected,actual in zip(gg,reader.shapes()):
  polygon=shape(actual.__geo_interface__);reference=transform(t,expected)
  assert polygon.is_valid and polygon.geom_type=='Polygon' and not polygon.interiors
  assert reference.symmetric_difference(polygon).area<20 and abs(reference.area-polygon.area)<20
cad=ezdxf.readfile(B/'exchange/xcity_site_boundary_utm19s.dxf')
for layer,gg in [('SITE_BOUNDARY',[scope]),('PARCELS',parcels)]:
 entities=list(cad.modelspace().query('LWPOLYLINE[layer=="'+layer+'"]'));assert len(entities)==len(gg)
 for expected,item in zip(gg,entities):
  polygon=Polygon([(v[0],v[1]) for v in item]);reference=transform(t,expected)
  assert item.closed and polygon.is_valid and not polygon.interiors
  assert reference.symmetric_difference(polygon).area<20 and abs(reference.area-polygon.area)<20
with zipfile.ZipFile(R/'brief/design-practice-stage1-data.zip') as z:
 for name in ['xcity_site_boundary.kml','xcity_site_boundary.kmz','scope_9_13.geojson','parcels_9_13.geojson','boundary-revision.json']:
  assert z.read('XCITY_design_practice_stage1_data/'+name)==(B/name).read_bytes(),name
 for p in (B/'exchange').iterdir():
  name=p.name if p.suffix=='.dxf' else 'shp/'+p.name
  assert z.read('XCITY_design_practice_stage1_data/'+name)==p.read_bytes(),name
print('PASS: explicit four-point open-seam patch, mouth transect and 25 formerly omitted slit samples covered; only authorised seam land added; closed valid rings, unchanged Parcel A, no overlap; GeoJSON/KML/KMZ/SHP/DXF/ZIP agree.')

projected_parcels=[shape(s.__geo_interface__) for s in shapefile.Reader(str(B/'exchange/parcels')).shapes()]
projected_scope=shape(shapefile.Reader(str(B/'exchange/site_boundary')).shape(0).__geo_interface__)
assert unary_union(projected_parcels).symmetric_difference(projected_scope).area<0.01
assert projected_parcels[0].intersection(projected_parcels[1]).area<0.01
print('PASS: projected GIS parcel union equals GIS scope without overlap, including target-CRS seam reconciliation (<20 m² chord-projection tolerance).')

assert all(projected_scope.covers(transform(t,point)) for point in samples),'SHP retains an open seam'
site_cad=list(cad.modelspace().query('LWPOLYLINE[layer=="SITE_BOUNDARY"]'))[0]
site_cad_polygon=Polygon([(v[0],v[1]) for v in site_cad])
assert all(site_cad_polygon.covers(transform(t,point)) for point in samples),'DXF retains an open seam'
print('PASS: independent slit sample coverage also verified in projected SHP and DXF.')

# Optional release verification: checks actual deployed bytes, not merely local data.
# Run only after publishing: --published-base https://xcityus.github.io/xcity-ai-competition/
if __name__=='__main__':
 import argparse,hashlib
 from urllib.request import urlopen
 from urllib.parse import urljoin
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--published-base',help='After deployment, compare official published files with this checked release')
 options=parser.parse_args()
 if options.published_base:
  for relative in ['brief/site-package/boundaries/scope_9_13.geojson','brief/site-package/boundaries/parcels_9_13.geojson','brief/site-package/boundaries/xcity_site_boundary.kml','brief/site-package/boundaries/xcity_site_boundary.kmz','brief/site-package/boundaries/boundary-revision.json','brief/design-practice-stage1-data.zip']:
   url=urljoin(options.published_base.rstrip('/')+'/',relative)+'?boundary_revision='+report['revision']
   with urlopen(url,timeout=45) as response:published=response.read()
   assert hashlib.sha256(published).digest()==hashlib.sha256((R/relative).read_bytes()).digest(),'Published file differs from corrected release: '+relative
  print('PASS: published GeoJSON, KML, KMZ, revision record and downloadable ZIP match this checked open-seam closure release byte-for-byte.')
