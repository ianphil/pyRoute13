from api.environment.cart import Cart
from api.environment.job import JobBase
from api.planner.planner import Assignment


def merge(carts, jobs, plan):
    """ Produces a new job assignment that is the merge of existing assignment
    and a new assignment.

    Arguments:
    carts -- list[tuple(cart_id, cart)]
    jobs  -- list[tuple(job_id, job)]
    plan  -- list[tuple(cart, assignment)]

    Returns: list[tuple(cart, list[job])]
    """
    merged = []

    [merged.append((cart, [])) for _, cart in carts.items()]

    for job_id, job in jobs.items():  # type: int, JobBase
        if job.assigned_to:
            [
                job_list.append(job)
                for cart, job_list in merged
                if cart.id == job.assigned_to.id
            ]

    for _, assignment in plan:  # type: Cart, Assignment
        cart = next(
            (cart for _, cart in carts.items() if cart.id == assignment.cart.id), None,
        )
        if not cart:
            msg = "Unknown cart_id".format(assignment.cart.id)
            raise TypeError(msg)
        else:
            for j in assignment.jobs:  # type: JobBase
                job = next(
                    (_job for _, _job in jobs.items() if j.id == _job.id), None
                )  # type: JobBase
                if job is None:
                    pass  # just discard it
                else:
                    if job.assigned_to is None:
                        [
                            job_list.append(job)
                            for _cart, job_list in merged
                            if cart.id == _cart.id
                        ]

    return merged
