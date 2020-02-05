#!/usr/bin/env python
from abc import ABC, abstractmethod
from route13.environment.job import JobBase
from route13.environment.cart import Cart


class Dispatcher(ABC):
    @abstractmethod
    def wait_for_next_plan(self, plan_time: int):
        pass

    @abstractmethod
    def newer_plan_available(self, plan_time: int) -> bool:
        pass

    @abstractmethod
    def get_current_plan_time(self) -> int:
        pass

    @abstractmethod
    def get_plan(self, cart: Cart) -> list:
        pass

    @abstractmethod
    def introduce_job(self, job: JobBase, time: int):
        pass

    @abstractmethod
    def planning_loop(self):
        pass

    @abstractmethod
    def shutdown_at(self, time: int):
        pass

    @abstractmethod
    def is_shutting_down(self) -> bool:
        pass
