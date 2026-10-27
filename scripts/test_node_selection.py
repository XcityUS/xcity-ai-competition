"""Run with python -m unittest discover -s scripts -p 'test_*.py'."""
import itertools
import unittest

from node_selection import ROOT, selection_errors


class NodeSelectionTests(unittest.TestCase):
    def test_all_combinations(self):
        groups = [{"A01", "A02", "A03"}, {"B01", "B02", "B03"}, {"C01", "C02", "C03", "C04"}]
        for ids in itertools.combinations(["%s%02d" % (g,i) for g,n in (("A",3),("B",3),("C",4)) for i in range(1,n+1)], 3):
            with self.subTest(ids=ids):
                expected = all(len(set(ids) & group) == 1 for group in groups)
                self.assertEqual(not selection_errors(ids), expected)

    def test_no_directory_has_group_selection_exception(self):
        ids = ["A01", "A02", "A03"]
        self.assertTrue(selection_errors(ids, ROOT / "submissions/jingyuanhuang-design/finite-water-city"))
        self.assertTrue(selection_errors(ids, ROOT / "submissions/new/finite-water-city"))

    def test_requires_three_distinct_valid_ids(self):
        for ids in (["A01", "A01", "B01"], ["A01", "B01", "Z99"], ["A01", "B01"]):
            self.assertTrue(selection_errors(ids, ROOT / "submissions/EXAMPLE-agent/sample-scheme"))


if __name__ == "__main__":
    unittest.main()
