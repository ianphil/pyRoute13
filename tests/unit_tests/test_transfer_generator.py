#!/usr/bin/env python
# -*- coding: utf-8 -*-
if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

import unittest
from generators.transfer_generator import IdFactory, TransferGenerator
from core import time


class Transfer_Generator_TestSuite(unittest.TestCase):
    """Tests for Transfer Generator Classes"""

    @classmethod
    def setUpClass(cls):
        arrival_count = 20
        earliest_arrival_time = time.time(8, 0)  # 8:00
        latest_arrival_time = time.time(22, 59)  # 22:59
        turn_around_time = 1 * time.HOUR
        min_connection_time = 30 * time.MINUTE
        max_items_per_transfer = 5

        cls._generator = TransferGenerator(
            arrival_count,
            earliest_arrival_time,
            latest_arrival_time,
            turn_around_time,
            min_connection_time,
            max_items_per_transfer,
        )

    def test_Id_Factory(self):
        id_factory = IdFactory()
        self.assertEqual(1, id_factory.id())
        self.assertEqual(2, id_factory.id())
        self.assertEqual(3, id_factory.id())

    def test_init_berth_count(self):
        count = self._generator.berth_count()
        self.assertEqual(3, count)

    def test_init_turn_around_count(self):
        count = self._generator.get_turn_around_counts()
        self.assertEqual(20, count)

    def test_init_job_count(self):
        count = self._generator.get_job_count()
        self.assertEqual(0, count)

    def test_turn_arounds(self):
        for turn_around in self._generator.get_turn_arounds():
            arrival = turn_around.arrival
            self.assertEqual(1, arrival.id)

            departure = turn_around.depature
            self.assertEqual(21, departure.id)

            self.assertEqual(0, len(turn_around.jobs))

            self._generator = TransferGenerator()

            break


if __name__ == "__main__":
    unittest.main()
