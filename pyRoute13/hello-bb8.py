#!/usr/bin/env python
import os
import sys
import time as t

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.environment import cart_factory, environment, job_factory, trace
from api.core import agent, time, timeline
from api.agents import simple_dispatcher, driver


def go():
    start = t.perf_counter()
    _timeline = timeline.Timeline()
    _trace = trace.TextTrace(_timeline, trace.format_time_HMS, print)
    _environment = environment.Environment(
        load_time_estimator,
        unload_time_estimator,
        route_next_step,
        transit_time_estimator,
        _trace,
    )
    _dispatcher = simple_dispatcher.SimpleDispatcher(_timeline, _environment, _trace)

    _driver = driver.Driver(_timeline, _dispatcher, _environment, _trace)

    _cart_factory = cart_factory.Cart_Factory()
    cart_count = 3

    for i in range(cart_count):
        cart = _cart_factory.cart(10, 0)
        _environment.add_cart(cart)
        agent.start(_driver.drive(cart))

    _job_factory = job_factory.JobFactory()
    jobs = []
    jobs.append(_job_factory.transfer(5, 2, time.time(0, 3), 10, time.time(0, 30)))
    jobs.append(_job_factory.transfer(6, 2, time.time(0, 3), 4, time.time(0, 25)))
    jobs.append(_job_factory.out_of_service(9, time.time(0, 30), time.time(0, 40)))
    jobs.append(_job_factory.transfer(9, 7, time.time(0, 13), 4, time.time(0, 27)))

    introduce_at = 0
    for j in jobs:
        agent.start(_dispatcher.introduce_job(j, introduce_at))

    agent.start(_dispatcher.shutdown_at(time.time(0, 59)))

    _timeline.main_loop()

    print("Simulation ended.")
    end = t.perf_counter()
    print((end - start) * 1000)


def load_time_estimator(location, quantity, start_time):
    return 30 * time.SECOND * quantity


def unload_time_estimator(location, quantity, start_time):
    return 10 * time.SECOND * quantity


def transit_time_estimator(origin, destination, start_time):
    return abs(destination - origin) * time.MINUTE


def route_next_step(origin, destination, t):
    if origin < destination:
        return origin + 1
    elif origin > destination:
        return origin - 1
    else:
        return origin


if __name__ == "__main__":
    go()
