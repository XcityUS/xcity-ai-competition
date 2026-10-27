"""A distant solar territory must not disappear when homes define a small local cluster."""
import unittest
from shapely.geometry import box
from make_scene import Scene
class SceneTerritoryScope(unittest.TestCase):
 def test_whole_site_camera_uses_issued_extent_not_housing(self):
  s=Scene.__new__(Scene);s.site=box(0,0,60000,40000);s.master=box(1000,1000,2000,2000);s.o=(1500,1500)
  s.buildings=[box(1200,1200,1300,1300)];s.geo={'buildings':[({'use':'residential'},s.buildings[0])],'nodes':[]}
  views={v['id']:v for v in s.views()};w=views['whole-site-aerial'];self.assertEqual(w['target'],[28500,18500,0]);self.assertGreater(w['pos'][2],50000)
  self.assertNotEqual(w['target'],views['city-aerial']['target']);self.assertIn('not the whole-site',views['city-aerial']['label'])
if __name__=='__main__':unittest.main()
