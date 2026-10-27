import json,tempfile,unittest
from pathlib import Path
from shapely.geometry import box,mapping
import spatial_checks as s
import xcity_common as xc
class SpatialTests(unittest.TestCase):
 def setUp(self):
  self.master=box(-68,-31,-67.99,-30.99)
 def geo(self,parts):return {'master_area':[({},self.master)],'land_use':[({'use':'open_space'},g) for g in parts]}
 def test_partition_overlap_and_omission(self):
  self.assertEqual(s.partition_problems(self.geo([self.master])),[])
  self.assertTrue(any('overlaps' in x for x in s.partition_problems(self.geo([self.master,self.master]))))
  self.assertTrue(any('omits' in x for x in s.partition_problems(self.geo([box(-68,-31,-67.995,-30.99)]))))
 def test_context_outside_not_construction(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'context').mkdir();f=p/'context/access.geojson'
   d={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'status':'study_only','authority':'not_secured','basis':'Regional access study, permissions unknown'},'geometry':mapping(box(-69,-32,-68.9,-31.9))}]};f.write_text(json.dumps(d));self.assertEqual(s.context_errors(p),[])
   d['features'][0]['properties']['authority']='approved';f.write_text(json.dumps(d));self.assertTrue(s.context_errors(p))
 def test_v2_metrics_clip_without_changing_legacy(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);inside=box(-68,-31,-67.995,-30.995);outside=box(-68.1,-31.1,-68.09,-31.09)
   geo=self.geo([self.master]);geo.update(buildings=[({'floors':2},inside),({'floors':3},outside)],structure=[],movement=[])
   old=xc.compute_metrics(p,geo)
   (p/'design_depth_matrix.json').write_text('{"schema_version":2}')
   new=xc.compute_metrics(p,geo);self.assertLess(new['gfa_m2'],old['gfa_m2']);self.assertGreater(new['outside_master_gfa_m2'],0)
 def test_pilot_parts_separate_and_both_protected(self):
  parts={k:xc.to_utm(g) for k,g in xc.pilot_parts().items()}
  self.assertEqual(xc.pilot_land_use_conflicts('agriculture',parts['agrivoltaic'],parts),[])
  self.assertIn('living',xc.pilot_land_use_conflicts('agriculture',parts['living'],parts))
  self.assertEqual(xc.pilot_land_use_conflicts('residential',parts['living'],parts),[])
if __name__=='__main__':unittest.main()
