"""Check submitted full-site base zoning and road hierarchy, never design quality.
System overlays remain allowed to overlap; base zoning is a separate role in the
existing structure file. No zones or roads are invented by this module.
"""
from shapely.ops import unary_union

def assess(geo_utm, site):
 errors=[];zones=[(p,g) for p,g in geo_utm.get('structure',[]) if p.get('plan_role')=='base_zoning']
 if not zones:return ['Full-site base zoning is missing: structure.geojson needs plan_role=base_zoning polygons with district_id, primary_use, name and basis_ref. System overlays, a local master plan and three node circles are not the full-site zoning plan.']
 ids=[]
 for i,(p,g) in enumerate(zones):
  for key in ['district_id','primary_use','name','basis_ref']:
   if not isinstance(p.get(key),str) or not p[key].strip():errors.append('Base zone %s: %s is missing'%(i,key))
  ids.append(p.get('district_id'))
  if g.geom_type not in ['Polygon','MultiPolygon'] or g.is_empty:errors.append('Base zone %s needs nonempty polygon geometry'%i)
 if len(set(ids))!=len(ids):errors.append('Base zoning district_id values must be unique; use a MultiPolygon for one district with separate parts.')
 if any(g.geom_type not in ['Polygon','MultiPolygon'] or g.is_empty for _,g in zones):return errors
 union=unary_union([g for _,g in zones]);tol=max(100,site.area*.0001)
 missing=site.difference(union).area;overlap=sum(g.intersection(site).area for _,g in zones)-union.intersection(site).area
 if missing>tol:errors.append('Full-site base zoning leaves %.3f km2 unassigned; classify development, agriculture, protection/reserve and fixed context explicitly. A reserve label still requires a design reason in the proposal.'%(missing/1e6))
 if overlap>tol:errors.append('Base zoning overlaps by %.3f km2; separate overlapping system layers using plan_role=system_overlay rather than double-counting the base land account.'%(overlap/1e6))
 if union.difference(site).area>tol:errors.append('Base zoning extends beyond the issued whole-site boundary; put external studies in context/.')
 roads=[(p,g) for p,g in geo_utm.get('movement',[]) if g.geom_type in ['LineString','MultiLineString'] and g.length>0]
 for level in ['primary','secondary']:
  if not any(p.get('road_class')==level for p,g in roads):errors.append('movement.geojson has no explicit road_class=%s route. Draw the proposed whole-site road hierarchy; network=people/shared/machine describes users, not street hierarchy.'%level)
 return errors
