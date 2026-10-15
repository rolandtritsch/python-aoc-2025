---
name: joltage-presses-cross-check
description: Independently verify an AoC "button schematics set joltage counters, fewest presses" solution (Day10 Factory part 2) against an exact-Dijkstra reference over counter-count states sharing none of the LP relaxation, exact simplex / shadow-price / fractional-branch / branch-and-bound machinery under review, covering the official sample (total 33), the completed subset of the 163-machine real input within a node budget, and joltage-press boundary banks.
---

# Joltage-presses cross-check

Use when a puzzle gives one factory machine per line with an indicator-light
diagram in `[..]`, button wiring schematics in `(...)`, and joltage tuples in
`{...}`, where flipping the lever switches the buttons into joltage mode: one
press increments each counter a button's wiring lists, every counter starts at
0, and the answer is the fewest total presses to make each machine's counters
land exactly on its required joltage tuple (Day10 Factory part 2). The
implementation under review finds each machine's minimum press count with an
exact LP relaxation of ``A x = joltages, x >= 0`` using a Fraction-valued
simplex tableau, reads fractional shadow prices, and branch-and-bounds a
fractional press to its floor or ceiling, re-relaxing after every fix until
all presses are integers.

## Trigger

- The answer is a minimum press count, one press increments each counter a
  button's wiring lists, counters start at 0command, and the machine must land
  exactly on its joltage tuple; each button may be pressed any non-negative
  integer number of times, so the fewest total presses is the minimum-weight
  integer solution of a non-negative linear system ``A x = joltages``.
- The implementation uses an exact (``Fraction``) LP relaxation + shadow prices
  + branch on fractional presses (simplex tableau, pivot, shadow price, floor /
  ceiling fix, branch-and-bound), so the reviewer needs an oracle sharing none
  of that machinery: no simplex, no ``Fraction``, no shadow prices, no branch
  on fractions, and no branch-and-bound.
- The reviewer must independently confirm the real-input total, because a wrong
  pivot, a wrong shadow price, or a missed branch can change the minimum press
  count even when each machine's wiring has been parsed correctly.

## Inputs

- The puzzle statement and the exact rule (one press increments each listed
  counter; fewest total presses landing exactly on every machine's joltage
  tuple; a machine that cannot be reached exactly is unconfigurable, raising
  ``ValueError``).
- The implementation under review (`src/aoc2025/day10.py`).
- The official sample `inputs/Day10Test.txt` with its stated part 2 total 33
  (10 + 12 + 11) and the real input `inputs/Day10.txt` (163 machines, answer
  16765).
- The boundary banks in `tests/test_day10.py` (single counter, shared counter
  splitting presses, single button incrementing all counters, the fractional
  relaxation that forces a branch, an unreachable / unconfigurable machine, and
  the empty machine list).

## Procedure

1. Write an independent reference sharing none of the LP/simplex/shadow-price /
   branch machinery. The recommended form runs Dijkstra over the natural
   counter-count states: a state is the tuple of current joltage counts (all
   counters start at 0; one press of a button increments each counter its wiring
   lists), and an edge pushes one button exactly once (unit cost). Any press
   that would push a counter past its joltage target is pruned, because it can
   never lead to an exact solution; the fewest presses is the cheapest integer
   number of presses landing exactly on the required joltage tuple. Targets
   that cannot be reached make the machine unconfigurable (raises
   ``ValueError``). It never builds a coefficient row, performs a pivot, reads a
   shadow price, fixes a fraction, an LP tableau, or ``Fraction`` arithmetic. A
   runnable Day10 part 2 reference is
   `skills/joltage-presses-cross-check/reference/day10_fewest_presses_dijkstra.py`
   (sample 33 = 10 + 12 + 11, real 16765 on performed machines, Dijkstra ==
   implementation throughout; the largest real machines have a huge product of
   target spaces and are not enumerated within the node budget, which the
   reference reports explicitly).

2. Confirm the sample reading: the official 3-machine sample totals 33 (10 + 12
   + 11) in part 2)Skip (part 1 sample totals 7). The reference must reproduce
   both on `Day10Test.txt`.

3. Run the reference on the official sample (must reproduce the stated total 33)
   and on the real input with a per-machine node budget; only machines whose
   counter state space fits in the budget are enumerated. Report which machines
   were completed and which were not (over budget), plus the partial total.
   Agreement on the complete sample and on the completed real machines is
   independent acceptance-adjacent evidence; the unverified remainder relies on
   the authoritative puzzle-page acceptance.

4. Exercise boundary banks where the rule is easy to get wrong: a single
   counter reachable by exactly one button (`(#, (0,), (5,)) -> 5`), a shared
   counter that must split presses across multiple buttons (`(##, ((0,),
   (1,)), (7,)) -> 7`), a single button wiring every counter, a machine with an
   unreachable counter (a counter with no button wiring, raising
   ``ValueError``), and an empty machine list contributing 0.

## Evidence

- The official sample reproduces total 33 exactly (one Dijkstra per edge = one
  press), plus 7 for part 1.
- The real input is verified on every machine whose counter state space stays
  within the node budget, and the skill reports unfinished machines
  explicitly. Completed-machine agreement on a Dijkstra reference sharing no LP
  machinery is independent acceptance-adjacent evidence; the puzzle-page
  acceptance remains the authoritative verdict for the total 16765.
- Boundary banks (single counter, shared-counter split, all-counters button,
  unconfigurable machine, empty list) reproduce the implementation's behavior
  including the ``ValueError`` for unconfigurable machines.
