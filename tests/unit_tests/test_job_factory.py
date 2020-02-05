#!/usr/bin/env python
# -*- coding: utf-8 -*-
if __debug__:
    import os
    import sys

    sys.path.insert(
        0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    )

import unittest
from environment import trace, location, job, job_factory


class Job_TestSuite(unittest.TestCase):
    """Tests for Job Class"""

    def test_Job(self):
        o = job.OutOfServiceJob()
        self.assertEqual(o.job_type, job.JobType.OUT_OF_SERVICE)

        t = job.TransferJob()
        self.assertEqual(t.job_type, job.JobType.TRANSFER)

    # TODO: Move over to Timeline
    class clock:
        def __init__(self):
            self.time = 3

    def test_job_factory(self):
        t = trace.TextTrace(self.clock(), trace.format_time_HMS, print)
        jf = job_factory.JobFactory()
        j1 = jf.out_of_service(location.LocationId(0), 3, 4)
        t.job_introducted(j1)

        j2 = jf.out_of_service(location.LocationId(2), 3, 4)
        t.job_introducted(j2)

        j3 = jf.transfer(5, location.LocationId(2), 5, location.LocationId(0), 6)
        t.job_introducted(j3)


if __name__ == "__main__":
    unittest.main()
