#!/usr/bin/env python
from api.core.timeline import Timeline
from api.core.condition import Condition
from api.environment.job import JobBase
from api.environment.cart import Cart
from api.environment.environment import Environment
from api.environment.trace import Trace
from api.agents.dispatcher import Dispatcher


class SimpleDispatcher(Dispatcher):
    def __init__(self, timeline: Timeline, env: Environment, trace: Trace):
        self._timeline = timeline
        self._env = env
        self._trace = trace
        self._shutting_down = False
        self._unallocated_job = []
        self._job_available_condition = Condition()

    def wait_for_next_plan(self, plan_time: int):
        if not self._shutting_down:
            yield self._wait_for_job()

    def newer_plan_available(self, plan_time: int) -> bool:
        return False

    def get_current_plan_time(self) -> int:
        return self._timeline.time

    def get_plan(self, cart: Cart, jobs) -> list:
        jobs = []

        try:
            job = self._unallocated_job.pop()
            jobs.append(job)
        except IndexError:
            pass

        if self._trace:
            self._trace.cart_plan_is(cart, jobs, jobs)

        return jobs

    def introduce_job(self, job: JobBase, time: int):
        yield self._timeline.until(time)
        self._env.add_job(job)
        self._unallocated_job.append(job)
        self._job_available_condition.wake_one()

    def planning_loop(self):
        pass

    def shutdown_at(self, time: int):
        yield self._timeline.until(time)
        self._shutting_down = True

    def is_shutting_down(self) -> bool:
        return self._shutting_down

    def _wait_for_job(self):
        def f(agent):
            self._job_available_condition.sleep(agent)

        return f
