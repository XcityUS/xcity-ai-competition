import unittest

from shapely.geometry import box
import xcity_common as xc


class PilotContextTests(unittest.TestCase):
    def setUp(self):
        self.parts = {"agrivoltaic": box(0, 0, 100, 100), "living": box(200, 0, 300, 100)}

    def test_residential_context_is_not_treated_as_a_solar_field(self):
        self.assertEqual(xc.pilot_land_use_conflicts("residential", self.parts["living"], self.parts), [])
        self.assertEqual(xc.pilot_land_use_conflicts("residential", self.parts["agrivoltaic"], self.parts), ["agrivoltaic"])

    def test_industrial_relabelling_fails_in_both_fixed_parts(self):
        self.assertEqual(set(xc.pilot_land_use_conflicts("industry", box(0, 0, 300, 100), self.parts)), set(self.parts))

    def test_compatible_fixed_context_and_external_land(self):
        self.assertEqual(xc.pilot_land_use_conflicts("energy", self.parts["agrivoltaic"], self.parts), [])
        self.assertEqual(xc.pilot_land_use_conflicts("agriculture", self.parts["living"], self.parts), [])
        self.assertEqual(xc.pilot_land_use_conflicts("industry", box(400, 0, 500, 100), self.parts), [])


if __name__ == "__main__":
    unittest.main()
