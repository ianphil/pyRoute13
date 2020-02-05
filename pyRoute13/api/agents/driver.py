#!/usr/bin/env python
from typing import Generator, Callable
from route13.core import timeline
from route13.agents import dispatcher
from route13.environment import cart, environment, job, location, trace
from route13.planner import route


class Driver:
    def __init__(
        self,
        timeline: timeline.Timeline,
        dispatcher: dispatcher.Dispatcher,
        env: environment.Environment,
        trace: trace.Trace,
    ):
        self._timeline = timeline
        self._dispatcher = dispatcher
        self._env = env
        self._trace = trace

    def drive(self, cart: cart.Cart) -> Generator[Callable, None, None]:
        _current_plan_time = float("-inf")
        while True:
            yield from self._dispatcher.wait_for_next_plan(_current_plan_time)

            if self._dispatcher.is_shutting_down():
                break

            _current_plan_time = self._timeline.time
            _jobs = self._dispatcher.get_plan(cart, self._env.jobs)
            if len(_jobs) > 0:
                yield from self._find_route_and_go(cart, _current_plan_time, _jobs)

    def _find_route_and_go(self, cart: cart.Cart, current_plan_time: int, jobs: list):
        _route = False

        try:
            _route = self._env.route_planner.get_best_route(
                cart, jobs, self._timeline.time
            )
        except Exception:
            pass

        if not _route:
            (self._env.fail_job(j) for j in jobs)

        else:
            for action in _route.actions:
                if self._dispatcher.newer_plan_available(current_plan_time):
                    break

                try:
                    yield from self._perform_one_action(cart, action)
                except TypeError:
                    pass

    def _perform_action_sequence(self, cart: cart.Cart, actions: list):
        for action in actions:
            yield from self._perform_one_action(cart, action)

    def _perform_one_action(self, cart: cart.Cart, action: route.ActionBase):
        def dropoff_action(self, cart, action):
            yield from self._dropoff(cart, action)

        def pickup_action(self, cart, action):
            yield from self._pickup(cart, action)

        def suspend_action(self, cart, action):
            yield from self._suspend(cart, action)

        action_cases = {
            route.ActionType.DROPOFF: dropoff_action,
            route.ActionType.PICKUP: pickup_action,
            route.ActionType.SUSPEND: suspend_action,
        }

        try:
            return action_cases[action.type](self, cart, action)
        except KeyError:
            pass
        except AttributeError:
            pass

    def _pickup(self, cart: cart.Cart, action: route.PickupAction):
        yield from self._drive_to(cart, action.location)
        yield from self._wait_until(cart, action.time)

        action.job.state = job.TransferJobState.ENROUTE
        self._env.assign_job(action.job, cart)

        yield from self._load(cart, action.quantity)

    def _dropoff(self, cart: cart.Cart, action: route.DropoffAction):
        yield from self._drive_to(cart, action.location)
        yield from self._unload(cart, action.quantity)
        self._env.complete_job(action.job)

    def _suspend(self, cart: cart.Cart, action: route.SuspendAction):
        yield from self._drive_to(cart, action.location)

        if self._trace:
            self._trace.cart_suspends_service(cart)

        action.job.state = job.OutOfServiceJobState.ON_BREAK
        yield from self._wait_until(cart, action.resume_time)

        if self._trace:
            self._trace.cart_resumes_service(cart)

        self._env.complete_job(action.job)

    def _drive_to(self, cart: cart.Cart, destination: location.LocationId):
        start = cart.last_known_location

        while cart.last_known_location != destination:
            next_location = self._env.route_next_step(
                cart.last_known_location, destination, self._timeline.time
            )
            drive_time = self._env.transit_time_estimator(
                cart.last_known_location, next_location, self._timeline.time
            )

            if self._trace:
                if cart.last_known_location == start:
                    self._trace.cart_departs(cart, destination)

            yield self._timeline.until(self._timeline.time + drive_time)
            if cart.last_known_location == next_location:
                break
            cart.last_known_location = next_location
            if self._trace:
                if cart.last_known_location == destination:
                    self._trace.cart_arrives(cart)
                else:
                    self._trace.cart_passes(cart)

    def _load(self, cart: cart.Cart, quantity: int):
        if cart.payload + quantity > cart.capacity:
            msg = "Cart {} with {} will exceed capacity loading {} itmes.".format(
                cart.id, cart.payload, quantity
            )
            raise ValueError(msg)

        if self._trace:
            self._trace.cart_begins_loading(cart, quantity)

        loading_finished_time = self._timeline.time + self._env.load_time_estimator(
            cart.last_known_location, quantity, self._timeline.time
        )
        yield self._timeline.until(loading_finished_time)
        cart.payload += quantity

        if self._trace:
            self._trace.cart_finishes_loading(cart)

    def _unload(self, cart: cart.Cart, quantity: int):
        if cart.payload < quantity:
            msg = "Cart {} with {} does not have {} items to unload.".format(
                cart.id, cart.payload, quantity
            )
            raise ValueError(msg)

        if self._trace:
            self._trace.cart_begins_unloading(cart, quantity)

        unloading_finished_time = self._timeline.time + self._env.unload_time_estimator(
            cart.last_known_location, quantity, self._timeline.time
        )
        yield self._timeline.until(unloading_finished_time)
        cart.payload -= quantity

        if self._trace:
            self._trace.cart_finishes_unloading(cart)

    def _wait_until(self, cart: cart.Cart, resume_time):
        if self._timeline.time < resume_time:
            if self._trace:
                self._trace.cart_waits(cart, resume_time)

            yield self._timeline.until(resume_time)
