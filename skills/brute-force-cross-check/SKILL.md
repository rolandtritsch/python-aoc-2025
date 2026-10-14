---
name: brute-force-cross-check
description: Verify an optimized AoC solution against a tiny independent brute-force reference on the official sample and the real input, and record agreement as acceptance-adjacent evidence.
---

# Brute-force cross-check

Use when reviewing (or before publishing) a solution that applies a clever
optimization — a suffix-max, a sliding window, a two-pointer scan, a greedy
rule, or dynamic programming — and you need to confirm the optimized code
actually computes what the statement asks. The reference solver is deliberately
naive: enumerate every candidate directly from the statement, never reuse the
optimized algorithm's insight.

## Trigger

- A solver produced a non-obvious optimization whose result is the puzzle answer.
- The reviewer must independently confirm the optimized algorithm's real-input
  total (not just the official sample).
- An edge case is ambiguous from the statement and needs a definitional oracle.

## Inputs

- The puzzle statement and the exact rule being implemented.
- The optimized implementation under review (`src/aoc2025/dayNN.py`).
- The official sample in `inputs/DayNNTest.txt` and its stated answer.
- The real input `inputs/DayNN.txt`.

## Procedure

1. Write a naive reference in a scratch file (or an inline `python3 -c`) that
   enumerates every candidate directly from the statement. For Day03 part1 the
   reference is `max(d[i] * 10 + d[j])` over every `i < j` in each bank
   (O(n^2)); see `reference/day03_pair_joltage.py`. For Day03 part2 the
   reference enumerates every `count`-element subsequence via
   `itertools.combinations`; see `reference/day03_k_digit_subsequence.py`.
   Keep it independent: no shared helper, no reuse of the optimized code's
   structural shortcut.
2. Run both the reference and the optimized function on the official sample.
   They must agree with each other and with the statement's stated sample answer
   (Day03 part1: 357; Day03 part2: 3121910778619). Disagreement means one of
   them misreads the rule.
3. Run both on the real input and require exact agreement on the total, but only
   when the reference stays tractable (Day03 banks are 100 digits, so the
   C(100,12) brute force cannot finish). Record both numbers. Agreement is
   strong but not proof: identical bugs can coincidentally agree, so also
   confirm a few boundary banks by hand.
4. Check boundary banks where the rule is easy to get wrong, such as an
   ascending sequence (`123456789 -> 89`), descending (`987654321 -> 98`),
   equal digits (`55555 -> 55`), a two-digit bank (`12 -> 12`), and a
   short/non-digit bank that the parser must reject. For a `count > 1` puzzle
   also check an exact-length bank (`987654321111` stays unchanged), a
   leading-small bank (`19999999999999 -> 999999999999`), and a
   `count <= 0` / too-short bank that must raise.
5. Record the agreement evidence on the review issue: sample total, real-input
   total, and the edge cases exercised, each with the reference vs optimized
   value. Label the reference "independent O(n^2) brute-force" or the like so a
   future reviewer can tell it apart from the optimized implementation.

## Evidence and validation

- `reference/day03_pair_joltage.py` is a runnable, self-checking demonstration:
  `python3 skills/brute-force-cross-check/reference/day03_pair_joltage.py`
  prints the sample total (357), the real-input total (17207), and
  the boundary banks, asserting brute-force == optimized throughout.
  It is read-only against the repository and needs no third-party packages.
- `reference/day03_k_digit_subsequence.py` is the Day03 part2 analogue: it
  cross-checks the monotonic-stack greedy against `itertools.combinations` on
  the sample (3121910778619), boundary banks, and 2000 seeded random small
  banks, then verifies the real-input total (170997883706617) through the fast
  implementation alone because the C(100,12) brute force is intractable.
  Run it with `python3 skills/brute-force-cross-check/reference/day03_k_digit_subsequence.py`.
- Do not weaken a solution's own regression tests to make a cross-check appear
  successful; the reference is an additional oracle, not a replacement for
  `tests/test_dayNN.py`.

## Stopping conditions

Stop after recording the agreement evidence and any discrepancy. Do not submit
an answer, change the puzzle's expected answer, or start another part. If the
reference and optimized totals disagree, that is an unresolved puzzle defect for
the Problem Solver on a later CTO cycle — record it and stop.
