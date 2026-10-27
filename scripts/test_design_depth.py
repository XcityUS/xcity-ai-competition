"""Isolated synthetic integration package; reference integrity is not design approval."""
import json
import tempfile
import unittest
from pathlib import Path
import design_depth as dd

class DepthTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
  for name in ('plan.svg','geometry.geojson'):(self.p/name).write_text('synthetic reference fixture only')
  (self.p/'proposal.md').write_text('## 7. Urban form\nFixture only\n')
  (self.p/'metrics.json').write_text('{"metrics":[{"key":"residents_phase1","value":1}]}')
  ids=[x['id'] for x in dd.POLICY['levels']]+['node:N02','node:N05','node:N07']
  self.doc={'schema_version':2,'rows':[{'decision':'Test the actual spatial claim','scope':{'extent':'Named district','phase':'Phase 1'},'id':i,'status':'documented','drawings':['plan.svg'],'geometry':['geometry.geojson'],'metrics':['residents_phase1'],'explanation':{'path':'proposal.md','heading':'## 7.'},'gaps':[]} for i in ids]}
 def tearDown(self):self.tmp.cleanup()
 def assess(self):
  (self.p/dd.MATRIX).write_text(json.dumps(self.doc));return dd.assess(self.p,['N02','N05','N07'])
 def test_reference_pass_never_design_pass(self):
  r=self.assess();self.assertEqual(r['automatic']['status'],'references_consistent');self.assertEqual(r['content_review']['status'],'not_assessed')
 def test_missing_row(self):
  self.doc['rows'].pop();self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_missing_file(self):
  self.doc['rows'][0]['drawings']=['missing.pdf'];self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_escaping_path(self):
  self.doc['rows'][0]['drawings']=['../outside'];self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_unknown_metric_and_heading(self):
  row=self.doc['rows'][0];row['metrics']=['invented'];row['explanation']['heading']='## 99.';self.assertEqual(len(self.assess()['automatic']['errors']),2)
 def test_partial_missing_data_disclosed(self):
  self.doc['rows'][0].update(status='partial',metrics=[],gaps=[{'kind':'organiser_data','missing':'Water entitlement','next_step':'Confirm with operator','responsible':'Water specialist'}]);r=self.assess();self.assertEqual(r['automatic']['status'],'references_consistent');self.assertEqual(r['further_work']['items'][0]['missing'],'Water entitlement')
 def test_partial_without_plan(self):
  self.doc['rows'][0]['status']='partial';self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_false_approval(self):
  self.doc['rows'][0]['status']='passed';self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_legacy_exact_paths(self):
  for rel in dd.POLICY['legacy_submissions']:
   package=dd.ROOT/rel
   self.assertEqual(dd.applies(package),(package/dd.MATRIX).exists())
  self.assertTrue(dd.applies(self.p))
 def test_missing_matrix(self):self.assertEqual(dd.assess(self.p,['N02','N05','N07'])['automatic']['status'],'failed')
 def test_v2_scope_decision_and_gap_types(self):
  self.doc['schema_version']=2
  for row in self.doc['rows']:row.update(decision='Locate services and test the upper-level promise',scope={'extent':'Named district within fixed site','phase':'Phase 1'})
  self.assertEqual(self.assess()['automatic']['status'],'references_consistent')
  self.doc['rows'][0]['scope']['extent']='{{replace}}';self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_v2_data_gap_does_not_waive_spatial_evidence(self):
  self.doc['schema_version']=2
  for row in self.doc['rows']:row.update(decision='Test spatial relation',scope={'extent':'Whole site','phase':'Long-term scenario'})
  self.doc['rows'][0].update(drawings=[],status='partial',gaps=[{'kind':'organiser_data','missing':'Water rights','next_step':'Verify source','responsible':'Water specialist'}])
  self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_new_entry_cannot_downgrade_to_v1(self):
  self.doc['schema_version']=1
  self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_machine_twins(self):self.assertEqual(json.loads((dd.ROOT/'brief/requirements.json').read_text())['design_depth'],dd.POLICY)

if __name__=='__main__':unittest.main()
