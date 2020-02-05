#!/usr/bin/env python

from api.environment import location


def transit_time_estimator(
    origin: location.LocationId, destination: location.LocationId, start_time: int,
) -> int:
    pass


def route_next_step(
    origin: location.LocationId, destination: location.LocationId, start_time: int,
) -> location.LocationId:
    pass


def load_time_estimator(
    location: location.LocationId, quantity: int, start_time: int
) -> int:
    pass


def unload_time_estimator(
    location: location.LocationId, quantity: int, start_time: int
) -> int:
    pass
