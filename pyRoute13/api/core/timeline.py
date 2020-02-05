#!/usr/bin/env python

import heapq
from abc import ABC, abstractmethod
from route13.core.agent import start


class SimTime(int):
    def __new__(cls, value=0):
        i = int.__new__(cls, value)
        return i


class Event(ABC):
    """Abstract class for events. Implements eq/lt for heapq order."""

    def __init__(self, time: SimTime, agent):
        self.time = time
        self.agent = agent

    @abstractmethod
    def __repr__(self):
        return "Event({})".format(self.time)

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time


class SimEvent(Event):
    def __init__(self, time: int, agent):
        super(SimEvent, self).__init__(time, agent)

    def __repr__(self):
        return "SimEvent({})".format(self.time)


class _TimeQueue:
    def __init__(self):
        self.heap = []

    def push(self, item: Event):
        heapq.heappush(self.heap, item)

    def pop(self) -> Event:
        event = None
        try:
            event = heapq.heappop(self.heap)
        except IndexError:
            pass
        return event


class Timeline:
    def __init__(self):
        self.queue = _TimeQueue()
        self.time = 0

    def main_loop(self):
        while True:
            event = self.queue.pop()
            if event:
                self.time = event.time
                start(event.agent)
            else:
                break

    def until(self, time: SimTime):
        def f(agent):
            self.queue.push(SimEvent(time, agent))

        return f
