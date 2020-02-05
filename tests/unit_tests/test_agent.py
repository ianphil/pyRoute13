#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

import unittest
from core.agent import start


class Agent_TestSuite(unittest.TestCase):
    """Tests for Agent Class"""

    def test_agent_start(self):
        class TempTest:
            def __init__(self):
                self.count = 0
                self._increment_counter(3)

            def _action(self):
                yield self._q()

            def _q(self):
                def f(item):
                    self.count += 1

                return f

            def _increment_counter(self, inc):
                for i in range(inc):
                    start(self._action())

        tt = TempTest()

        self.assertEqual(3, tt.count)


if __name__ == "__main__":
    unittest.main()
