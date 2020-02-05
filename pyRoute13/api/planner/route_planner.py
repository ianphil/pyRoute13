#!/usr/bin/env python

from typing import List, Generator, Dict
from api.core.timeline import SimTime
from api.environment.job import (
    JobType,
    OutOfServiceJobState,
    TransferJobState,
    OutOfServiceJob,
    TransferJob,
)
from api.environment.cart import Cart
from api.environment.location import LocationId
from api.estimators.estimators import (
    transit_time_estimator,
    load_time_estimator,
    unload_time_estimator,
)
from api.planner.route import (
    ActionType,
    ActionBase,
    DropoffAction,
    PickupAction,
    Route,
    SuspendAction,
)
from api.planner.trie import build_trie


class RouteState:
    def __init__(self):
        self.start_time = None  # type: SimTime
        self.time = None  # type: SimTime
        self.location = None  # type: LocationId
        self.payload = None  # type: int
        self.working_time = None  # type: SimTime
        self.quantity_unloaded = None  # type: int


def state_from_cart(cart: Cart, time: SimTime) -> RouteState:
    r = RouteState()
    r.start_time = time
    r.time = time
    r.location = cart.last_known_location
    r.payload = cart.payload
    r.working_time = 0
    r.quantity_unloaded = 0

    return r


class Logger:
    def __call__(self, msg):
        print(msg)


