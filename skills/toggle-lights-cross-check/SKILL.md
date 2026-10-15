---
name: toggle-lights-cross-check
description: Independently verify an AoC "push buttons that toggle lights, fewest total presses" solution (Day10 Factory part 1) against a subset-enumeration reference that simulates toggles on a plain boolean list and shares no GF(2) row reduction, null-space enumeration, or bit-mask algebra with the implementation under review, covering the official sample, the real input, and boundary banks.
---

# Toggle-lights cross-check

Use when a puzzle gives one machine spec per line with an indicator-light diagram
(`[.#...]`, `.` off, `#` on) and button wiring schematics (`(...)`, each button
toggles every listed light, 0-based), where pushing a button toggles the state of
each light it is wired to, and the answer is the fewest total presses to light
every machine's diagram exactly (Day10 part 1). The implementation under review
models each machine as a GF(2) linear system `A x = target`, reduces an augmented
coefficient matrix with Gaussian elimination, reads a particular solution from
the pivots, computes the null-space basis, and enumerates the null space for the
minimum popcount.

## Trigger

- The answer is a minimum number of toggling button presses, and each button is
  effectively pushed 0 or 1 times (pushing twice cancels).
- The implementation uses GF(2) Gaussian elimination + null-space enumeration
  (bit masks, pivot rows, rank, popcount), so the reviewer needs an oracle that
  shares none of that algebra.
- The reviewer must independently confirm the real-input total, because a wrong
  pivot, an incorrect particular solution, or a missed null-space combination
  can change the minimum press count while still reaching the diagram.

## Inputs

- The puzzle statement and the exact rule (lights start off; each button toggles
  the listed lights; fewest presses per machine, summed across machines).
- The implementation under review (`src/aoc2025/day10.py`).
- The official sample in `inputs/Day10Test.txt` with its stated part 1 answer 7
  (2 + 3 + 2), and the real input `inputs/Day10.txt` (163 machines, answer 417).
- The boundary banks from `tests/test_day10.py` (single light on/off, redundant
  buttons, one button wiring two lights, unconfigurable machine).

## Procedure

1. Write an independent reference that, for every machine, enumerates every
   button subset mask `0..2^b-1` (each button pushed 0 or 1 times), *simulates*
   the toggles on a plain boolean light list (`lights[light] = not lights[light]`),
   accepts masks whose resulting lights equal the diagram, and returns the
   smallest popcount among accepted masks. It must never build a coefficient
   row, pivot, rank, particular solution, null vector, or GF(2) linear
   combination. For Day10 this is `reference/day10_min_presses_bruteforce.py`.
   It may reuse only the official parser (`day10.read_machines`) so the same
   material is fed to both sides; it never calls `day10._min_presses`,
   `day10._solve_gf2`, or any private solver helper.
2. Confirm the sample reading: the official 3-machine sample totals 2 + 3 + 2 =
   7. The reference must reproduce 7 on `inputs/Day10Test.txt`.
3. Run the reference and the implementation on the official sample (both 7) and
   the boundary banks (single light required-on 1, single light required-off 0,
   redundant button pair wired to the same light 1, two independent lights 2,
   one button wiring both lights 1, unconfigurable machine raises `ValueError`).
   Exact agreement throughout is acceptance-adjacent evidence, not a
   transcription, because the reference uses explicit per-subset simulation.
4. Verify the real input's total independently with the subset enumeration
   (163 machines, 417). The real input has at most 13 buttons per machine, so
   the `O(2^b)` enumeration per machine is tractable. A seeded random fuzz over
   small light/button counts (e.g. 200 machines, 1-5 lights, 1-6 buttons) can
   additionally pin agreement beyond the fixed banks.
5. Exercise boundary banks where the semantics are easy to get wrong: a
   single-light machine requiring `#` (1) and `.` (0), duplicate buttons wired
   to the same light (must pick one, not double-count), a button wiring two
   lights at once (fewer presses than two single-light buttons), and an
   unconfigurable machine (a required-on light wired to no button, or a
   contradictory row) raising `ValueError`.

## Evidence and validation

- `reference/day10_min_presses_bruteforce.py` is a runnable, self-checking
  demonstration:
  `uv run python3 skills/toggle-lights-cross-check/reference/day10_min_presses_bruteforce.py`
  prints the sample total (7), the real-input total (417), and the boundary
  banks (1, 0, 1, 2, 1, unconfigurable), and asserts every check. It is
  read-only against the repository and needs no third-party packages.
- The reference is deliberately independent: it never imports `day10`'s private
  helpers, never builds a coefficient matrix, never performs a pivot, never
  computes a rank, and never uses a popcount null-space search.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_day10.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and the implementation totals disagree, that is an unresolved puzzle
defect for the Problem Solver on a later CTO cycle — record it and stop.