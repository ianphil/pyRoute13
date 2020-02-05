#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from generators.jobs import jobs_reader as job

UnitDir = os.path.dirname(__file__)
DATA = os.path.join(UnitDir, "..\..\generators\jobs\data")
start_date = "09-20-2018"
end_date = "09-21-2018"
data_folder = "data"
file_base_name = "MSBI_2018_Bag_XFR_Part1"
date_format = "%Y%m%d %H:%M:%S"
parse_dates = ["Actl_Arr_LTs", "Schd_Dprt_LTs"]
dtypes = {
    "Orig": str,
    "ArrFlightNum": str,
    "Ib_Gt_Id": str,
    "Dest": str,
    "DepFlightNum": str,
    "Ob_Gt_Id": str,
    "BagsCount": int,
}
sort_by = "Actl_Arr_LTs"
data_file_name = file_base_name + "_" + start_date + "_" + end_date


class JobLoad_TestSuite(unittest.TestCase):
    """Tests for Jobs Load Class"""

    data_folder = "Data"

    # TODO: Move over to Timeline
    class clock:
        def __init__(self):
            self.time = 3

    def datafile(self):
        return os.path.join(DATA, data_file_name)

    def test_data_open(self):
        datafile = self.datafile() + ".csv"
        print("Data file={}".format(datafile))
        self.assertTrue(os.path.isfile(datafile))

    def test_jobs_load(self):
        # Load Bags data
        reader = job.JobsReader(
            data_folder, data_file_name, date_format, parse_dates, dtypes, sort_by,
        )
        reader.loadJobsData()

        self.assertEqual(reader.totalRows, 27575)


if __name__ == "__main__":
    unittest.main()
