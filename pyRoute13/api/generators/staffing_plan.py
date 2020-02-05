#!/usr/bin/env python

from typing import List, Dict
from route13.environment import location, cart_factory, job_factory, job, cart
from route13.core import timeline, agent, time


class Interval:
    def __init__(self):
        self.start = None     # type: timeline.SimTime
        self.end = None       # type: timeline.SimTime


class Break:
    def __init__(self):
        self.interval = None  # type: Interval
        self.location = None  # type: location.LocationId


class Shift:
    def __init__(self):
        self.name = None     # type: str
        self.working = None  # type: Interval
        self.breaks = []     # type: List[Break]
        self.home = None     # type: location.LocationId


class Crew:
    def __init__(self):
        self.shift = None    # type: Shift
        self.size = None     # type: int


class StaffingPlan:
    def __init__(self, crews):
        self._timeline = timeline.Timeline()
        self._cart_factory = cart_factory.Cart_Factory()
        self._job_factory = job_factory.JobFactory()
        self._cart_capacity = 10
        self._all_carts = []      # type: List[cart.Cart]
        self._break_periods = []  # type: List[job.OutOfServiceJob]

        # This next line actually uses a line continuation for the type
        # comment. ref:
        # https://github.com/python/mypy/issues/4511#issuecomment-360798876
        self._carts_waiting = dict() \
            # type: Dict[int, List[job.OutOfServiceJob]]

        self._generate_all_shifts(crews)
        self._timeline.main_loop()

    def carts(self):
        for _, fleet in self._carts_waiting.items():
            for c in fleet:  # type: job.OutOfServiceJob
                yield c.assignedTo  # type: cart.Cart

    def jobs(self):
        yield from self._break_periods

    def _generate_all_shifts(self, crews: List[Crew]):
        for crew in crews:  # type: Crew
            i = 0
            while (i < crew.size):
                try:
                    agent.start(self._generate_one_shift(crew.shift))
                finally:
                    i += 1

    def _generate_one_shift(self, shift: Shift):
        yield self._timeline.until(shift.working.start)
        end_of_last_shift = self._allocate_cart(shift.home)
        cart = end_of_last_shift.assignedTo  # type: cart.Cart
        end_of_last_shift.resume_time = shift.working.start
        end_of_current_shift = self._create_Job(
            cart,
            shift.home,
            shift.working.end,
            time.MAX_DATE
        )

        for b in shift.breaks:  # type: Break
            self._create_Job(
                cart, b.location, b.interval.start, b.interval.end)

        yield self._timeline.until(shift.working.end)
        self._return_cart(end_of_current_shift)

    def _allocate_cart(self, home: location.LocationId) -> job.OutOfServiceJob:
        try:
            waiting = self._carts_waiting[home]  # type: List
            cart = waiting.pop()
            return cart
        except KeyError:
            self._carts_waiting[home] = []
            return self._create_cart(home)
        except IndexError:
            return self._create_cart(home)

    def _create_cart(self, home: location.LocationId) -> job.OutOfServiceJob:
        cart = self._cart_factory.cart(self._cart_capacity, home)
        self._all_carts.append(cart)
        out_of_service = self._create_Job(
            cart, home, time.MIN_DATE, time.MAX_DATE)

        return out_of_service

    def _return_cart(self, j: job.OutOfServiceJob):
        c = j.assignedTo  # type: cart.Cart
        jobs = self._carts_waiting[c.last_known_location]  # type: List
        jobs.append(j)

    def _create_Job(
            self,
            cart: cart.Cart,
            suspend_location: location.LocationId,
            suspend_time: timeline.SimTime,
            resume_time: timeline.SimTime) -> job.OutOfServiceJob:

        job = self._job_factory.out_of_service(
            suspend_location, suspend_time, resume_time)
        job.assignedTo = cart
        self._break_periods.append(job)
        return job


def standard_shift(
    name: str,
    start: timeline.SimTime,
    home: location.LocationId,
    break_room: location.LocationId
) -> Shift:
    s = Shift()
    s.name = name
    s.working = interval(start, 0, 8 * time.HOUR - 1)
    s.home = home

    b1 = Break()
    b1.location = break_room
    b1.interval = interval(
        start, 120 * time.MINUTE, 15 * time.MINUTE)

    b2 = Break()
    b2.location = break_room
    b2.interval = interval(
        start, 240 * time.MINUTE, 30 * time.MINUTE)

    b3 = Break()
    b3.location = break_room
    b3.interval = interval(
        start, 360 * time.MINUTE, 15 * time.MINUTE)

    s.breaks = [b1, b2, b3]
    return s


def interval(
    base: timeline.SimTime,
    offset: timeline.SimTime,
    length: timeline.SimTime
) -> Interval:
    i = Interval()
    i.start = base + offset
    i.end = base + offset + length
    return i


def adjust_interval(interval: Interval, offset: int) -> Interval:
    i = Interval()
    i.start = interval.start + offset
    i.end = interval.end + offset
    return i


def adjust_break(b: Break, offset: timeline.SimTime) -> Break:
    result = Break()
    result.interval = adjust_interval(b.interval, offset)
    result.location = b.location
    return result


def adjust_shift(name: str, shift: Shift, offset: int) -> Shift:
    s = Shift()
    s.name = name
    s.working = adjust_interval(shift.working, offset)
    s.breaks = [adjust_break(x, offset) for x in shift.breaks]
    s.home = shift.home
    return s


def contains(outer: Interval, inner: Interval) -> bool:
    result = outer.start < inner.start and \
        outer.start < inner.end and \
        outer.end > inner.start and \
        outer.end > inner.end

    return result
