---
name: beam-split-cross-check
description: Independently verify an AoC beam-splitting or merge-propagation simulation against an explicit per-cell reachability reference that counts splitter hits, covering the official sample, the real input, and edge banks for merging and boundary drops.
---

# Beam-split cross-check

Use when a puzzle simulates entities that propagate down a grid and merge when
they occupy the same position, and part 1 asks for a count of distinct events
(Day07's tachyon manifold: a beam moves downward, a `^` splitter stops it and
emits two new beams from its immediate left and right which then move
downward, and beams in the same column merge into one). The implementation
under review (`src/aoc2025/day07.py` `part1`) tracks a set of active beam
columns per row, so merging is implicit in the set, and you need to confirm
the splitter-hit total without trusting the column-set merge.

## Trigger

- A solution simulates downward propagation where two entities reaching the
  same cell/column merge, and the answer counts discrete events (splits).
- The implementation uses a per-row set (or other aggregate) that hides the
  merge semantics, so an independent per-cell reference is needed.
- The reviewer must independently confirm the real-input total (not just the
  official sample).
- Boundary handling is easy to get wrong: splits near the left/right grid edge
  that would spawn an out-of-range beam, and splitters that a beam never
  reaches.

## Inputs

- The puzzle statement and the exact propagation rule (downward movement,
  splitter spawns left/right, same-column merge, edge exit).
- The implementation under review (`src/aoc2025/day07.py`).
- The official sample in `inputs/Day07Test.txt` and its stated answer (21).
- The real input `inputs/Day07.txt` (142 rows x 141 cols, one `S` at row 0
  col 70).
- The boundary banks from `tests/test_day07.py`.

## Procedure

1. Write an explicit per-cell reachability reference that shares no helper
   with the implementation: a stack of beam cells starting at the `S` cell; a
   visited-cell set so two beams arriving at the same cell merge into one;
   a splitter cell adds one to the count the first time it is reached and
   spawns the cells immediately left and right one row down; any other cell
   continues one row down; cells outside the grid are dropped. For Day07 this
   is `reachability_split_count` in
   `reference/day07_beam_reachability.py`.
2. Run the reference and the implementation on the official sample. They must
   agree with each other and with the statement's stated answer (Day07: 21).
   Disagreement means one of them misreads the propagation or merge rule.
3. Run both on the real input and require exact agreement on the total (Day07
   part1: 1605). The reachability reference is O(R*C) on the stack's visited
   set, so it is trivially tractable on the 142x141 real manifold.
4. Check edge banks where the semantics are easy to get wrong: empty grid,
   single cell `S`, straight-down with no splitter, a single splitter, a
   splitter off the beam's path (missed), two beams merging into one splitter
   (split once, not twice), a splitter at the left edge (the negative spawn is
   dropped), a splitter at the right edge (the out-of-range spawn is dropped),
   and adjacent splitters (a spawned beam lands below, not sideways onto the
   neighbour splitter).
5. Record the agreement evidence on the review issue: sample total, real-input
   total, and the boundary banks exercised, each with reference vs
   implementation value. Label the reference "explicit per-cell reachability"
   so a future reviewer can tell it apart from the column-set implementation.

## Evidence and validation

- `reference/day07_beam_reachability.py` is a runnable, self-checking
  demonstration: `uv run python3 skills/beam-split-cross-check/reference/day07_beam_reachability.py`
  prints the sample total (21), the real-input total (1605), and each boundary
  bank, asserting per-cell reachability == implementation throughout. It is
  read-only against the repository and needs no third-party packages.
- The reference is deliberately independent: it never forms a per-row column
  set, never reuses `day07.read_grid`, `day07._entry_column`, or
  `day07.part1`, and counts splitter cells by explicit beam position, so
  agreement on the real input is independent acceptance-adjacent evidence,
  not a tautology.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_day07.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.
