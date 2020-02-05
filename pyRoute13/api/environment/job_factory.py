#!/usr/bin/env python

from route13.environment.job import OutOfServiceJob, OutOfServiceJobState
from route13.environment.job import TransferJob, TransferJobState


class JobFactory:
    def __init__(self):
        self._nextId = 0

    def out_of_service(self, suspendLocation, suspendTime, resumeTime):
        o = OutOfServiceJob()
        o.id = self._nextId
        self._nextId += 1
        o.state = OutOfServiceJobState.BEFORE_BREAK
        o.suspend_location = suspendLocation
        o.suspend_time = suspendTime
        o.resume_time = resumeTime

        return o

    def transfer(
        self, quantity, pickup_location, pickup_after, dropoff_location, dropoff_before,
    ):
        t = TransferJob()
        t.id = self._nextId
        self._nextId += 1
        t.state = TransferJobState.BEFORE_PICKUP
        t.quantity = quantity
        t.pickup_location = pickup_location
        t.pickup_after = pickup_after
        t.dropoff_location = dropoff_location
        t.dropoff_before = dropoff_before

        return t
