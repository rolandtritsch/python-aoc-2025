---
name: worksheet-column-block-cross-check
description: Independently verify an AoC column-worksheet parser against a pure character-column reference that slices the grid between full-space separator columns, covering the official sample, the real input, and alignment boundary banks.
---

# Worksheet column-block cross-check

Use when a puzzle lays its data out as side-by-side vertical "problems" in a
wide text grid (Day06's trash compactor worksheet), where each problem is a
stack of numbers with an operation symbol below it and problems are separated
by a full column of only spaces. The implementation under review parses such
worksheets by splitting every line on whitespace and taking the `i`-th token
of each line as problem `i`. You need to confirm that whitespace-split parsing
really assigns every number to the problem the statement intends, without
trusting the token-index shortcut.

## Trigger

- A solution answers "sum the fold of each side-by-side vertical column of
  numbers, operator at the bottom" (Day06 part1), and the parser is the
  whitespace-split/column-index approach.
- The reviewer must independently confirm the real-input grand total (not just
  the official sample).
- Alignment is easy to get wrong: numbers within a problem may be
  left/right-aligned differently, and a wide number next to a narrow one can
  move the separator, so the token-index parse needs an independent oracle.

## Inputs

- The puzzle statement and the exact worksheet layout rule (vertical numbers,
  operator symbol below each, problems separated by a full column of spaces).
- The implementation under review (`src/aoc2025/day06.py`).
- The official sample in `inputs/Day06Test.txt` and its stated grand total.
- The real input `inputs/Day06.txt`.

## Procedure

1. Write a pure character-column reference that ignores whitespace splitting
   entirely: pad every line to the same width, find the columns that are spaces
   in *every* line (the full-space separator columns), slice the grid into
   blocks between those separators, and read each block's rows as the problem's
   numbers/operator. It must share no helper with the implementation. For
   Day06 part1 this is `grand_total`/`column_block_parse` in
   `reference/day06_column_block.py`.
2. Run the reference and the implementation on the official sample. They must
   agree with each other and with the statement's stated grand total (Day06
   part1: 4277556). Disagreement means one of them misreads the layout rule.
3. Run both on the real input and require exact agreement on the total (Day06
   part1: 6378679666679). The column-block parse is O(lines * width), so it is
   trivially tractable on the 1000-problem real worksheet.
4. Check alignment boundary banks where the token-index parse is easy to get
   wrong: a single problem that is right-aligned and one that is left-aligned,
   a single-number-row problem, mixed `+`/`*` operators in one row, a wide
   number next to a narrow one with irregular inner padding, trailing spaces
   on every line, a single problem with many number rows, and several
   single-digit problems in a row.
5. Confirm the reference rejects a worksheet whose numbers bleed across the
   separator (no full space column remains): the token containing an inner
   space makes `column_block_parse` raise ValueError, which is the correct
   "not a valid worksheet" signal.
6. Record the agreement evidence on the review issue: sample total, real-input
   total, and the boundary banks exercised, each with reference vs
   implementation value. Label the reference "pure character-column block
   parse" so a future reviewer can tell it apart from the whitespace-split
   implementation.

## Evidence and validation

- `reference/day06_column_block.py` is a runnable, self-checking demonstration:
  `uv run python3 skills/worksheet-column-block-cross-check/reference/day06_column_block.py`
  prints the sample total (4277556), the real-input total (6378679666679), and
  each boundary bank, asserting column-block == implementation throughout, and
  confirms the invalid-bank ValueError. It is read-only against the repository
  (bank worksheets are written to a temporary directory) and needs no
  third-party packages.
- The reference is deliberately independent: it never calls `str.split` on a
  worksheet line, never reuses `day06.read_worksheet`, and reads numbers by
  character position only, so agreement on the real input is independent
  acceptance-adjacent evidence, not a tautology.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_day06.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.
