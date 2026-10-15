---
name: loop-fill-rectangle-cross-check
description: Independently verify an AoC "fill a closed orthogonal loop, then find the largest red-cornered rectangle made only of red/green tiles" solution (Day09 Movie Theater part 2) against a per-cell flood-fill reference that shares no edge/interval/even-odd machinery with a scanline implementation, covering the official sample, the real input's filled volume, and boundary banks.
---

# Loop-fill rectangle cross-check

Use when a puzzle gives a list of points where consecutive points (with the list
wrapping) lie on a shared row or column, the straight segments between them plus
the enclosed region are "filled", and the answer is the largest axis-aligned
rectangle whose opposite corners are points from the list and whose every cell
is in the filled set (Day09 part 2: red tiles connected by green tiles, interior
green, largest all-red/green rectangle). The implementation under review builds
vertical/horizontal edges, computes per-row filled x-intervals with an even-odd
scanline over half-open walls plus re-added horizontal edges, merges adjacent
intervals, compresses identical rows, and answers rectangles with a
`bisect_right` coverage lookup.

## Trigger

- The answer is the largest rectangle whose corners are input points and whose
  cells all lie in a filled orthogonal loop region.
- The implementation uses edge decomposition + even-odd scanline intervals and a
  sorted-interval coverage lookup, so the reviewer needs an oracle that shares
  none of that structure.
- The reviewer must independently confirm the real-input total and the size of
  the filled region, because a wrong even-odd pairing or a wrong horizontal-edge
  boundary can change which rectangles are valid.

## Inputs

- The puzzle statement and the exact rule (loop wraps; adjacent tiles share a row
  or column; boundary plus interior is red/green; rectangle corners must be red).
- The implementation under review (`src/aoc2025/day09.py`).
- The official sample in `inputs/Day09Test.txt` with its stated part 2 answer 24
  (rectangle between `9,5` and `2,3`), and the real input `inputs/Day09.txt`
  (496 tiles, bounding box ~9.3e9 cells, answer 1439894345).
- The boundary banks from `tests/test_day09.py`.

## Procedure

1. Write an independent reference that:
   - walks each consecutive tile pair (wrapping) and emits the explicit cell
     positions of the loop boundary into a set (`boundary_cells`),
   - fills the interior by flood-filling the *exterior* of the padded bounding
     box and marking every non-exterior cell (`filled_cells`), so the whole
     computation is per-cell reachability with no interval arithmetic,
   - evaluates every red-tile pair as opposite corners and keeps the largest
     rectangle whose cells are all in the filled set, pruning pairs whose area
     is no larger than the current best (`largest_rect`).
   For Day09 this is `reference/day09_loop_fill.py`. The reference never calls
   `_edges`, `_cover_at`, `_filled_regions`, `_covers`, or `bisect`.
2. Confirm the loop reading on the sample. The sample's red tiles connect into
   one closed orthogonal loop and the largest all-red/green rectangle has area
   24, while the plain (red-cornered, unconstrained) part-1 answer is 50. The
   reference must reproduce 24 on the official sample (and the `interior-notch`
   bank pins the interior-only reading: tiles whose rectangle would poke through
   a notch are invalid).
3. Run the reference and the implementation on the official sample (both 24),
   the boundary banks (tiny square loop 9, thin rectangle loop 10, interior
   notch 8), and a corpus of small hand-built orthogonal loops (comb, L,
   staircase, T, plus, two notches, deep U, stair-notch, zigzag, skinny long,
   square). Exact agreement throughout is acceptance-adjacent evidence, not a
   transcription, because the reference uses explicit per-cell reachability.
4. Verify the real input's *filled volume* independently with Pick's theorem:
   `B` boundary cells (counted from the walked loop) and shoelace area `A` give
   `A + B/2 + 1` filled cells with no interior enumeration. This works on the
   ~9.3e9-cell bounding box where a per-cell fill is intractable. Compare it to
   the sum of the implementation's region intervals; they must agree exactly
   (real input: 7070643880).
5. The real input's *rectangle total* is reproduced by the implementation
   (1439894345); a per-cell rectangle sweep is intractable on that bounding box,
   so record that the reference cross-checks the fill volume on the real input
   and the full rectangle semantics on the sample, banks, and corpus. Report the
   per-cell reference as the "loop-fill flood-fill" oracle and Pick's theorem as
   the "shoelace volume" oracle so a future reviewer can tell them apart from
   the edge/scanline implementation.
6. Exercise boundary banks where the semantics are easy to get wrong: a tiny
   closed square loop, a one-cell-tall rectangle loop (thin horizontal), an
   interior notch that prunes a diagonal rectangle, a degenerate one-cell-tall
   loop (deep U / skinny long), and fewer than two tiles raising `ValueError`.

## Evidence and validation

- `reference/day09_loop_fill.py` is a runnable, self-checking demonstration:
  `uv run python3 skills/loop-fill-rectangle-cross-check/reference/day09_loop_fill.py`
  prints the sample total (24), the boundary banks (9, 10, 8), the corpus
  agreement (11 shapes), the real filled volume by Pick vs the implementation
  region sum (both 7070643880), the reproduced real rectangle total
  (1439894345), and asserts per-cell fill == implementation throughout. It is
  read-only against the repository and needs no third-party packages.
- The reference is deliberately independent: it never imports `day09`'s private
  helpers, never builds edges, never applies an even-odd scanline, never merges
  intervals, and never uses `bisect`.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_day09.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and the implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.