#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

import unittest
from core.condition import Condition


class Condition_TestSuite(unittest.TestCase):
    """Tests for Condition Class"""

    def test_condition_sleep(self):
        count_queue = []

        def _action():
            yield _q()

        def _q():
            def f(item):
                count_queue.append(item)

            return f

        c = Condition()
        c.sleep(_action())
        self.assertEqual(1, len(c.agents))

        c.pending_wakeups += 1
        c.sleep(_action())

        self.assertEqual(1, len(count_queue))

    def test_condition_wake_all(self):
        count_queue = []

        def _action():
            yield _q()

        def _q():
            def f(item):
                count_queue.append(item)

            return f

        c = Condition()
        c.sleep(_action())
        self.assertEqual(1, len(c.agents))

        c.sleep(_action())
        c.pending_wakeups += 1
        self.assertEqual(2, len(c.agents))
        self.assertEqual(0, len(count_queue))

        c.wake_all()
        self.assertEqual(2, len(count_queue))
        self.assertEqual(0, c.pending_wakeups)

    def test_condition_wake_one(self):
        count_queue = []

        def _action():
            yield _q()

        def _q():
            def f(item):
                count_queue.append(item)

            return f

        c = Condition()
        c.sleep(_action())
        self.assertEqual(1, len(c.agents))

        c.wake_one()

        self.assertEqual(1, len(count_queue))

        c.wake_one()
        self.assertEqual(1, c.pending_wakeups)


if __name__ == "__main__":
    unittest.main()
