"""Run with python -m unittest discover -s scripts -p 'test_*.py'."""
import itertools
import unittest

from node_selection import ROOT, selection_errors


class NodeSelectionTests(unittest.TestCase):
    def test_all_combinations(self):
        groups = [{"N02", "N08", "N10"}, {"N03", "N04", "N05"}, {"N01", "N06", "N07", "N09"}]
        for ids in itertools.combinations(["N%02d" % i for i in range(1, 11)], 3):
            with self.subTest(ids=ids):
                expected = all(len(set(ids) & group) == 1 for group in groups)
                self.assertEqual(not selection_errors(ids), expected)

    def test_legacy_exception_is_path_bound(self):
        ids = ["N02", "N08", "N10"]
        self.assertFalse(selection_errors(ids, ROOT / "submissions/jingyuanhuang-design/finite-water-city"))
        self.assertTrue(selection_errors(ids, ROOT / "submissions/new/finite-water-city"))

    def test_legacy_still_requires_three_distinct_valid_ids(self):
        for ids in (["N02", "N02", "N03"], ["N02", "N03", "N99"], ["N02", "N03"]):
            self.assertTrue(selection_errors(ids, ROOT / "submissions/EXAMPLE-agent/sample-scheme"))


if __name__ == "__main__":
    unittest.main()
