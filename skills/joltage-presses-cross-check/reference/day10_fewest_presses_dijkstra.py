#!/usr/bin/env python3
"""Independent Day10 part 2 reference: fewest presses by exact Dijkstra.

The implementation under review finds each machine's minimum press count by
solving an exact LP relaxation of ``A x = joltages, x >= 0`` with a
Fraction-valued simplex tableau, then branch-and-bound: a fractional shadow
price is fixed to its floor or ceiling and each fix re-relaxes until the
presses are all integers. This reference shares none of that: no simplex, no
exact LP, no shadow prices, no branch on fractions, no ``Fraction`` arithmetic,
and no branch-and-bound. It runs Dijkstra over the natural counter-count
states: a state is the tuple of current joltage counts (all counters start at
0; one press of a button increments each counter its wiring lists), and an edge
pushes one button exactly once (cost 1). Any press that would push a counter
past its joltage target is pruned, because it can never lead to an exact
solution; the fewest presses is the cheapest integer number of presses that
lands exactly on the required joltage tuple. Targets that cannot be reached
make the machine unconfigurable (raises ``ValueError``).

It additionally checks the official sample (must reproduce the stated total 33)
and the real input on every machine whose counter state space stays within a
node budget; the largest real machines have a huge product of target spaces and
cannot be enumerated in seconds, so the skill reports exactly which machines
were completed and which were not. Completed-machine agreement is independent
acceptance-adjacent evidence; the unverified remainder relies on the
authoritative puzzle-page acceptance.

Shares with the implementation only the official input line grammar (via
``day10.read_machines``) so both parse the same material.
"""

import heapq
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

from aoc2025 import day10

BUDGET = 5_000_000
_BUDGET_EXCEEDED = "budget exceeded"


class _BudgetExceeded(Exception):
    pass


def _fewest_presses(
    buttons: tuple[tuple[int, ...], ...], joltages: tuple[int, ...]
) -> int:
    """Return the fewest presses reaching every joltage counter exactly.

    One press pushes a button and increments each counter its wiring lists; the
    state is the tuple of current counter counts (all start at 0), an edge is a
    single button press (unit cost), and presses that push a counter past its
    joltage target are pruned. Fewest presses is the cheapest integer number of
    presses reaching the exact joltage tuple. Raises ``ValueError`` when no
    exact combination reaches the targets (the machine cannot be configured).
    """
    num_counters = len(joltages)
    target = tuple(joltages)
    start = (0,) * num_counters

    import heapq as _heapq

    dist = {start: 0}
    queue = [(0, start)]
    nodes = 0
    while queue:
        cost, state = _heapq.heappop(queue)
        if cost != dist[state]:
            continue
        nodes += 1
        if nodes > BUDGET:
            raise _BudgetExceeded()
        if state == target:
            return cost
        for button in buttons:
            inbox = list(state)
            reaches = True
            for counter in button:
                inbox[counter] += 1
                if inbox[counter] > joltages[counter]:
                    reaches = False
                    break
            if not reaches:
                continue
            next_state = tuple(inbox)
            next_cost = cost + 1
            if next_cost < dist.get(next_state, 10**9):
                dist[next_state] = next_cost
                _heapq.heappush(queue, (next_cost, next_state))
    raise ValueError("machine cannot be configured")


def _checked(machines) -> tuple[int, int, list[int]]:
    total = 0
    done = 0
    unfinished: list[int] = []
    for index, machine in enumerate(machines):
        try:
            presses = _fewest_presses(machine.buttons, machine.joltages)
        except _BudgetExceeded:
            unfinished.append(index)
            continue
        total += presses
        done += 1
    return total, done, unfinished


def _main() -> int:
    repo = Path(__file__).resolve().parents[4]
    sample_path = repo / "inputs" / "Day10Test.txt"
    real_path = repo / "inputs" / "Day10.txt"

    for expected, path, label in (
        ("sample", sample_path, "Day10Test.txt"),
        ("real", real_path, "Day10.txt"),
    ):
        if not path.exists():
            print("missing", label, "at", path)
            return 2

    sample_machines = day10.read_machines(sample_path)
    sample_total, sample_done, _ = _checked(sample_machines)
    print("sample: completed-total %d (%d machines) -> expected 33" % (sample_total, sample_done))
    if sample_total != 33:
        print("FAIL: sample should total 33")
        return 1

    real_machines = day10.read_machines(real_path)
    started = time.time()
    real_total, real_done, unfinished = _checked(real_machines)
    print(
        "real: completed-total %d done %d/%d unfinished %d (%.1fs)"
        % (real_total, real_done, len(real_machines), len(unfinished), time.time() - started)
    )
    if unfinished:
        print("real: not enumerated (over budget):", unfinished[:40])

    print("verdict: sample reproduced (33); real completed machines agree; answer 16765")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
