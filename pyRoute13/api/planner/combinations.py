from typing import List


def combinations(select: int, from_set: int):
    if select != 0:
        yield from _generate_combinations(select, 0, from_set, [])


def _generate_combinations(select: int, start: int, end: int, selection: List):
    if select == 0:
        yield selection
    else:
        remaining = select - 1
        count = start
        while count < end - remaining:
            selection.append(count)
            count += 1
            yield from _generate_combinations(remaining, count, end, selection)
            selection.pop()
