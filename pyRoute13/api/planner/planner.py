#!/usr/bin/env python

from typing import Generator, List, Tuple
from abc import ABC, abstractmethod
from route13.core.timeline import SimTime
from route13.environment.job import JobBase
from route13.environment.cart import Cart


class Assignment:
    def __init__(self):
        self.cart = None  # type: Cart
        self.jobs = []  # type: List[JobBase]
        self.score = None  # type: int


class Planner(ABC):
    @abstractmethod
    def create_assignment(
        self,
        jobs: Generator[JobBase, None, None],
        carts: Generator[Cart, None, None],
        time: SimTime,
    ) -> List[Tuple[Cart, Assignment]]:
        pass
