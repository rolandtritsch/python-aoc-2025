# python-aoc-2025

![Advent of Code tree][tree]

A Python skeleton for [Advent of Code 2025][aoc], based on the Day00 template in
[scala3-aoc-2025][scala]. Only Day00 is implemented: a Fibonacci practice problem
with separate input parsing, part 1, part 2, and a runner. Read the
[Day00 problem][day00] or browse the published [API documentation][api].

## Quick start

Install [uv][] and clone this repository:

```bash
git clone https://github.com/rolandtritsch/python-aoc-2025.git
cd python-aoc-2025
uv python install
uv sync --locked
uv run solve
```

Python 3.13.7 is pinned in `.python-version` and `.tool-versions`. uv installs the
pinned interpreter when needed; asdf users can alternatively run `asdf install`.
Development dependencies are recorded in `uv.lock`.

The runner prints `Day00 - part1: 55` and `Day00 - part2:` followed by the complete
209-digit value of `fib(1000)`. Both bundled input files contain `10` and `1000`.
The `solve` command uses the top-level `inputs/` directory in this checkout through
uv's editable installation. Puzzle inputs are not bundled in built packages.

## Commands

Run these from the repository root:

```bash
uv run solve
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run pdoc aoc2025 -o build/docs
```

Tests enforce at least 80% branch-aware coverage. Open `build/docs/index.html`
after generating API docs. GitHub Actions runs the same checks and publishes
documentation from successful pushes to `main`.

For repository structure and development guidance, see [AGENTS.md][agents] and
[CONTRIBUTING.md][contributing]. Licensed under [MIT][license].

[tree]: assets/aoc-tree.png
[aoc]: https://adventofcode.com/2025
[scala]: https://github.com/rolandtritsch/scala3-aoc-2025
[day00]: problems/Day00.md
[api]: https://tedn.life/python-aoc-2025/
[uv]: https://docs.astral.sh/uv/
[agents]: AGENTS.md
[contributing]: CONTRIBUTING.md
[license]: LICENSE
