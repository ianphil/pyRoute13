#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

import unittest
from generators.staffing_plan import (
    StaffingPlan,
    Crew,
    standard_shift,
    adjust_shift,
)
from core.time import HOUR


class Staffing_Generator_TestSuite(unittest.TestCase):
    """Tests for Staffing Generator Classes"""

    @classmethod
    def setUpClass(cls):
        home = 0
        break_room = 7

        day = standard_shift("Day Shift", 8 * HOUR, home, break_room)
        swing = adjust_shift("Swing Shift", day, 8 * HOUR)

        crews = []

        c1 = Crew()
        c1.shift = day
        c1.size = 3
        crews.append(c1)

        c2 = Crew()
        c2.shift = swing
        c2.size = 2
        crews.append(c2)

        cls._staff = StaffingPlan(crews)

    @classmethod
    def tearDownClass(cls):
        cls._staff = None

    def test_carts(self):
        carts = sorted([cart for cart in self._staff.carts()], key=lambda a: a.id)
        self.assertEqual(1, carts[0].id)
        self.assertEqual(2, carts[1].id)
        self.assertEqual(3, carts[2].id)

    def test_jobs(self):
        jobs = sorted([job for job in self._staff.jobs()], key=lambda a: a.id)
        self.assertEqual(1, jobs[0].id)
        self.assertEqual(2, jobs[1].id)
        self.assertEqual(3, jobs[2].id)

    def test_standard_shift(self):
        home = 0
        break_room = 7
        day = standard_shift("Day Shift", 8 * HOUR, home, break_room)
        self.assertEquals(3, len(day.breaks))
        self.assertEqual(57599999, day.working.end)
        self.assertEqual(28800000, day.working.start)
        self.assertEqual("Day Shift", day.name)
        self.assertEqual(0, day.home)

    def test_adjust_shift(self):
        home = 0
        break_room = 7
        day = standard_shift("Day Shift", 8 * HOUR, home, break_room)
        swing = adjust_shift("Swing Shift", day, 8 * HOUR)
        self.assertEquals(3, len(swing.breaks))
        self.assertEqual(86399999, swing.working.end)
        self.assertEqual(57600000, swing.working.start)
        self.assertEqual("Swing Shift", swing.name)
        self.assertEqual(0, swing.home)


if __name__ == "__main__":
    unittest.main()
