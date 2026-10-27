"""Regression for the actual omitted-road bug in the default whole-site panel."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from shapely.geometry import box,LineString
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import make_figures as mf
class WholeSiteRenderTests(unittest.TestCase):
 def test_submitted_hierarchy_is_rendered(self):
  site=box(0,0,10000,10000);primary=LineString([(100,100),(9000,100)]);secondary=LineString([(100,200),(9000,200)])
  pkg=SimpleNamespace(site=site,master=None,nodes={},parcels=[],computed={'structure_km2':{}},geo={'structure':[({'plan_role':'base_zoning','district_id':'D1','primary_use':'compute'},site)],'movement':[({'road_class':'primary'},primary),({'road_class':'secondary'},secondary)]})
  f,ax=plt.subplots()
  with patch.object(mf,'hillshade'),patch.object(mf,'site_context'),patch.object(mf,'channels'),patch.object(mf,'frame'),patch.object(mf,'scalebar_north'),patch.object(mf,'outline') as outline:
   legend=mf.panel_structure(pkg,ax)
  widths=[c.kwargs.get('lw') for c in outline.call_args_list]
  self.assertIn(2.0,widths);self.assertIn(1.15,widths)
  self.assertTrue(any('Compute' in str(row) for row in legend))
  plt.close(f)
if __name__=='__main__':unittest.main()
