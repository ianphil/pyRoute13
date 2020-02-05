#!/usr/bin/env python
import os
import sys
import time as t

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from argparse import ArgumentParser
from route13.core.timeline import Timeline
from route13.environment.trace import TextTrace, format_time_HMS
from route13.environment.environment import Environment
from route13.core.time import HOUR, MINUTE, SECOND, time
from route13.planner.job_assigner import JobAssigner
from route13.agents.simple_dispatcher import SimpleDispatcher
from route13.agents.planning_loop_dispatcher import PlanningLoopDispatcher
from route13.agents.driver import Driver
from route13.environment.cart_factory import Cart_Factory
from route13.core.agent import start
from route13.generators.transfer_generator import TransferGenerator
from route13.environment.job import TransferJob


def main():
    s = t.perf_counter()
    parser = ArgumentParser()
    parser.add_argument("--simple", action="store_true")
    args = parser.parse_args()

    timeline = Timeline()
    trace = TextTrace(timeline, format_time_HMS, print)
    environment = Environment(
        load_time_estimator,
        unload_time_estimator,
        route_next_step,
        transit_time_estimator,
        trace,
    )

    max_job_count = 3
    planner = JobAssigner(
        max_job_count,
        load_time_estimator,
        unload_time_estimator,
        transit_time_estimator,
    )

    planning_start_time = time(7, 45)
    planning_interval = time(0, 15)

    dispatcher = None

    if args.simple:
        dispatcher = SimpleDispatcher(timeline, environment, trace)
    else:
        dispatcher = PlanningLoopDispatcher(
            timeline,
            environment,
            trace,
            planning_start_time,
            planning_interval,
            planner,
        )

    driver = Driver(timeline, dispatcher, environment, trace)

    cart_factory = Cart_Factory()
    cart_count = 3
    for x in range(cart_count):
        cart = cart_factory.cart(10, 0)
        environment.add_cart(cart)
        start(driver.drive(cart))

    arrival_count = 20
    earliest_arrival_time = time(8, 0)
    latest_arrival_time = time(22, 59)
    turn_around_time = 1 * HOUR
    min_connection_time = 30 * MINUTE
    max_items_per_transfer = 5
    transfers = TransferGenerator(
        arrival_count,
        earliest_arrival_time,
        latest_arrival_time,
        turn_around_time,
        min_connection_time,
        max_items_per_transfer,
    )

    last_berth = None
    for turn_around in transfers.get_turn_arounds():
        arrival = turn_around.arrival
        if arrival.location != last_berth:
            print("")
            print("Berth {}".format(arrival.location))
            last_berth = arrival.location
        depature = turn_around.depature
        print(
            "  Inbound #{} at {} => Outbound #{} at {}".format(
                arrival.id,
                format_time_HMS(arrival.time),
                depature.id,
                format_time_HMS(depature.time),
            )
        )
        for job in turn_around.jobs:  # type: TransferJob
            transfer_time = job.dropoff_before - job.pickup_after
            msg = (
                "    Job {}: move {} items from {} to {} between"
                " {} and {} ({})".format(
                    job.id,
                    job.quantity,
                    job.pickup_location,
                    job.dropoff_location,
                    format_time_HMS(job.pickup_after),
                    format_time_HMS(job.dropoff_before),
                    format_time_HMS(transfer_time),
                )
            )
            print(msg)
    print("")

    for job in transfers.jobs():  # type: TransferJob
        introduce_at = max([job.pickup_after - (15 * MINUTE), 0])
        start(dispatcher.introduce_job(job, introduce_at))

    start(dispatcher.planning_loop())

    start(dispatcher.shutdown_at(time(23, 59)))

    timeline.main_loop()

    scheduled_jobs = transfers.get_job_count()
    completed_jobs = len(environment.successful_jobs)
    failed_jobs = scheduled_jobs - completed_jobs

    print("Scheduled: {} jobs".format(scheduled_jobs))
    print("Completed: {} jobs".format(completed_jobs))
    print("Failed: {} jobs".format(failed_jobs))

    print("Simulation ended.")
    e = t.perf_counter()
    print((e - s) * 100)


def load_time_estimator(location, quantity, start_time):
    return 30 * SECOND * quantity


def unload_time_estimator(location, quantity, start_time):
    return 10 * SECOND * quantity


def transit_time_estimator(origin, destination, start_time):
    return abs(destination - origin) * MINUTE


def route_next_step(origin, destination, t):
    if origin < destination:
        return origin + 1
    elif origin > destination:
        return origin - 1
    else:
        return origin


if __name__ == "__main__":
    main()
