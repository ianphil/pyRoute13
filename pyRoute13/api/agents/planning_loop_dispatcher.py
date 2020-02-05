from api.agents.dispatcher import Dispatcher
from api.core.timeline import Timeline, SimTime
from api.environment.environment import Environment
from api.environment.trace import Trace
from api.planner.planner import Planner
from api.environment.job import JobBase
from api.environment.cart import Cart
from api.core.condition import Condition
from api.planner.job_merger import merge


class PlanningLoopDispatcher(Dispatcher):
    def __init__(
        self,
        timeline: Timeline,
        env: Environment,
        trace: Trace,
        planning_start_time: SimTime,
        planning_interval: SimTime,
        planner: Planner,
    ):
        self.timeline = timeline
        self.env = env
        self.trace = trace
        self.planning_start_time = planning_start_time
        self.planning_interval = planning_interval
        self.planner = planner
        self.shutting_down = False
        self.job_available_condition = Condition()
        self.current_plan = []  # List[Tuple(Cart, List[JobBase])]
        self.current_plan_time = float("-inf")
        self.new_plan_available = Condition()

    def wait_for_job(self):
        def f(agent):
            self._job_available_condition.sleep(agent)

        return f

    def wait_for_next_plan(self, plan_time: SimTime):
        if plan_time >= self.current_plan_time and not self.shutting_down:

            def f(agent):
                self.new_plan_available.sleep(agent)

            yield f

    def get_plan(self, cart: Cart, jobs):
        try:
            unfiltered = next(
                (job_list for c, job_list in self.current_plan if cart.id == c.id), [],
            )
        except TypeError:
            raise TypeError("Unknown cart".format(cart.id))

        filtered = []
        for job in unfiltered:  # type: JobBase
            job_active = next(
                (_job for i, _job in jobs.items() if job.id == _job.id), None
            )
            if job_active:
                if job.assigned_to is None or job.assigned_to.id == cart.id:
                    filtered.append(job)

        if self.trace:
            self.trace.cart_plan_is(cart, unfiltered, filtered)

        return filtered

    def get_current_plan_time(self):
        return self.current_plan_time

    def newer_plan_available(self, plan_time: SimTime):
        return plan_time < self.current_plan_time

    def is_shutting_down(self):
        return self.shutting_down

    def introduce_job(self, job: JobBase, time: SimTime):
        yield self.timeline.until(time)
        self.env.add_job(job)
        self.job_available_condition.wake_one()

    def planning_loop(self):
        if self.planner:
            while not self.shutting_down:
                yield from self._update_job_assignments()

    def _update_job_assignments(self):
        if not self.shutting_down:
            self.trace.planner_started()
            carts = self.env.cart_snapshot()
            jobs = self.env.job_snapshot()

            plan_ready_time = max(
                [
                    self.planning_start_time,
                    (self.timeline.time + self.planning_interval),
                ]
            )
            yield self.timeline.until(plan_ready_time)

        plan = self.planner.create_assignment(jobs, carts, plan_ready_time, None)

        self.current_plan = merge(self.env.fleet, self.env.jobs, plan)
        self.current_plan_time = self.timeline.time

        self.trace.planner_finished()
        self.new_plan_available.wake_all()

    def shutdown_at(self, time: SimTime):
        yield self.timeline.until(time)
        self.shutting_down = True
