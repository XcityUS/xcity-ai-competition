import unittest
from shapely.geometry import box,MultiPolygon
from analyse_functional_balance import analyse,programme_checks,area
class BalanceTests(unittest.TestCase):
 def test_multipart_areas_and_denominator_stay_consistent(self):
  a=box(500000,6500000,501000,6501000);b=box(502000,6500000,503000,6501000);m=MultiPolygon([a,b]);self.assertAlmostEqual(area(m),area(a)+area(b))
  r=analyse(m,[(a,{'plan_role':'base_zoning','primary_use':'ecology'}),(b,{'plan_role':'base_zoning','primary_use':'housing'})]);self.assertAlmostEqual(r['base_groups']['living']['share_of_nonfixed_nonretained_pct'],100)
 def test_overlays_are_not_added_to_base(self):
  s=box(500000,6500000,501000,6501000);r=analyse(s,[(s,{'plan_role':'base_zoning','primary_use':'solar_agriculture'}),(s,{'plan_role':'system_overlay','system':'agri_production'})])
  self.assertAlmostEqual(r['base_groups']['energy_compute']['whole_site_pct'],100)
  self.assertAlmostEqual(r['system_overlay_coverage']['agri_production']['whole_site_pct'],100)
  self.assertAlmostEqual(r['geometry_findings']['overlap_excess_km2'],0)
 def test_overlapping_and_outside_base_are_reported(self):
  s=box(500000,6500000,501000,6501000);g=box(500500,6500000,501500,6501000)
  r=analyse(s,[(s,{'plan_role':'base_zoning','primary_use':'housing'}),(g,{'plan_role':'base_zoning','primary_use':'industry'})]);self.assertGreater(r['geometry_findings']['overlap_excess_km2'],.4);self.assertGreater(r['geometry_findings']['outside_scope_km2'],.4)
 def test_no_defaults_for_missing_demand(self):
  self.assertTrue(all(x['gross_area_estimate_km2'] is None for x in programme_checks({})))
 def test_compute_rounds_whole_halls_and_requires_basis(self):
  d={k:{'value':v,'evidence':'assumed','basis':'test scenario'} for k,v in [('it_mw',3),('it_mw_per_hall',2),('hall_footprint_m2',1000),('campus_building_coverage',.5)]}
  self.assertAlmostEqual(programme_checks(d)[2]['gross_area_estimate_km2'],.004)
  d['it_mw']['basis']=''
  with self.assertRaises(ValueError):programme_checks(d)
if __name__=='__main__':unittest.main()
