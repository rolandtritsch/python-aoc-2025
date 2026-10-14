---
name: closest-pairs-circuit-cross-check
description: Independently verify an AoC "connect the closest pairs" circuit solution (Day08 Playground part 1) against a sorted-pair reference that tracks circuits as merged sets, covering the official sample, the real input, the skip-consumes-a-slot rule, cutoff ties, and circuit boundary banks.
---

# Closest-pairs circuit cross-check

Use when a puzzle connects pairs of points in increasing straight-line distance,
skipping pairs whose endpoints are already in the same circuit, and then asks for
a product of the three largest circuit sizes (Day08 part 1: connect the 1000
closest junction-box pairs, multiply the three largest circuits). The
implementation under review materializes all pairs into a min-heap and uses a
path-halving disjoint-set forest.

## Trigger

- The answer is a product of the largest connected-component sizes after a fixed
  number of closest pairs are examined.
- The implementation uses a heap keyed by squared distance plus a union-find
  parent array, so the reviewer needs an oracle that shares neither structure.
- The exact reading of the connection budget matters: do skipped (already
  in-circuit) pairs consume one of the examined pairs or not?
- The reviewer must independently confirm the real-input total and whether the
  cutoff distance has ties that would make the answer order-dependent.

## Inputs

- The puzzle statement and the exact rule (closest pairs by squared distance,
  skip already-connected pairs, product of three largest circuits).
- The implementation under review (`src/aoc2025/day08.py`).
- The official sample in `inputs/Day08Test.txt` (20 boxes) with its stated
  answer 40 after 10 closest pairs, and the real input `inputs/Day08.txt`
  (1000 boxes, 499500 pairs).
- The boundary banks from `tests/test_day08.py`.

## Procedure

1. Write an independent reference that sorts a plain list of
   `(squared_distance, i, j)` tuples and tracks circuits as a
   `representative -> set(members)` mapping, merging the smaller set into the
   larger. This shares no heap and no parent array with the implementation. For
   Day08 this is `part1`/`circuit_sizes` in
   `reference/day08_closest_pairs.py`.
2. Confirm the connection-budget reading on the sample. The statement's sample
   examines 10 closest pairs, one of which is already in-circuit, and gives 40.
   A reading where skips do not consume a slot gives 50 on the same sample, so
   the reference must treat every examined pair (skip included) as consuming the
   budget. The `skip-consumes-slot` boundary bank pins this: boxes at
   `x = 0, 1, 2, 4` with 3 connections connect `{0,1,2}` and leave `{4}` alone
   (product 3), because the third-closest pair `(0,2)` is skipped but still
   counts.
3. Run the reference and the implementation on the official sample (both 40) and
   the real input (both 90036). Exact agreement on the real total is
   acceptance-adjacent evidence, not a transcription, because the two use
   different data structures.
4. Check cutoff tie-robustness. Sort every pair distance and require the K-th
   closest distance to be unique (`cutoff_is_tie_free`). For the real input the
   1000th distance (63950729) is unique and no two of the first 1000 pair
   distances tie, so 90036 does not depend on tie-breaking order. If a future
   input has a tie across the cutoff, the answer is ambiguous and must be
   reported as such rather than silently accepted.
5. Exercise boundary banks where the semantics are easy to get wrong: fewer than
   three boxes raises `ValueError`; a 3-box line with 2 connections forms one
   circuit; two far-apart pairs plus a singleton; `ties-at-cutoff`; a connection
   budget larger than the pair count (everything merges); two disconnected
   clusters; and a pair examined after its boxes are already connected.
6. Record the agreement evidence on the review issue: sample total, real-input
   total, cutoff tie-free result, and the boundary banks exercised, each with
   reference vs implementation value. Label the reference "sorted-pair merged-set"
   so a future reviewer can tell it apart from the heap/union-find implementation.

## Evidence and validation

- `reference/day08_closest_pairs.py` is a runnable, self-checking demonstration:
  `uv run python3 skills/closest-pairs-circuit-cross-check/reference/day08_closest_pairs.py`
  prints the sample total (40), the real-input total (90036), the cutoff
  tie-free result, and each boundary bank, asserting sorted-set ==
  implementation throughout. It is read-only against the repository and needs no
  third-party packages.
- The reference is deliberately independent: it never imports `day08`'s private
  `_circuit_sizes`/`_squared_distance`, never builds a heap, and never uses a
  parent array or path compression.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_day08.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and the implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.
