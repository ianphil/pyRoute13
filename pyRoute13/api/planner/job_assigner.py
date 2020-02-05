from typing import List
from copy import deepcopy
from route13.core.timeline import SimTime
from route13.environment.cart import Cart
from route13.environment.job import JobBase
from route13.planner.combinations import combinations
from route13.planner.planner import Assignment, Planner
from route13.planner.route_planner import RoutePlanner


class JobAssigner(Planner):
    def __init__(
        self,
        max_job_count: int,
        load_time_estimator,
        unload_time_estimator,
        transit_time_estimator,
    ):
        self.max_job_count = max_job_count
        self.route_planner = RoutePlanner(
            max_job_count,
            load_time_estimator,
            unload_time_estimator,
            transit_time_estimator,
            None,
        )
        self.assigned_jobs = set()

    # returns list containing tuple of cart, assignment
    def create_assignment(self, jobs, carts, time: SimTime, logger):
        existing_assignments = []
        unassigned = []

        for i, cart in carts.items():  # type: Cart
            existing_assignments.append((cart, []))

        for i, job in jobs.items():  # type: JobBase
            cart = job[0].assigned_to
            if cart:
                cart_jobs = next(
                    (
                        job_list
                        for c, job_list in existing_assignments
                        if c.id == cart.id
                    ),
                    None,
                )
                if cart_jobs:
                    cart_jobs.append(job[0])
            else:
                unassigned.append(job[0])

        alternatives = []
        for cart, assigned in existing_assignments:
            if len(assigned) >= self.max_job_count:
                a = Assignment()
                a.cart = cart
                a.jobs = assigned
                a.score = float("inf")
            else:
                max_new_jobs = self.max_job_count - len(assigned)
                for job_count in range(1, max_new_jobs):
                    for combination in combinations(
                        job_count, len(unassigned)
                    ):  # type: List
                        slate = deepcopy(assigned)
                        [slate.append(unassigned[x]) for x in combination]
                        try:
                            plan = self.route_planner.get_best_route(cart, slate, time)
                            if plan:
                                a = Assignment()
                                a.cart = cart
                                a.jobs = slate
                                a.score = plan.working_time
                                alternatives.append(a)
                        except ValueError:
                            pass

        alternatives = sorted(alternatives, key=lambda x: x.score, reverse=True)

        assignments = []
        # assigned_jobs = set()
        assigned_carts = set()
        for alternative in alternatives:
            conflicting = alternative.cart in assigned_carts
            if not conflicting:
                for job in alternative.jobs:
                    if job in self.assigned_jobs:
                        conflicting = True
                        break
            if not conflicting:
                assigned_carts.add(alternative.cart)
                [self.assigned_jobs.add(job) for job in alternative.jobs]
                assignments.append((alternative.cart, alternative))

        if logger:
            logger("")
            logger("Searched {} assignements".format(len(alternatives)))
            logger("")

        return assignments
