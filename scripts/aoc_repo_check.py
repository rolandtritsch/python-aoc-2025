#!/usr/bin/env python3
"""Run the repository's standard validation and emit a deterministic evidence report.

Each solve/submit/review repeats the same mechanical checks against the shared
checkout: git parity with origin/main, formatting, lint, the full test suite
with coverage, and the runner output. This read-only helper runs all of them
and prints one JSON object so the evidence has a stable shape instead of
hand-copied command output.

The script never modifies the repository: ``ruff format --check`` and
``ruff check`` are read-only, pytest writes only git-ignored coverage/cache
files, and ``solve`` only reads inputs. Git state is reported, never changed.

Examples
--------
    python3 scripts/aoc_repo_check.py
    python3 scripts/aoc_repo_check.py --repo /path/to/python-aoc-2025

The JSON report includes ``git.head``, ``git.originMain``, ``git.clean``
(empty working tree) and ``git.parity`` (head equals origin/main), one
``checks`` entry per standard command with ``exitCode``/``passed`` and a
bounded ``outputTail``, plus parsed ``tests.passed`` and ``tests.coverage``
and ``solve.answers`` keyed as ``"{day}.{part}"``. The overall ``passed``
field and the process exit status are green only when every check passes and
git parity holds; a nonzero exit flags a failed or ambiguous repo state for
the reviewer to explain.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

REPO_ENV = "AOC_REPO_DIR"

STANDARD_CHECKS: list[tuple[str, list[str]]] = [
    ("format", ["uv", "run", "--locked", "ruff", "format", "--check", "."]),
    ("lint", ["uv", "run", "--locked", "ruff", "check", "."]),
    ("tests", ["uv", "run", "--locked", "pytest"]),
    ("solve", ["uv", "run", "--locked", "solve"]),
]

TAIL_LINES = 30
OUTPUT_LIMIT = 60_000
RUN_TIMEOUT = 600

Runner = Callable[[list[str], str], tuple[int, str]]


def run_command(
    argv: list[str], cwd: str, timeout: int = RUN_TIMEOUT
) -> tuple[int, str]:
    """Run ``argv`` in ``cwd`` and return ``(exit_code, output)``.

    Captures combined stdout/stderr and truncates output that exceeds
    ``OUTPUT_LIMIT`` characters so a pathological command cannot produce an
    unbounded report. A missing executable is reported as exit code 127 with
    the error text rather than raising.
    """
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = completed.stdout + completed.stderr
        code = completed.returncode
    except FileNotFoundError as error:
        return 127, f"command not found: {argv[0]} ({error})"
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or "") + (error.stderr or "")
        return 124, output
    if len(output) > OUTPUT_LIMIT:
        output = output[-OUTPUT_LIMIT:]
    return code, output


def tail(output: str, lines: int = TAIL_LINES) -> str:
    """Return the last ``lines`` nonempty lines of ``output`` as one string."""
    kept = [line for line in output.splitlines() if line.strip()][-lines:]
    return "\n".join(kept)


def git_state(cwd: str, runner: Runner = run_command) -> dict[str, object]:
    """Return head, origin/main, working-tree cleanliness, and parity."""
    head_code, head_out = runner(["git", "rev-parse", "HEAD"], cwd)
    main_code, main_out = runner(["git", "rev-parse", "origin/main"], cwd)
    status_code, status_out = runner(["git", "status", "--porcelain"], cwd)
    head = head_out.strip() if head_code == 0 else ""
    origin_main = main_out.strip() if main_code == 0 else ""
    dirty = status_code == 0 and bool(status_out.strip())
    return {
        "head": head,
        "originMain": origin_main,
        "clean": not dirty,
        "parity": bool(head) and head == origin_main,
    }


def parse_pytest(output: str) -> dict[str, object]:
    """Extract passed/failed counts and total coverage from pytest output."""
    passed = 0
    failed = 0
    summary = re.search(r"(\d+)\s+passed", output)
    if summary:
        passed = int(summary.group(1))
    failed_match = re.search(r"(\d+)\s+failed", output)
    if failed_match:
        failed = int(failed_match.group(1))
    coverage = None
    coverage_match = re.search(r"Total coverage:\s*([0-9.]+)%", output)
    if coverage_match:
        coverage = float(coverage_match.group(1))
    return {"passed": passed, "failed": failed, "coverage": coverage}


def parse_solve(output: str) -> dict[str, str]:
    """Extract ``DayNN - partP: answer`` lines as ``{day.part: answer}``."""
    answers: dict[str, str] = {}
    for match in re.finditer(
        r"^Day(\d{2}) - part([12]):\s*(\S+)\s*$", output, re.MULTILINE
    ):
        answers[f"{int(match.group(1))}.{int(match.group(2))}"] = match.group(3)
    return answers


def run_checks(
    cwd: str,
    checks: list[tuple[str, list[str]]] | None = None,
    runner: Runner = run_command,
) -> dict[str, dict[str, object]]:
    """Run each standard check and return per-check pass/fail results."""
    results: dict[str, dict[str, object]] = {}
    for name, argv in checks or STANDARD_CHECKS:
        code, output = runner(argv, cwd)
        result: dict[str, object] = {
            "command": " ".join(argv),
            "exitCode": code,
            "passed": code == 0,
            "outputTail": tail(output),
        }
        if name == "tests":
            result.update(parse_pytest(output))
        if name == "solve":
            result["answers"] = parse_solve(output)
        results[name] = result
    return results


def build_report(
    cwd: str,
    checks: list[tuple[str, list[str]]] | None = None,
    runner: Runner = run_command,
) -> dict[str, object]:
    """Assemble the full evidence report and the overall pass flag."""
    state = git_state(cwd, runner)
    results = run_checks(cwd, checks, runner)
    passed = (
        bool(state["parity"])
        and bool(state["clean"])
        and all(result["passed"] for result in results.values())
    )
    return {
        "schema": "aoc-repo-check-v1",
        "repo": cwd,
        "git": state,
        "checks": results,
        "passed": passed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run standard repo validation and emit a JSON evidence report."
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=os.environ.get(REPO_ENV) or Path.cwd(),
        help="checkout to validate (default: $AOC_REPO_DIR or the current directory)",
    )
    args = parser.parse_args(argv)
    report = build_report(str(args.repo))
    print(json.dumps(report, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
