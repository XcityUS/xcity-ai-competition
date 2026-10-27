import unittest
from shapely.geometry import box,LineString
from whole_site_plan import assess
class FullSitePlanTests(unittest.TestCase):
 def setUp(self):
  self.site=box(0,0,10000,10000);self.road=[({'road_class':k},LineString([(0,i*1000),(10000,i*1000)])) for i,k in enumerate(['primary','secondary'])]
 def zone(self,i,g):return ({'plan_role':'base_zoning','district_id':i,'primary_use':'planned use','name':'Named area','basis_ref':'assumptions.json#A-SITING'},g)
 def test_complete_base_and_roads(self):self.assertEqual([],assess({'structure':[self.zone('A',box(0,0,5000,10000)),self.zone('B',box(5000,0,10000,10000))],'movement':self.road},self.site))
 def test_local_plan_is_not_whole_site(self):self.assertTrue(any('unassigned' in e for e in assess({'structure':[self.zone('A',box(0,0,1000,1000))],'movement':self.road},self.site)))
 def test_overlays_do_not_replace_base(self):self.assertTrue(any('missing' in e for e in assess({'structure':[({'system':'living'},self.site)],'movement':self.road},self.site)))
 def test_overlap_rejected(self):self.assertTrue(any('overlaps' in e for e in assess({'structure':[self.zone('A',self.site),self.zone('B',box(5000,0,10000,10000))],'movement':self.road},self.site)))
 def test_user_network_is_not_hierarchy(self):self.assertTrue(any('road_class' in e for e in assess({'structure':[self.zone('A',self.site)],'movement':[({'network':'machine'},LineString([(0,0),(10000,0)]))]},self.site)))
 def test_overlay_overlap_allowed(self):self.assertEqual([],assess({'structure':[self.zone('A',self.site),({'plan_role':'system_overlay','system':'energy_compute'},self.site)],'movement':self.road},self.site))
if __name__=='__main__':unittest.main()
