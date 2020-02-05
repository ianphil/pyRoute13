#!/usr/bin/env python

import unittest

from environment import trace, cart_factory, environment


class Environment_Integraton_TestSuite(unittest.TestCase):
    """Ingegration Tests for Environment Module"""

    # TODO: Move over to Timeline
    class clock:
        def __init__(self):
            self.time = 0

    def test_add_cart(self):
        tt = trace.TextTrace(self.clock(), trace.format_time_HMS, print)
        e = environment.Environment(1, 1, 1, 1, tt)

        cf = cart_factory.Cart_Factory()
        c1 = cf.cart(0, "gate a1", 5)
        e.add_cart(c1)
        self.assertEqual(len(e.fleet), 1)


if __name__ == "__main__":
    unittest.main()
