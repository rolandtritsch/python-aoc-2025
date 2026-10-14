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
