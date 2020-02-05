#!/usr/bin/env python


def start(agent) -> None:
    try:
        next_step = next(agent)
        try:
            next_step(agent)
        except TypeError:
            msg = "Returned generator not a function, did you use yield from?"
            raise TypeError(msg)
    except StopIteration:
        pass
