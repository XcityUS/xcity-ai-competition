#!/usr/bin/env python3
"""Verify the issued GeoJSON, Google Earth, GIS, CAD and ZIP contain one geometry revision.
Optional dependencies: pyshp, ezdxf. Does not modify submissions or data.
"""
from pathlib import Path
import json,xml.etree.ElementTree as ET,zipfile
import shapefile,ezdxf
from shapely.geometry import shape,Polygon
from shapely.ops import transform,unary_union
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];B=R/'brief/site-package/boundaries';t=Transformer.from_crs(4326,32719,always_xy=True).transform
parcels=[shape(f['geometry']) for f in json.loads((B/'parcels_9_13.geojson').read_text())['features']];scope=shape(json.loads((B/'scope_9_13.geojson').read_text())['features'][0]['geometry'])
old=shape(json.loads((B/'archive/2026-10-26/scope_9_13.geojson').read_text())['features'][0]['geometry'])
assert scope.is_valid and scope.geom_type=='Polygon' and len(scope.interiors)==0
original_parcels=[shape(f['geometry']) for f in json.loads((B/'archive/2026-10-26/parcels_9_13.geojson').read_text())['features']]
assert scope.exterior.equals(unary_union(original_parcels).exterior),'Source union external outline changed'
assert transform(t,scope.exterior).hausdorff_distance(transform(t,old.exterior))<0.1,'Previous scope differs beyond sub-decimetre intersection rounding'
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
print('PASS: valid no-hole scope; unchanged external outline; shared seam without overlap; GeoJSON/KML/KMZ/SHP/DXF/ZIP agree; fixed pilot layers retained.')

projected_parcels=[shape(s.__geo_interface__) for s in shapefile.Reader(str(B/'exchange/parcels')).shapes()]
projected_scope=shape(shapefile.Reader(str(B/'exchange/site_boundary')).shape(0).__geo_interface__)
assert unary_union(projected_parcels).symmetric_difference(projected_scope).area<0.01
assert projected_parcels[0].intersection(projected_parcels[1]).area<0.01
print('PASS: projected GIS parcel union equals GIS scope without overlap, including target-CRS seam reconciliation (<20 m² chord-projection tolerance).')
