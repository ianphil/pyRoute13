#!/usr/bin/env python

from enum import Enum
from route13.environment.cart import Cart


class JobType(str, Enum):
    OUT_OF_SERVICE = "out_of_service"
    TRANSFER = "transfer"


class OutOfServiceJobState(str, Enum):
    BEFORE_BREAK = "before_break"
    ON_BREAK = "on_break"


class TransferJobState(str, Enum):
    BEFORE_PICKUP = "before_pickup"
    ENROUTE = "enroute"


class JobBase:
    def __init__(self):
        self.id = None
        self.job_type = None
        self.assigned_to = None  # type: Cart


class OutOfServiceJob(JobBase):
    def __init__(self):
        super(OutOfServiceJob, self).__init__()
        self.job_type = JobType.OUT_OF_SERVICE
        self.state = None
        self.suspend_location = None
        self.suspend_time = None
        self.resume_time = None


class TransferJob(JobBase):
    def __init__(self):
        super(TransferJob, self).__init__()
        self.job_type = JobType.TRANSFER
        self.state = None
        self.quantity = None  # Bag quantity
        self.pickup_location = None  # Inbound/Arrival Gate
        self.pickup_after = None  # Actual Arrival time
        self.dropoff_location = None  # Outbound Gate
        self.dropoff_before = None  # Scheduled depature time
