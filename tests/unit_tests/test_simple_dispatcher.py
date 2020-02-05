#!/usr/bin/env python
# -*- coding: utf-8 -*-
if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

import unittest
import math
from core.time import MINUTE, SECOND
from core.timeline import Timeline
from environment.environment import Environment
from environment.trace import TextTrace, format_time_HMS
from agents.simple_dispatcher import SimpleDispatcher

# from agents.driver import Driver
from environment.cart_factory import Cart_Factory
from environment.job_factory import JobFactory
from core.agent import start


class Simple_Dispatcher_TestSuite(unittest.TestCase):
    """Tests for Simple Dispatcher Class"""

    def test_wait_for_next_plan(self):
        timeline, trace, environment, simple_dispatcher = setup_classes()

        start(simple_dispatcher.wait_for_next_plan(float("-inf")))
        self.assertEqual(1, len(simple_dispatcher._job_available_condition.agents))

    def test_newer_plan_available(self):
        timeline, trace, environment, simple_dispatcher = setup_classes()

        val = simple_dispatcher.newer_plan_available(0)
        self.assertEqual(False, val)

    def test_get_current_plan_time(self):
        timeline, trace, environment, simple_dispatcher = setup_classes()

        val = simple_dispatcher.get_current_plan_time()
        self.assertEqual(0, val)

    def test_get_plan(self):
        timeline, trace, environment, simple_dispatcher = setup_classes()

        cf = Cart_Factory()
        val = simple_dispatcher.get_plan(cf.cart(10, 0), [])
        self.assertEqual(0, len(val))

    def test_introduce_job(self):
        timeline, trace, environment, simple_dispatcher = setup_classes()

        jf = JobFactory()
        job = jf.transfer(5, 0, 5, 1, 7)
        cf = Cart_Factory()
        cart = cf.cart(10, 0)
        job.assignedTo = cart
        start(simple_dispatcher.introduce_job(job, 0))
        simple_dispatcher._timeline.main_loop()
        self.assertEqual(1, len(simple_dispatcher._env.jobs))

    def test_shutting_down(self):
        timeline, trace, environment, simple_dispatcher = setup_classes()

        start(simple_dispatcher.shutdown_at(0))
        simple_dispatcher._timeline.main_loop()
        self.assertTrue(simple_dispatcher.is_shutting_down())


def setup_classes():
    timeline = Timeline()
    trace = TextTrace(timeline, format_time_HMS, print)
    environment = Environment(
        load_time_estimator,
        unload_time_estimator,
        route_next_step,
        transit_time_estimator,
        trace,
    )
    simple_dispatcher = SimpleDispatcher(timeline, environment, trace)

    return timeline, trace, environment, simple_dispatcher


def load_time_estimator(location, quantity, start_time):
    return 10 * SECOND * quantity


def unload_time_estimator(location, quantity, start_time):
    return 10 * SECOND * quantity


def transit_time_estimator(origin, destination, start_time):
    return math.fabs(destination - origin) * MINUTE


def route_next_step(origin, destination):
    if origin < destination:
        return origin + 1
    elif origin > destination:
        return origin - 1
    else:
        return origin


if __name__ == "__main__":
    unittest.main()
