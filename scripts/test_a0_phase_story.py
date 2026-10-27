"""A large district programme must not turn the presentation board into a table."""
import unittest
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from make_figures import panel_a0_phase_story
class A0PhaseStoryTests(unittest.TestCase):
 def test_large_programme_remains_three_stage_story(self):
  data={'phases':[{'phase':i,'objective':'Open services and connect complete neighbourhoods','zones':[{'zone_id':f'D{j}','new_residents':100} for j in range(32)]} for i in [1,2,3]]}
  f,a=plt.subplots();panel_a0_phase_story(a,data)
  self.assertEqual(len(a.tables),0)
  texts=[x.get_text() for x in a.texts]
  self.assertEqual(sum('additional residents' in x for x in texts),3)
  self.assertEqual(sum('3,200' in x for x in texts),3)
  self.assertFalse(any('D31' in x for x in texts))
  plt.close(f)
 def test_capacity_ranges_keep_scenario_range(self):
  f,a=plt.subplots();panel_a0_phase_story(a,{'phases':[{'phase':1,'objective':'Build daily services','zones':[{'new_residents':{'min':100,'max':200}},{'new_residents':50}]}]})
  self.assertTrue(any('150 - 250 additional residents' in x.get_text() for x in a.texts));self.assertEqual(len(a.tables),0);plt.close(f)
if __name__=='__main__':unittest.main()
