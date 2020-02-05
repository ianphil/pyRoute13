#!/usr/bin/env python
# -*- coding: utf-8 -*-
if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

import unittest
from core.timeline import Timeline, SimEvent


class Timeline_TestSuite(unittest.TestCase):
    """Tests for Timeline Class"""

    def test_timeline_main_loop(self):
        event_results = []

        def _action():
            yield _q()

        def _q():
            def f(item):
                event_results.append(item)

            return f

        e = SimEvent(1, _action())

        t = Timeline()
        t.queue.push(e)
        t.main_loop()

        self.assertEqual(1, len(event_results))

    def test_timeline_until(self):
        event_results = []

        def _action():
            yield _q()

        def _q():
            def f(item):
                event_results.append(item)

            return f

        e1 = SimEvent(1, _action())
        e2 = SimEvent(2, _action())

        t = Timeline()
        t.queue.push(e1)
        t.until(e2.time)(e2.agent)

        t.main_loop()

        self.assertEqual(2, len(event_results))


if __name__ == "__main__":
    unittest.main()
