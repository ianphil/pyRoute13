#!/usr/bin/env python

import math
import random
from typing import List
from scipy.stats import norm
from route13.core import timeline, agent
from route13.environment import location, job, job_factory

random.seed("seed1")


class JourneyId(int):
    def __new__(cls, value=0):
        i = int.__new__(cls, value)
        return i


class Arrival:
    def __init__(self):
        self.id = None  # type: JourneyId
        self.time = None  # type: timeline.SimTime
        self.location = None  # type: location.LocationId
        self.earliest_connection = None  # type: int


class Depature:
    def __init__(self):
        self.id = None  # type: JourneyId
        self.time = None  # type: timeline.SimTime
        self.location = None  # type: location.LocationId


class Turnaround:
    def __init__(self):
        self.arrival = None  # type: Arrival
        self.depature = None  # type: Depature
        self.jobs = None  # type: list[job.TransferJob]


class Berth:
    def __init__(self):
        self.location = None  # type: location.LocationId


class IdFactory:
    def __init__(self):
        self.next_id = 0  # type: int

    def id(self) -> int:
        self.next_id += 1
        return self.next_id


class TransferGenerator:
    def __init__(
        self,
        arrival_count: int,
        earliest_arrival_time: timeline.SimTime,
        latest_arrival_time: timeline.SimTime,
        turn_around_time: timeline.SimTime,
        min_connection_time: timeline.SimTime,
        max_items_per_transfer: int,
    ):

        self._arrivals = []  # type: List[Arrival]
        self._depatures = []  # type: List[Depature]
        self._turn_arounds = []  # type: List[Turnaround]
        self._berths = []  # type: List[location.LocationId]
        self._transfers = []  # type: List[job.TransferJob]

        self._min_connection_time = min_connection_time
        self._max_items_per_transfer = max_items_per_transfer
        self._turn_around_time = turn_around_time
        self._distribution = norm(
            loc=min_connection_time * 1.5,
            scale=25 * min_connection_time * min_connection_time,
        )
        self._berth_factory = IdFactory()
        self._journey_factory = IdFactory()
        self._job_factory = job_factory.JobFactory()
        self._timeline = timeline.Timeline()

        for i in range(arrival_count):
            self._arrivals.append(
                self._random_arrival(earliest_arrival_time, latest_arrival_time)
            )

        for arrival in self._arrivals:
            turn_arround = self._random_turn_around(arrival)
            self._turn_arounds.append(turn_arround)
            self._depatures.append(turn_arround.depature)

        for turn_arround in self._turn_arounds:
            agent.start(self._assign_berth(turn_arround))

        self._timeline.main_loop()

        self._arrivals.sort(key=lambda a: a.time)
        self._depatures.sort(key=lambda a: a.time)

        self._determine_earliest_connections()

        for turn_around in self._turn_arounds:
            arrival = turn_around.arrival
            for transfer in self._random_transfer_jobs(arrival):
                self._transfers.append(transfer)
                turn_around.jobs.append(transfer)

        self._turn_arounds = sorted(
            self._turn_arounds, key=lambda a: a.arrival.location
        )
        self._turn_arounds = sorted(self._turn_arounds, key=lambda a: a.arrival.time)

    def berth_count(self) -> int:
        return len(self._berths)

    def jobs(self):
        yield from self._transfers

    def get_job_count(self) -> int:
        return len(self._transfers)

    def get_turn_arounds(self):
        yield from self._turn_arounds

    def get_turn_around_counts(self):
        return len(self._turn_arounds)

    def _determine_earliest_connections(self):
        if len(self._depatures) > 0:
            earliest_connection = 0
            for arrival in self._arrivals:
                while (
                    self._depatures[earliest_connection].time - arrival.time
                    < self._min_connection_time
                ):
                    earliest_connection += 1
                    if earliest_connection == len(self._depatures):
                        return
                arrival.earliest_connection = earliest_connection

    def _assign_berth(self, turn_around: Turnaround):
        yield self._timeline.until(turn_around.arrival.time)
        berth = self._allocate_random_berth()
        turn_around.arrival.location = berth
        turn_around.depature.location = berth
        yield self._timeline.until(turn_around.depature.time)
        self._release_berth(berth)

    def _allocate_random_berth(self) -> location.LocationId:
        if len(self._berths) == 0:
            berth = self._berth_factory.id()
            return berth
        elif len(self._berths) == 1:
            berth = self._berths.pop()  # type: location.LocationId
            return berth
        else:
            index = self._random_in_range(0, len(self._berths))
            temp = self._berths[index]
            self._berths[index] = self._berths[0]
            self._berths.pop(0)
            return temp

    def _release_berth(self, berth: location.LocationId) -> None:
        self._berths.append(berth)

    def _random_arrival(
        self,
        earliest_arrival_time: timeline.SimTime,
        latest_arrival_time: timeline.SimTime,
    ) -> Arrival:
        id = self._journey_factory.id()
        time = self._random_in_range(earliest_arrival_time, latest_arrival_time)

        arrival = Arrival()
        arrival.id = id
        arrival.time = time
        return arrival

    def _random_turn_around(self, arrival: Arrival) -> Turnaround:
        id = self._journey_factory.id()
        time = arrival.time + self._turn_around_time

        turn_arround = Turnaround()
        turn_arround.arrival = arrival
        turn_arround.depature = Depature()
        turn_arround.depature.id = id
        turn_arround.depature.time = time
        turn_arround.jobs = []
        return turn_arround

    def _random_transfer_jobs(self, arrival: Arrival):
        if arrival.earliest_connection is not None:
            i = arrival.earliest_connection
            # job_limiter = 3
            while i < len(self._depatures):
                try:
                    depature = self._depatures[i]
                    if arrival.location is not depature.location:
                        connection_time = depature.time - arrival.time
                        mean = self._distribution.mean()
                        conn_dist = self._distribution.pdf(connection_time)
                        mean_dist = self._distribution.pdf(mean)
                        p = min([conn_dist / mean_dist, 0.39])
                        r = random.random()
                        if r < p:
                            quantity = self._random_natural_number(
                                self._max_items_per_transfer
                            )

                            job = self._job_factory.transfer(
                                quantity,
                                arrival.location,
                                arrival.time,
                                depature.location,
                                depature.time,
                            )

                            # if job_limiter == 0: break
                            # job_limiter -= 1

                            yield job
                finally:
                    i += 1

    def _random_in_range(self, start: int, end: int) -> int:
        if end < start:
            raise ValueError("End cannot be less than start")
        return random.randrange(start, end)

    def _random_natural_number(self, max: int) -> int:
        if max < 1:
            raise ValueError("Max cannot be less than 1.")
        return 1 + math.floor(random.random() * max)
