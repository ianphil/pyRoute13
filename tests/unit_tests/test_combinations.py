#!/usr/bin/env python
# -*- coding: utf-8 -*-
from planner.combinations import combinations
import unittest

if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )


class Job_TestSuite(unittest.TestCase):
    """Tests for Combinations function"""

    def test_Combinations_1_of_8(self):
        combo_expected = [[0], [1], [2], [3], [4], [5], [6], [7]]
        combo_observed = list(combinations(1, 8))
        self.assertEqual(combo_observed, combo_expected)

    def test_Combinations_2_of_8(self):
        combo_expected = [
            [0, 1],
            [0, 2],
            [0, 3],
            [0, 4],
            [0, 5],
            [0, 6],
            [0, 7],
            [1, 2],
            [1, 3],
            [1, 4],
            [1, 5],
            [1, 6],
            [1, 7],
            [2, 3],
            [2, 4],
            [2, 5],
            [2, 6],
            [2, 7],
            [3, 4],
            [3, 5],
            [3, 6],
            [3, 7],
            [4, 5],
            [4, 6],
            [4, 7],
            [5, 6],
            [5, 7],
            [6, 7],
        ]
        combo_observed = list(combinations(2, 8))
        self.assertEqual(combo_observed, combo_expected)


if __name__ == "__main__":
    unittest.main()
