"""Regression: changed rendering policy/code must invalidate cached scene views."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import xcity_common as xc
class SceneFingerprintTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.r=Path(self.tmp.name);self.p=self.r/'package';self.p.mkdir();(self.r/'scripts/scene').mkdir(parents=True);(self.r/'scripts/make_scene.py').write_text('version one');(self.r/'scripts/scene/scene.js').write_text('client one');self.man={'title':'QA','scene_generation':{'procedural_planting':False}};self.write()
 def write(self):(self.p/'manifest.json').write_text(json.dumps(self.man))
 def tearDown(self):self.tmp.cleanup()
 def h(self):
  with patch.object(xc,'ROOT',str(self.r)):return xc.scene_input_hash(str(self.p))
 def test_stable(self):self.assertEqual(self.h(),self.h())
 def test_policy_changes(self):
  old=self.h();self.man['scene_generation']['procedural_planting']=True;self.write();self.assertNotEqual(old,self.h())
 def test_generator_changes(self):
  old=self.h();(self.r/'scripts/make_scene.py').write_text('version two');self.assertNotEqual(old,self.h())
 def test_client_changes(self):
  old=self.h();(self.r/'scripts/scene/scene.js').write_text('client two');self.assertNotEqual(old,self.h())
if __name__=='__main__':unittest.main()
