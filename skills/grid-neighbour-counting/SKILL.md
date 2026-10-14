---
name: grid-neighbour-counting
description: Independently verify an AoC grid-counting solution against a padded-grid reference that removes bounds checks, covering the official sample, the real input, and neighbour-count boundary banks.
---

# Grid neighbour counting

Use when a puzzle counts or selects cells based on how many occupied cells sit in
their adjacent positions (orthogonal plus diagonal, or orthogonal only), and you
need to confirm the implementation's count on the official sample and the real
input without trusting its bounds handling or off-by-one loops. Typical triggers
are grid puzzles with rules like "accessible when fewer than N neighbours" or a
flickering/occupancy/adjacency rule over the eight surrounding cells.

## Trigger

- A solution counts cells whose neighbour count passes a threshold.
- The reviewer must independently confirm the real-input total (not just the
  official sample).
- Boundary handling (edges, corners, single row/column) is easy to get wrong and
  needs an independent oracle.

## Inputs

- The puzzle statement and the exact neighbour-count rule.
- The implementation under review (`src/aoc2025/dayNN.py`).
- The official sample in `inputs/DayNNTest.txt` and its stated answer.
- The real input `inputs/DayNN.txt`.

## Procedure

1. Write a naive reference that pads the grid with an inert border (`.` for the
   Day04 roll grid) and then scans the original cells. Padding means every
   original cell has a full neighbour window, so the reference has **no bounds
   checks at all** — a structurally independent formulation from an
   implementation that guards each neighbour coordinate. For Day04 part1 the
   reference is `padded_count` in `reference/day04_padded_grid.py`: count rolls
   whose eight neighbours contain fewer than four rolls.
2. Run both the reference and the implementation on the official sample. They
   must agree with each other and with the statement's stated sample answer
   (Day04 part1: 13). Disagreement means one of them misreads the rule.
3. Run both on the real input and require exact agreement on the total (Day04
   part1: 1356). The real grid is only 138x138, so the padded reference is
   tractable and verifies the total independently, unlike intractable
   combinatorial brute forces.
4. Check boundary banks where the rule is easy to get wrong: an empty grid
   (0), a single isolated cell (1), a full block (only the corners stay below
   the threshold; 3x3 and 4x4 both give 4), a cell with exactly-threshold
   neighbours that must be excluded, a diagonal-only arrangement (diagonals are
   counted), and degenerate shapes (single row, single column, a lone middle
   cell, a plus/cross).
5. Record the agreement evidence on the review issue: sample total, real-input
   total, and the boundary banks exercised, each with reference vs
   implementation value. Label the reference "independent padded-grid
   brute-force" so a future reviewer can tell it apart from the implementation.

## Evidence and validation

- `reference/day04_padded_grid.py` is a runnable, self-checking demonstration:
  `python3 skills/grid-neighbour-counting/reference/day04_padded_grid.py`
  prints the sample total (13), the real-input total (1356), and the boundary
  grids, asserting padded == implementation throughout. It is read-only against
  the repository and needs no third-party packages.
- The reference's padding approach is deliberately independent: no shared
  helper, no reuse of the implementation's bounds checks, so agreement on the
  real input is independent evidence, not a tautology.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_dayNN.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.
