"""Regression tests for construction-programme reconciliation, not design quality."""
import copy,json,tempfile,unittest
from pathlib import Path
import phasing_programme
class ProgrammeTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name);(self.p/'geometry').mkdir();(self.p/'map.png').touch();(self.p/'a0.pdf').touch()
  self.d={'schema_version':1,'map':'map.png','a0_board':'a0.pdf','phases':[]};features=[]
  for n in [1,2,3]:
   self.d['phases'].append({'phase':n,'period':'Years %s to %s'%(n,n+1),'objective':'Provide homes and services','works':['Homes after utility commissioning'],'sequence_dependencies':['Commission water before occupancy'],'trigger':'Verified resource capacity and demand','zones':[{'zone_id':'town','basis':'Scenario based on dwelling capacity','new_residents':100,'cumulative_residents':100*n,'new_dwellings':40,'cumulative_dwellings':40*n,'new_jobs':30,'cumulative_jobs':30*n}]})
   features.append({'properties':{'zone_id':'town','phase':n}})
  (self.p/'geometry/phasing.geojson').write_text(json.dumps({'features':features}));(self.p/'metrics.json').write_text(json.dumps({'metrics':[{'key':'residents_phase1','value':100}]}))
 def tearDown(self):self.t.cleanup()
 def run_check(self):
  (self.p/'phasing_programme.json').write_text(json.dumps(self.d));return phasing_programme.assess(self.p)
 def test_reconciled(self):self.assertEqual(self.run_check(),[])
 def test_missing(self):self.assertTrue(phasing_programme.assess(self.p))
 def test_bad_cumulative(self):
  self.d['phases'][1]['zones'][0]['cumulative_residents']=100;self.assertTrue(any('reconcile' in x for x in self.run_check()))
 def test_metric_mismatch(self):
  self.d['phases'][0]['zones'][0]['new_residents']=80;self.d['phases'][0]['zones'][0]['cumulative_residents']=80;self.assertTrue(any('metrics.json' in x for x in self.run_check()))
 def test_zone_not_in_map(self):
  self.d['phases'][1]['zones'][0]['zone_id']='invented';self.assertTrue(any('no matching' in x for x in self.run_check()))
 def test_placeholder(self):
  self.d['phases'][0]['period']='{{duration}}';self.assertTrue(any('actual period' in x for x in self.run_check()))
if __name__=='__main__':unittest.main()
