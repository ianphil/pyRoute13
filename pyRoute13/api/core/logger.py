#!/usr/bin/env python

from api.planner.route import Route, ActionType, ActionBase


class Logger:
    def __call__(self, msg):
        print(msg)

    @staticmethod
    def format_action(action: ActionBase) -> str:
        s = "Unknown action"

        def case_drop_off(action: ActionBase):
            return "dropoff {} items at location {} before {}".format(
                action.quantity, action.location, action.time
            )

        def case_pickup(action: ActionBase):
            return "pickup {} items at location {} after {}".format(
                action.quantity, action.suspendTime, action.resume_time
            )

        def case_suspend(action: ActionBase):
            return "suspend at location {} before {} until {}".format(
                action.location, action.suspendTime, action.resumeTime
            )

        action_cases = {
            ActionType.DROPOFF: case_drop_off,
            ActionType.PICKUP: case_pickup,
            ActionType.SUSPEND: case_suspend,
        }

        try:
            s = action_cases[action.type](action)
        except KeyError:
            pass  # shouldnt be reachable, still should log raise error

        return "{} (job {})".format(s, action.job.id)

    @staticmethod
    def print_route(route: Route):
        msg = "Route for cart {} (working time = {}):".format(
            route.cart.id, route.working_time
        )
        print(msg)

        for action in route.actions:
            print("    {}".format(Logger.format_action(action)))
