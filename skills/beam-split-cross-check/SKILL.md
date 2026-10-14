---
name: beam-split-cross-check
description: Independently verify an AoC beam-splitting or merge-propagation simulation against explicit per-cell references, covering splitter-hit totals (part 1) and distinct many-worlds timeline counts (part 2), on the official sample, the real input, and edge banks for merging, timeline distinctness, and boundary drops.
---

# Beam-split cross-check

Use when a puzzle simulates entities that propagate down a grid and merge when
they occupy the same position (Day07's tachyon manifold: a beam moves downward,
a `^` splitter stops it and emits two new beams from its immediate left and
right which then move downward, and beams in the same column merge into one).
Part 1 asks for a count of distinct splitter events; part 2 sends a single
quantum particle that takes *both* splitter branches, so time forks at each
splitter and the answer is the number of distinct timelines — which are distinct
even when they reach the same cell, because they arrived along different
histories.

## Trigger

- Part 1: a solution simulates downward propagation where two entities reaching
  the same cell/column merge, the answer counts discrete events (splits), and
  the implementation uses a per-row set (or other aggregate) that hides the
  merge semantics, so an independent per-cell reference is needed.
- Part 2: the same puzzle switches to the many-worlds reading where entities
  *never* merge — the answer counts distinct timelines, not distinct occupied
  columns — and the implementation tracks per-column counts. Verify that the
  counts really stay distinct (two timelines coinciding at a splitter fork into
  four, not two) and are not reusing part 1's set-merge semantics.
- The reviewer must independently confirm the real-input total (not just the
  official sample).
- Boundary handling is easy to get wrong: splits near the left/right grid edge
  that would spawn an out-of-range beam, splitters that a beam never reaches,
  and coinciding timelines.

## Inputs

- The puzzle statement and the exact propagation rule (downward movement,
  splitter spawns left/right, same-column merge for part 1, no-merge for part
  2, edge and bottom exit).
- The implementation under review (`src/aoc2025/day07.py`).
- The official sample in `inputs/Day07Test.txt` and its stated answers (21
  splits, 40 timelines).
- The real input `inputs/Day07.txt` (142 rows x 141 cols, one `S` at row 0
  col 70).
- The boundary banks from `tests/test_day07.py`.

## Procedure

1. For part 1, write an explicit per-cell reachability reference that shares no
   helper with the implementation: a stack of beam cells starting at the `S`
   cell; a visited-cell set so two beams arriving at the same cell merge into
   one; a splitter cell adds one to the count the first time it is reached and
   spawns the cells immediately left and right one row down; any other cell
   continues one row down; cells outside the grid are dropped. For Day07 this
   is `reachability_split_count` in
   `reference/day07_beam_reachability.py`.
2. For part 2, write two structurally independent references in
   `reference/day07_timeline_count.py`:
   - `enumerate_timeline_count` brute-force walks every distinct timeline as an
     explicit path of cells (forking at each splitter, counting once when the
     path leaves the grid) and never merges coinciding paths. This is the
     many-worlds definition directly and is tractable on the sample and banks,
     but not on the real input.
   - `memo_timeline_count` computes the same total with a bottom-up recursion
     over cells `count(row, col)` (an exited cell contributes 1, a splitter
     sums its two children, any other cell continues one row down), sharing no
     per-row dict or running accumulator with the implementation. This verifies
     the real input's large total.
3. Run the references and the implementation on the official sample. They must
   agree with each other and with the statement's stated answer (Day07: 21,
   part2: 40). Disagreement means one of them misreads the propagation, merge,
   or distinct-timeline rule.
4. Run both on the real input and require exact agreement on the total (Day07
   part1: 1605, part2: 29893386035180). The per-cell references are O(R*C) on
   the visited set or memo table, so they are trivially tractable on the
   142x141 real manifold.
5. Check edge banks where the semantics are easy to get wrong: empty grid,
   single cell `S`, straight-down with no splitter, a single splitter, a
   splitter off the beam's path (missed), two beams merging into one splitter
   (split once, not twice, for part 1), coinciding timelines that stay distinct
   (converging at an empty cell, and coinciding at a splitter where part 2
   forks each timeline so a count of two becomes four), a splitter at the left
   edge (the negative spawn is dropped), a splitter at the right edge (the
   out-of-range spawn is dropped), and a splitter on the last row whose
   children exit at the edge and the bottom.
6. Record the agreement evidence on the review issue: sample total, real-input
   total, and the boundary banks exercised, each with reference vs
   implementation value. Label the references "explicit per-cell reachability"
   (part 1), "explicit timeline enumeration", and "memoized cell recurrence"
   (part 2) so a future reviewer can tell them apart from the column-set and
   column-count implementations.

## Evidence and validation

- `reference/day07_beam_reachability.py` is a runnable, self-checking
  demonstration for part 1: `uv run python3 skills/beam-split-cross-check/reference/day07_beam_reachability.py`
  prints the sample total (21), the real-input total (1605), and each boundary
  bank, asserting per-cell reachability == implementation throughout. It is
  read-only against the repository and needs no third-party packages.
- `reference/day07_timeline_count.py` is the matching part 2 demonstration:
  `uv run python3 skills/beam-split-cross-check/reference/day07_timeline_count.py`
  prints the sample total (40), the real-input total (29893386035180), and each
  boundary bank, asserting enumerated == memoized == implementation throughout.
  It notes that the real input is only checkable by the memoized recurrence
  (enumerating 29893386035180 timelines is intractable) and is read-only.
- The references are deliberately independent: they never form a per-row column
  set, never reuse `day07.read_grid`, `day07._entry_column`, `day07.part1`, or
  `day07.part2`, and count splitter cells (or timelines) by explicit position,
  so agreement on the real input is independent acceptance-adjacent evidence,
  not a tautology.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_day07.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If a
reference and the implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.
