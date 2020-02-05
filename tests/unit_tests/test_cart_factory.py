#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from environment import trace, location, cart_factory


class Cart_TestSuite(unittest.TestCase):
    """Tests for Cart Factory Class"""

    # TODO: Move over to Timeline
    class clock:
        def __init__(self):
            self.time = 3

    def test_cart_factory(self):
        t = trace.TextTrace(self.clock(), trace.format_time_HMS, print)
        cf = cart_factory.Cart_Factory()
        c1 = cf.cart(0, "gate a1", 5)
        c2 = cf.cart(0, "gate a2", 10)
        t.cart_arrives(c1)
        t.cart_arrives(c2)

        u = [location.LocationId(0), location.LocationId(3)]
        f = [location.LocationId(1), location.LocationId(4)]
        t.cart_plan_is(c2, u, f)


if __name__ == "__main__":
    unittest.main()
