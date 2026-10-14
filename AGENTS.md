# Repository guidance

See [README.md][readme] for usage and [CONTRIBUTING.md][contributing] for the
contribution workflow. This repository is a Python adaptation of the local
Scala Day00 skeleton at commit `da340d8357f04e69c0ee68f26d9cc9dd8857f840`.

## Structure

- `src/aoc2025/day00.py`: Fibonacci implementation and file parsing.
- `src/aoc2025/main.py`: runner, exposed as `uv run solve`.
- `tests/`: per-day tests and runner integration tests.
- `inputs/`: full and sample inputs, named `Day00.txt` and `Day00Test.txt`.
- `problems/`: written problem statements, starting with `Day00.md`.
- `scripts/`: reusable deterministic helpers for the AoC workflow.
- `skills/`: distilled review lessons, one directory per skill.
- `assets/`: the tree image reused from the Scala blueprint.
- `hooks/`: the pre-push quality check.
- `.github/workflows/ci.yml`: checks, generated API docs, and Pages deployment.

The package uses a standard `src` layout and uv's build backend. Runtime code has
no third-party dependencies. Python 3.13.7 is pinned; Ruff, pytest, pytest-cov, and
pdoc are development dependencies locked in `uv.lock`.

## Implementation conventions

Use typed functions with docstrings, snake_case names, and separate parsing and
part functions. Keep modules silent on import. Day00 is a practice exercise, not
an official AoC day: fib(0) is 0 and fib(1) is 1; part 1 uses the first input value
and part 2 the last. Python integers retain large answers without special types.

Default runner inputs are resolved relative to the source checkout, independently
of the working directory. The runner requires an editable installation because
`inputs/` stays outside the package. API docs must be generated without reading
inputs or running solutions on import.

Add later days only when requested, with a problem statement, input fixtures,
solution module, tests, and an explicit runner entry. Add reusable utilities only
after repeated puzzle requirements justify them. No grid/search framework or
Paperclip runtime configuration belongs in this skeleton.

## Company operation

The separate **AoC Solver 2025 Python** company uses this repository as its
canonical solution checkout. Day00 stays the practice template. The company
authorizes one day/part at a time, through Day12, with review before advancement.

Use `src/aoc2025/dayNN.py`, `tests/test_dayNN.py`, `problems/DayNNProblem.txt`,
`inputs/DayNN.txt`, and `inputs/DayNNTest.txt` for subsequent days. Name active
part tests `test_part1_*` and `test_part2_*` so pytest JUnit output supplies
unambiguous per-part evidence. Sample, edge, and real-input assertions remain
meaningful; skipped tests and tests for another part do not establish completion.
Print only implemented runner parts as `DayNN - partP: <answer>`. Do not fabricate
numeric placeholders for unimplemented parts.

Personal inputs and samples are tracked and pushed by explicit owner choice,
matching the Scala repository. Do not add ignore rules for inputs. Cache material
and fetch only the authorized day/part. Credentials stay outside this repository.

Read applicable `skills/*/SKILL.md` before repeating work. Reviewed reusable
improvements belong in this repository's `skills/` and `scripts/`, with discovery
guidance here. Company monitoring tooling stays in the company package.

`scripts/aoc_verdict_extract.py` classifies saved AoC answer HTML and extracts
accepted-answer codes for reconciling ambiguous submission responses; see
`skills/verdict-reconciliation/SKILL.md`. It reports `completed_day` for an
authenticated day page that marks both parts complete, including when that
marker sits outside the article, and `matchedPart` (1-based) attributing an
`--answer` match to part 1 or part 2 by accepted-code document order. Add new
helpers only after repeated puzzle or workflow requirements justify them.

`scripts/aoc_repo_check.py` runs the standard validation commands (format,
lint, tests, solve) plus a git parity/cleanliness check and prints one JSON
evidence report; see the `Validation` section below for the exact commands it
wraps. Use it in a review to capture deterministic evidence instead of
hand-copying command output: `python3 scripts/aoc_repo_check.py [--repo DIR]`
(defaults to `$AOC_REPO_DIR` or the current directory). It is read-only and
exits nonzero if any check fails or the working tree is dirty or diverged.

`skills/brute-force-cross-check/SKILL.md` distills how to verify an optimized
solution (suffix-max, sliding window, greedy rule) against a tiny independent
brute-force reference on the official sample, the real input, and boundary
banks. Use it when a review must independently confirm an optimized
implementation's real-input total. Runnable Day03 references:
`skills/brute-force-cross-check/reference/day03_pair_joltage.py` (part 1,
O(n^2) ordered pairs) and
`skills/brute-force-cross-check/reference/day03_k_digit_subsequence.py`
(part 2, `itertools.combinations` on the 12-digit subsequence, including
seeded random small-bank agreement; the C(100,12) brute force on the real
input is intractable so that reference verifies the real total via the fast
implementation alone).

