# Contributing

See [README.md][readme] for setup and [AGENTS.md][agents] for implementation
conventions.

## Development workflow

```bash
uv python install
uv sync --locked
git config core.hooksPath hooks
git switch -c roland/ad-hoc/describe-your-change
```

Use `roland/<ticket-id>/<3-word-description>` when working from a ticket. Keep
changes focused, add tests for new behavior, and use type annotations and
docstrings for public functions. Runtime dependencies should remain unnecessary
until a puzzle establishes a need for them.

Format changes explicitly, then run the checks:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
uv run solve
uv run pdoc aoc2025 -o build/docs
```

The pre-push hook checks formatting, lint, and tests without rewriting source.
Tests enforce an 80% minimum with branch coverage. CI also runs Day00 and builds
the API documentation. Open `build/docs/index.html` to inspect generated docs.

Update dependencies with `uv add --dev <package>` and commit both `pyproject.toml`
and `uv.lock`. Use `uv sync --locked` to reproduce the committed environment.

## Pull requests

Commit the intended files, push the branch, and open a pull request:

```bash
git push -u origin roland/ad-hoc/describe-your-change
gh pr create --title "ad-hoc: describe-your-change" --body ""
gh pr checks
```

Use the ticket ID in the title when one exists. A committer reviews and merges
after CI succeeds. Successful pushes to `main` publish API docs to GitHub Pages;
pull requests build docs without deploying them.

[readme]: README.md
[agents]: AGENTS.md
