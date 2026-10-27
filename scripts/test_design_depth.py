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
  self.doc={'schema_version':1,'rows':[{'id':i,'status':'documented','drawings':['plan.svg'],'geometry':['geometry.geojson'],'metrics':['residents_phase1'],'explanation':{'path':'proposal.md','heading':'## 7.'},'gaps':[]} for i in ids]}
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
  self.doc['rows'][0].update(status='partial',metrics=[],gaps=[{'missing':'Water entitlement','next_step':'Confirm with operator','responsible':'Water specialist'}]);r=self.assess();self.assertEqual(r['automatic']['status'],'references_consistent');self.assertEqual(r['further_work']['items'][0]['missing'],'Water entitlement')
 def test_partial_without_plan(self):
  self.doc['rows'][0]['status']='partial';self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_false_approval(self):
  self.doc['rows'][0]['status']='passed';self.assertEqual(self.assess()['automatic']['status'],'failed')
 def test_legacy_exact_paths(self):
  for rel in dd.POLICY['legacy_submissions']:self.assertFalse(dd.applies(dd.ROOT/rel))
  self.assertTrue(dd.applies(self.p))
 def test_missing_matrix(self):self.assertEqual(dd.assess(self.p,['N02','N05','N07'])['automatic']['status'],'failed')
 def test_machine_twins(self):self.assertEqual(json.loads((dd.ROOT/'brief/requirements.json').read_text())['design_depth'],dd.POLICY)

if __name__=='__main__':unittest.main()
