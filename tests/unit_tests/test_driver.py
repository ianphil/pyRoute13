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
from agents.driver import Driver
from environment.cart_factory import Cart_Factory

# from environment.job_factory import JobFactory
from core.agent import start


class Driver_TestSuite(unittest.TestCase):
    """Tests for Driver Class"""

    def test_wait_for_next_plan(self):
        (timeline, trace, environment, simple_dispatcher, driver,) = setup_classes()

        cart_factory = Cart_Factory()
        cart_count = 3

        for i in range(cart_count):
            cart = cart_factory.cart(10, 0)
            environment.add_cart(cart)
            start(driver.drive(cart))


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
    driver = Driver(timeline, simple_dispatcher, environment, trace)

    return timeline, trace, environment, simple_dispatcher, driver


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
