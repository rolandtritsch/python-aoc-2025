---
name: closest-pairs-circuit-cross-check
description: Independently verify an AoC "connect the closest pairs" circuit solution (Day08 Playground parts 1 and 2) against a sorted-pair reference that tracks circuits as merged sets, covering the official sample, the real input, the skip-consumes-a-slot rule, cutoff ties, the final-connection X product, and circuit boundary banks.
---

# Closest-pairs circuit cross-check

Use when a puzzle connects pairs of points in increasing straight-line distance,
skipping pairs whose endpoints are already in the same circuit, and then asks for
a product of the three largest circuit sizes (Day08 part 1: connect the 1000
closest junction-box pairs, multiply the three largest circuits) or the product
of the X coordinates of the pair that first joins every point into one circuit
(Day08 part 2: keep connecting until one large circuit). The implementation under
review materializes all pairs into a min-heap and uses a path-halving
disjoint-set forest.

## Trigger

- Part 1: the answer is a product of the largest connected-component sizes after
  a fixed number of closest pairs are examined.
- Part 2: the answer is the product of the X coordinates of the pair whose
  connection first joins every point into a single connected component.
- The implementation uses a heap keyed by squared distance plus a union-find
  parent array, so the reviewer needs an oracle that shares neither structure.
- The exact reading of the connection budget matters: do skipped (already
  in-circuit) pairs consume one of the examined pairs or not?
- The reviewer must independently confirm the real-input total and whether the
  cutoff distance (part 1) or the final-merge distance (part 2) has ties that
  would make the answer order-dependent.

## Inputs

- The puzzle statement and the exact rule (closest pairs by squared distance,
  skip already-connected pairs, product of three largest circuits / product of
  the X coordinates of the final pair).
- The implementation under review (`src/aoc2025/day08.py`).
- The official sample in `inputs/Day08Test.txt` (20 boxes) with its stated
  part 1 answer 40 after 10 closest pairs and part 2 answer 25272 = 216 * 117
  from the final pair (216,146,977) and (117,168,530), and the real input
  `inputs/Day08.txt` (1000 boxes, 499500 pairs).
- The boundary banks from `tests/test_day08.py`.

## Procedure

### Part 1 (fixed K closest pairs, product of three largest circuits)

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

### Part 2 (keep connecting, product of X of the final pair)

1. Write an independent reference that tracks circuits the same way (sorted pair
   list, `representative -> set(members)` merges) but iterates every pair until a
   single circuit remains and returns the pair that completed the merge; the
   answer is the product of the two boxes' X coordinates. For Day08 this is
   `part2`/`final_pair` in `reference/day08_final_connection.py`.
2. Confirm the final-connection reading on the sample. The sample's final pair is
   (216,146,977) and (117,168,530) (sample answer 25272 = 216 * 117), not the
   product of the two highest X coordinates and not the farthest pair overall.
   The real input's final pair is boxes 661 (80198,9816,87378) and 937
   (75856,51,95679), giving 80198 * 75856 = 6083499488.
3. Run the reference and the implementation on the official sample (both 25272)
   and the real input (both 6083499488). Exact agreement on the real total is
   acceptance-adjacent evidence, not a transcription, because the two use
   different data structures.
4. Check final-merge tie-robustness. Require the final pair's distance to be
   unique (`final_merge_is_tie_free`). For the real input the final-merge
   distance is unique, so 6083499488 does not depend on tie-breaking order. Both
   structures use the same `(distance, i, j)` ordering, so they still agree on a
   tied bank (`ties-at-final-merge` gives 6), but that agreement is
   order-dependent: a tie at the final-merge distance makes the pair ambiguous
   and must be reported as such.
5. Exercise boundary banks where part 2 semantics are easy to get wrong: fewer
   than two boxes raises `ValueError`; two boxes form a single pair (product of
   that pair); a 3-box line where the final pair is the outer pair; two close
   clusters where the final connection is the closest cross-cluster pair, not
   the farthest pair overall; a bank pinning that the answer is the X product of
   the pair that completed the merge, not the max-X product; and a tie at the
   final-merge distance.
6. Record the agreement evidence on the review issue: sample total, real-input
   total, final-merge tie-free result, and the boundary banks exercised, each
   with reference vs implementation value. Label the reference "sorted-pair
   merged-set" so a future reviewer can tell it apart from the heap/union-find
   implementation.

## Evidence and validation

- `reference/day08_closest_pairs.py` is a runnable, self-checking demonstration
  of part 1: `uv run python3 skills/closest-pairs-circuit-cross-check/reference/day08_closest_pairs.py`
  prints the sample total (40), the real-input total (90036), the cutoff
  tie-free result, and each boundary bank, asserting sorted-set == implementation
  throughout.
- `reference/day08_final_connection.py` is a runnable, self-checking
  demonstration of part 2:
  `uv run python3 skills/closest-pairs-circuit-cross-check/reference/day08_final_connection.py`
  prints the sample total (25272), the real-input total (6083499488), the
  final-merge tie-free result, and each boundary bank, asserting merged-set ==
  implementation throughout. It is read-only against the repository and needs no
  third-party packages.
- The references are deliberately independent: they never import `day08`'s
  private `_circuit_sizes`/`_squared_distance`/`_final_connection`, never build a
  heap, and never use a parent array or path compression.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the references are additional oracles, not a replacement for
  `tests/test_day08.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and the implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.
