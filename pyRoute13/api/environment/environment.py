#!/usr/bin/env python

from route13.environment.cart import Cart
from route13.environment.job import JobBase
from route13.environment.trace import Trace
from route13.planner.route_planner import RoutePlanner
from collections import OrderedDict
from copy import deepcopy


class Environment:
    def __init__(
        self,
        load_time_estimator,
        unload_time_estimator,
        route_next_step,
        transit_time_estimator,
        trace,
    ):

        self.load_time_estimator = load_time_estimator
        self.route_next_step = route_next_step
        self.unload_time_estimator = unload_time_estimator
        self.transit_time_estimator = transit_time_estimator
        self._trace = trace  # type: Trace
        self.route_planner = RoutePlanner(
            3,
            self.load_time_estimator,
            self.unload_time_estimator,
            self.transit_time_estimator,
            None,
        )
        self.fleet = OrderedDict()
        self.jobs = OrderedDict()
        self.successful_jobs = []
        self.failed_jobs = []

    def add_cart(self, cart: Cart):
        if cart.id in self.fleet:
            pass
        else:
            self.fleet[cart.id] = cart

    def cart_snapshot(self):
        return deepcopy(self.fleet)

    def job_snapshot(self):
        copy = OrderedDict()

        for _, j in self.jobs.items():
            assigned_to = None
            if j.assigned_to is not None:
                assigned_to = copy.get(j.assigned_to.id)
            copy[j.id] = j, assigned_to

        return copy

    def add_job(self, job: JobBase):
        if self._trace is not None:
            self._trace.job_introducted(job)

        self.jobs[job.id] = job

    def assign_job(self, job: JobBase, cart: Cart):
        job.assigned_to = cart

        if self._trace is not None:
            self._trace.job_assigned(job)

    def complete_job(self, job: JobBase):
        try:
            self.jobs.pop(job.id)
        except KeyError:
            pass

        if job in self.successful_jobs:
            raise ValueError("Completed job a second time.")

        self.successful_jobs.append(job)

        if self._trace is not None:
            self._trace.job_succeeded(job)

    def fail_job(self, job: JobBase):
        try:
            self.jobs.pop(job.id)
        except KeyError:
            pass

        self.failed_jobs.append(job)  # MBR Calc

        if self._trace is not None:
            self._trace.job_failed(job)