`skills/grid-neighbour-counting/SKILL.md` distills how to independently verify
a grid-counting solution whose rule is a threshold on occupied neighbours
(orthogonal plus diagonal, or orthogonal only) using a padded-grid reference
that removes all bounds checks, so the reference is structurally independent of
an implementation that guards each neighbour coordinate. Use it when a review
must confirm a neighbour-threshold count on the official sample, the real
input, and degenerate boundary banks (empty, single cell, full block, exactly-
threshold exclusion, diagonal-only, single row/column). Runnable Day04
references: `skills/grid-neighbour-counting/reference/day04_padded_grid.py`
(part 1, counts rolls with fewer than four occupied neighbours; sample 13,
real input 1356, 10 boundary grids, padded == implementation throughout) and
`skills/grid-neighbour-counting/reference/day04_cascade_removal.py` (part 2,
synchronous round-removal of accessible rolls mirroring the statement's worked
example; sample 43, real input 8713, the same boundary grids, round-removal ==
implementation throughout). Run either with `uv run python3`.

`skills/range-membership-cross-check/SKILL.md` distills how to independently
verify an interval-membership or interval-union solution whose rule is
"inclusive range, falls into at least one range" using independent references
that share no structural shortcut with an implementation that merges ranges and
binary-searches or sums merged lengths. Use it when a review must confirm an
inclusive-range membership count or interval-union total on the official
sample, the real input, and interval boundary banks (empty, no ranges, no
queries, inclusive bounds, just outside, below/above/in-gap, overlap-once,
adjacent-touching, contained, contained-touching-at-endpoint, single-point,
duplicate queries, many single points, unsorted input). Runnable Day05
references:
`skills/range-membership-cross-check/reference/day05_naive_membership.py`
(part 1, counts available IDs fresh in at least one range; sample 3, real input
848, 13 boundary banks, naive == implementation throughout) and
`skills/range-membership-cross-check/reference/day05_union_sweep.py`
(part 2, endpoint-sweep union length over the ranges themselves; sample 14,
real input 334714395325710, 10 interval-union banks, sweep == implementation
throughout). Run them with
`uv run python3 skills/range-membership-cross-check/reference/day05_naive_membership.py`
and
`uv run python3 skills/range-membership-cross-check/reference/day05_union_sweep.py`.

`skills/worksheet-column-block-cross-check/SKILL.md` distills how to
independently verify a column-worksheet parser whose rule is "vertical stack
of numbers with the operation symbol below, problems separated by a full
column of only spaces" using a pure character-column reference that slices the
padded grid between full-space separator columns and reads numbers by character
position only — never splitting a line on whitespace and sharing no helper
with an implementation that takes the i-th token of every line. Use it when a
review must confirm a whitespace-split worksheet parser's grand total on the
official sample, the real input, and alignment boundary banks (right- and
left-aligned single problems, single number row, mixed operators, wide next to
narrow, trailing spaces, many rows, adjacent single digits) plus the
separator-broken invalid bank. Runnable Day06 part1 reference:
`skills/worksheet-column-block-cross-check/reference/day06_column_block.py`
(sample 4277556, real input 6378679666679, 8 boundary banks, invalid bank
raises ValueError, column-block == implementation throughout). Run it with
`uv run python3 skills/worksheet-column-block-cross-check/reference/day06_column_block.py`.
The same skill covers Day06 part2's right-to-left column reading (each number
is one character column read top-to-bottom) with a structurally different
transpose reference: `skills/worksheet-column-block-cross-check/reference/day06_column_block_part2.py`
transposes the whole padded grid so each column becomes a row, splits on
all-space rows (the separator columns' image), and reads each block's rows as
numbers with the operator from the trailing character (sample 3263827, real
input 11494432585168, 8 part2 boundary banks, bleed-across-separator bank
agrees at 84, malformed worksheets raise ValueError, transpose ==
implementation throughout). Run it with
`uv run python3 skills/worksheet-column-block-cross-check/reference/day06_column_block_part2.py`.

## Validation

```bash
uv sync --locked
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked pytest
uv run --locked solve
uv run --locked pdoc aoc2025 -o build/docs
```

Tests require 80% coverage, including branch coverage. Generated environments,
coverage data, and documentation output are ignored. Do not commit them.
Update README for usage changes, and this file for implementation conventions.

[readme]: README.md
[contributing]: CONTRIBUTING.md
