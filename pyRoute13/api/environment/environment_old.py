#!/usr/bin/env python
from collections import OrderedDict
from copy import deepcopy

from api.core.logger import Logger
from api.environment.cart import Cart
from api.environment.job import JobBase
from api.environment.trace import Trace
from api.planner.route_planner import RoutePlanner
from api.planner.route_calculator import RouteCalculator


class Environment:
    def __init__(
        self,
        max_of_jobs: int,
        load_time_estimator,
        unload_time_estimator,
        route_next_step,
        transit_time_estimator,
        route_calculator: RouteCalculator,
        logger: Logger,
        trace: Trace,
    ):

        self.max_jobs = max_of_jobs
        self.load_time_estimator = load_time_estimator
        self.route_next_step = route_next_step
        self.unload_time_estimator = unload_time_estimator
        self.transit_time_estimator = transit_time_estimator
        self._trace = trace  # type: Trace
        self._logger = logger  # type: Logger
        self.route_planner = RoutePlanner(
            self.max_jobs,
            self.load_time_estimator,
            self.unload_time_estimator,
            self.transit_time_estimator,
            route_calculator,
            None
            # self._logger
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

    def job_snapshot(self, cart_copy):
        copy = OrderedDict()

        for j in self.jobs:
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
            self.jobs.move_to_end(job.id)
            self.jobs.popitem(job.id)
            self.successful_jobs.append(job)
        except KeyError:
            pass

        if self._trace is not None:
            self._trace.job_succeeded(job)

    def fail_job(self, job: JobBase):
        self.jobs.move_to_end(job.id)
        self.jobs.popitem(job.id)

        self.failed_jobs.append(job)  # MBR Calc

        if self._trace is not None:
            self._trace.job_failed(job)