class RoutePlanner:
    def __init__(
        self,
        max_jobs: int,
        load_time_estimator: load_time_estimator,
        unload_time_estimator: unload_time_estimator,
        transit_time_estimator: transit_time_estimator,
        logger: Logger,
    ):
        self._max_jobs = max_jobs
        self._load_time_estimator = load_time_estimator
        self._unload_time_estimator = unload_time_estimator
        self._transit_time_estimator = transit_time_estimator
        self._logger = logger
        self._permutations = build_trie([], list(range(self._max_jobs * 2)))
        self._failed_route_count = 0

    def get_best_route(self, cart: Cart, jobs: List, time: SimTime) -> Route:
        working_time = float("inf")
        best_route = None  # type: Route
        successful_route_count = 0
        self._failed_route_count = 0

        for route in self._valid_routes_from_jobs(cart, jobs, time):  # type: Route
            if self._logger:
                self._logger("=================")
                self._logger("Succeeded:")
                self._logger("")
                self.explain_route(route, time, self._logger)
                self._logger("")

            if len(route.actions) == 0:
                print("zero-length route")
                for route in self._valid_routes_from_jobs(cart, jobs, time):
                    print("   Route")

            if route.working_time < working_time:
                successful_route_count += 1
                working_time = route.working_time
                best_route = route

        if self._logger:
            self._logger("")
            self._logger(
                "Considered {} failed routes.".format(self._failed_route_count)
            )
            self._logger(
                "Considered {} successful routes.".format(successful_route_count)
            )

        return best_route

    def _valid_routes_from_jobs(
        self, cart: Cart, jobs: List, time: SimTime
    ) -> Generator[Route, None, None]:
        if len(jobs) > self._max_jobs:
            msg = "Too many jobs for cart {}".format(cart.id)
            raise ValueError(msg)

        actions = self._actions_from_jobs(jobs)
        state = state_from_cart(cart, time)
        yield from self._valid_routes_from_actions(
            self._permutations, cart, state, actions, []
        )

    def _valid_routes_from_actions(
        self,
        trie: Dict,
        cart: Cart,
        previous_state: RouteState,
        actions: List,
        head: List,
    ) -> Generator[Route, None, None]:
        leaf_node = True

        for node in trie:
            if node.key < len(actions):
                action = actions[node.key]
                leaf_node = False
                new_head = head.copy()
                new_head.append(action)
                state = previous_state

                if not self._apply_action(cart.capacity, state, action, self._logger):
                    self._failed_route_count += 1
                    if self._logger:
                        self._logger("================")
                        self._logger("Failed:")
                        self._logger("")
                        route = Route()
                        route.cart = cart
                        route.actions = new_head
                        route.working_time = state.working_time
                        route.score = 0
                        self.explain_route(route, state.start_time, self._logger)
                        self._logger("")

                    return

                yield from self._valid_routes_from_actions(
                    node.children, cart, state, actions, new_head
                )

        if leaf_node:
            score = 0
            if previous_state.working_time != 0:
                score = previous_state.quantity_unloaded / previous_state.working_time

            route = Route()
            route.cart = cart
            route.actions = head
            route.working_time = previous_state.working_time
            route.score = score

            yield route

    def _apply_action(
        self, capacity: int, state: RouteState, action: ActionBase, logger: Logger,
    ) -> bool:
        value = True

        def case_drop_off(
            self,
            capacity: int,
            state: RouteState,
            action: DropoffAction,
            logger: Logger,
        ):
            if logger:
                msg = "DROPOFF {} items at location {} before {} (job {})".format()
            start_time = state.time

            if action.location != state.location:
                transit_time = self._transit_time_estimator(
                    state.location, action.location, state.time
                )
                if logger:
                    msg = "    {}: drive for {}s to location {}".format(
                        state.time, transit_time, action.location
                    )
                    logger(msg)
                state.time += transit_time
                state.location = action.location

            unload_time = self._unload_time_estimator(
                action.location, action.quantity, state.time
            )
            if logger:
                msg = "    {}: unload {} tiems in {}s.".format(
                    state.time, action.quantity, unload_time
                )
                logger(msg)
            state.time += unload_time
            state.payload -= action.quantity
            state.quantity_unloaded += action.quantity

            if state.time > action.time:
                if logger:
                    msg = (
                        "    {}: CONSTRAINT VIOLATED - dropoff after"
                        " deadline {}".format(state.time, action.time)
                    )
                    logger(msg)

                return False

            if state.payload < 0:
                if logger:
                    msg = "    {}: CONSTRAINT VIOLATED - negative payload {}".format(
                        state.time, action.time
                    )

                return False

            state.working_time += state.time - start_time
            return True

        def case_pickup(
            self,
            capacity: int,
            state: RouteState,
            action: PickupAction,
            logger: Logger,
        ):
            if logger:
                msg = "PICKUP {} items at location {} after {} (job {})".format(
                    action.quantity, action.location, action.time, action.job.id,
                )
                logger(msg)
            start_time = state.time

            if action.location != state.location:
                transit_time = self._transit_time_estimator(
                    state.location, action.location, state.time
                )
                if logger:
                    msg = "    {}: drive for {}s to location {}".format(
                        state.time, transit_time, action.location
                    )
                    logger(msg)
                state.time += transit_time
                state.location = action.location

            if action.time > state.time:
                wait_time = action.time - state.time
                if logger:
                    msg = "    {}: wait {}s until {}".format(
                        state.time, wait_time, action.time
                    )
                    logger(msg)
                state.time = action.time

            load_time = self._load_time_estimator(
                action.location, action.quantity, state.time
            )
            if logger:
                msg = "    {}: load {} items in {}s.".format(
                    state.time, action.quantity, load_time
                )
                logger(msg)
            state.time += load_time
            state.payload += action.quantity

            if state.payload > capacity:
                if logger:
                    msg = (
                        "    {}: CONSTRANT VIOLATED - payload of {}"
                        "exceeds capacity of {}".format(
                            state.time, state.payload, capacity
                        )
                    )
                return False

            state.working_time += state.time - start_time
            return True

        def case_suspend(
            self,
            capacity: int,
            state: RouteState,
            action: SuspendAction,
            logger: Logger,
        ):
            if logger:
                msg = "SUSPEND at location {} before {} until {} (job {})".format(
                    action.location,
                    action.suspend_time,
                    action.resume_time,
                    action.job.id,
                )
                logger(msg)

            if action.location != state.location:
                transit_time = self._transit_time_estimator(
                    state.location, action.location, state.time
                )
                if logger:
                    msg = "    {}: dirve for {}s to location {}".format(
                        state.time, transit_time, action.location
                    )
                    logger(msg)
                state.time += transit_time
                state.working_time += transit_time
                state.location = action.location

            if state.time > action.suspend_time:
                if logger:
                    msg = (
                        "    {}: CONSTRAINT VIOLATED - suspends after"
                        " deadline {}".format(state.time, action.suspend_time)
                    )
                    logger(msg)
                return False

            if logger:
                msg = "    {}: suspend operations".format(state.time)
                logger(msg)

            if state.time < action.resume_time:
                wait_time = action.resume_time - state.time
                if logger:
                    msg = "    {}: wait {}s until {}".format(
                        state.time, wait_time, action.resume_time
                    )
                    logger(msg)
                state.time = action.resume_time

            if logger:
                logger("    {}: reusme operations".format(state.time))
            return True

        action_cases = {
            ActionType.DROPOFF: case_drop_off,
            ActionType.PICKUP: case_pickup,
            ActionType.SUSPEND: case_suspend,
        }

        try:
            value = action_cases[action.type](self, capacity, state, action, logger)
        except KeyError:
            pass  # shouldnt be reachable, still should log raise error
        except AttributeError:
            pass

        if logger:
            logger("    {}: completed".format(state.time))

        return value

    def _actions_from_jobs(self, jobs: List) -> List:
        actions = []

        def case_out_of_service(self, job: TransferJob):
            if job.state == OutOfServiceJobState.BEFORE_BREAK:
                sa = SuspendAction()
                sa.job = job
                sa.type = ActionType.SUSPEND
                sa.location = job.suspend_location
                sa.suspend_time = job.suspend_time
                sa.resume_time = job.resume_time
                actions.append(sa)

                actions.append(None)

        def case_transfer(self, jobs: TransferJob):
            if job.state == TransferJobState.BEFORE_PICKUP:
                pa = PickupAction()
                pa.job = job
                pa.type = ActionType.PICKUP
                pa.location = job.pickup_location
                pa.time = job.pickup_after
                pa.quantity = job.quantity

                actions.append(pa)

            da = DropoffAction()
            da.job = job
            da.type = ActionType.DROPOFF
            da.location = job.dropoff_location
            da.time = job.dropoff_before
            da.quantity = job.quantity

            actions.append(da)

            if job.state != TransferJobState.BEFORE_PICKUP:
                actions.append(None)

        job_cases = {
            JobType.OUT_OF_SERVICE: case_out_of_service,
            JobType.TRANSFER: case_transfer,
        }

        for job in jobs:
            try:
                job_cases[job.job_type](self, job)
            except KeyError:
                pass

        return actions

    def explain_route(self, route: Route, time: SimTime, logger: Logger):
        msg = "Route for cart {} (working time = {}, score = {:.3f}:".format(
            route.cart.id, route.working_time, route.score
        )
        logger(msg)

        cart = route.cart
        state = state_from_cart(cart, time)

        for action in route.actions:
            if not self._apply_action(cart.capacity, state, action, logger):
                break


def format_action(action: ActionBase) -> str:
    s = "Unknown action"

    def case_drop_off(action: ActionBase):
        s = "dropoff {} items at location {} before {}".format(
            action.quantity, action.location, action.time
        )

    def case_pickup(action: ActionBase):
        s = "pickup {} items at location {} after {}".format(
            action.quantity, action.suspendTime, action.resume_time
        )

    def case_suspend(action: ActionBase):
        s = "suspend at location {} before {} until {}".format(
            action.location, action.suspendTime, action.resumeTime
        )

    action_cases = {
        ActionType.DROPOFF: case_drop_off,
        ActionType.PICKUP: case_pickup,
        ActionType.SUSPEND: case_suspend,
    }

    try:
        action_cases[action.type](action)
    except KeyError:
        pass  # shouldnt be reachable, still should log raise error

    return "{} (job {})".format(s, action.job.id)


def print_route(route: Route):
    msg = "Route for cart {} (working time = {}):".format(
        route.cart.id, route.working_time
    )
    print(msg)

    for action in route.actions:
        print("    {}".format(format_action(action)))
