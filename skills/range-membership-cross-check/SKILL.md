---
name: range-membership-cross-check
description: Independently verify an AoC interval-membership or interval-union solution against a naive reference that scans every range for each queried value, covering the official sample, the real input, and inclusive-range boundary banks.
---

# Range membership cross-check

Use when a puzzle counts or tests items against inclusive numeric ranges that may
overlap (fresh ingredient IDs in Day05, or any "falls into at least one range"
rule) and the implementation optimizes the membership test — for example by
merging overlapping/adjacent ranges and then binary-searching each query, or by
merging and summing interval lengths. You need to confirm the optimized code's
count on the official sample and the real input without trusting the merge logic
or the binary-search indexing.

## Trigger

- A solution answers "how many queried values fall into at least one inclusive
  range" (Day05 part1) or "how many values are covered by the union of ranges"
  (a part2-style interval-union count).
- The reviewer must independently confirm the real-input total (not just the
  official sample).
- Boundary behavior — inclusive endpoints, overlap deduplication, adjacency of
  touching ranges — is easy to get wrong and needs an independent oracle.

## Inputs

- The puzzle statement and the exact interval rule (inclusive endpoints, at
  least one range).
- The implementation under review (`src/aoc2025/dayNN.py`).
- The official sample in `inputs/DayNNTest.txt` and its stated answer.
- The real input `inputs/DayNN.txt`.

## Procedure

1. Write a naive reference that scans every raw range for each queried value:
   an ID is fresh when `any(first <= id <= last)` over the unmerged ranges.
   It must share no structural shortcut with the implementation — no range
   merging, no binary search, no shared helper. For Day05 part1 this is
   `naive_fresh_count` in `reference/day05_naive_membership.py`.
2. Run the reference and the implementation on the official sample. They must
   agree with each other and with the statement's stated sample answer (Day05
   part1: 3). Disagreement means one of them misreads the rule.
3. Run both on the real input and require exact agreement on the total (Day05
   part1: 848). The real input is only 182 ranges and 1000 IDs, so the O(n*m)
   reference is trivially tractable and verifies the total independently.
4. Check boundary banks where the rule is easy to get wrong: empty ranges and
   empty queries (0), inclusive bounds (each of 3, 4, 5 fresh in 3-5), just
   outside (2, 6 spoiled), below/above/in-gap of disjoint ranges, overlapping
   ranges counting a duplicated query value once, touching/adjacent ranges
   (3 and 4 both fresh in 1-3, 4-6), a contained range, a single-point range,
   and duplicate query values each counted.
5. For an interval-union part (Day05 part2), use a structurally different
   sweep-line reference instead: a +1 event at each `first`, a -1 event at
   each `last + 1`, then a walk over sorted coordinates summing any span where
   the active count is positive (`union_length_sweep` in
   `reference/day05_union_sweep.py`). It never merges ranges and never sums
   merged lengths, so agreement on the real input is independent evidence for
   the part2 total (sample 14, real 334714395325710). Sweep the same boundary
   banks: no ranges (0), single point (1), inclusive endpoints, disjoint
   lengths, overlap-once, adjacent-touching, contained, contained-touching at
   an endpoint, many single points, and unsorted input.
6. Record the agreement evidence on the review issue: sample total, real-input
   total, and the boundary banks exercised, each with reference vs
   implementation value. Label the reference "independent naive range scan"
   (part1) or "independent endpoint sweep" (part2) so a future reviewer can
   tell it apart from the optimized implementation.

## Evidence and validation

- `reference/day05_naive_membership.py` is a runnable, self-checking
  demonstration for part1: `uv run python3 skills/range-membership-cross-check/reference/day05_naive_membership.py`
  prints the sample total (3), the real-input total (848), and the boundary
  banks, asserting naive == implementation throughout. It is read-only against
  the repository and needs no third-party packages.
- `reference/day05_union_sweep.py` is the part2 counterpart, a self-checking
  endpoint-sweep reference: `uv run python3 skills/range-membership-cross-check/reference/day05_union_sweep.py`
  prints the sample total (14), the real-input total (334714395325710), and the
  interval-union boundary banks, asserting sweep == implementation throughout.
- The references are deliberately independent: they reuse only the parser
  (`day05.read_database`) for input, never the merge, binary-search, or
  sum-merged-lengths logic, so agreement on the real input is independent
  acceptance-adjacent evidence, not a tautology.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the references are additional oracles, not a replacement for
  `tests/test_dayNN.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.
