"""Deterministic repo-evidence report behavior for the review workflow."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import aoc_repo_check


def fake_runner(results: dict[tuple[tuple[str, ...], str], tuple[int, str]]):
    """Return a Runner recording calls and serving canned (code, output) pairs."""

    def runner(argv: list[str], cwd: str) -> tuple[int, str]:
        key = (tuple(argv), cwd)
        if key not in results:
            raise AssertionError(f"unexpected invocation: {key!r}")
        return results[key]

    return runner


def test_git_state_parity() -> None:
    runner = fake_runner(
        {
            (("git", "rev-parse", "HEAD"), "/repo"): (0, "abc123\n"),
            (("git", "rev-parse", "origin/main"), "/repo"): (0, "abc123\n"),
            (("git", "status", "--porcelain"), "/repo"): (0, ""),
        }
    )
    state = aoc_repo_check.git_state("/repo", runner)
    assert state["head"] == "abc123"
    assert state["originMain"] == "abc123"
    assert state["parity"] is True
    assert state["clean"] is True


def test_git_state_dirty_or_diverged() -> None:
    runner = fake_runner(
        {
            (("git", "rev-parse", "HEAD"), "/repo"): (0, "abc123\n"),
            (("git", "rev-parse", "origin/main"), "/repo"): (0, "def456\n"),
            (("git", "status", "--porcelain"), "/repo"): (
                0,
                " M src/aoc2025/day02.py\n",
            ),
        }
    )
    state = aoc_repo_check.git_state("/repo", runner)
    assert state["parity"] is False
    assert state["clean"] is False


def test_git_state_missing_origin() -> None:
    runner = fake_runner(
        {
            (("git", "rev-parse", "HEAD"), "/repo"): (0, "abc123\n"),
            (("git", "rev-parse", "origin/main"), "/repo"): (
                128,
                "fatal: bad revision\n",
            ),
            (("git", "status", "--porcelain"), "/repo"): (0, ""),
        }
    )
    state = aoc_repo_check.git_state("/repo", runner)
    assert state["parity"] is False
    assert state["originMain"] == ""


def test_parse_pytest_counts_and_coverage() -> None:
    output = (
        "src/aoc2025/day02.py         56      0     34      0   100%\n"
        "TOTAL                       147      0     70      0   100%\n"
        "Required test coverage of 80% reached. Total coverage: 100.00%\n"
        "===================== 128 passed in 26.20s =====================\n"
    )
    parsed = aoc_repo_check.parse_pytest(output)
    assert parsed["passed"] == 128
    assert parsed["failed"] == 0
    assert parsed["coverage"] == 100.0


def test_parse_pytest_failures() -> None:
    output = (
        "========================= 1 failed, 127 passed =========================\n"
    )
    parsed = aoc_repo_check.parse_pytest(output)
    assert parsed["passed"] == 127
    assert parsed["failed"] == 1


def test_parse_pytest_missing_coverage() -> None:
    parsed = aoc_repo_check.parse_pytest("no coverage line here")
    assert parsed["passed"] == 0
    assert parsed["coverage"] is None


def test_parse_solve_answers() -> None:
    output = (
        "Day00 - part1: 55\n"
        "Day01 - part2: 6638\n"
        "Day02 - part1: 44487518055\n"
        "Day02 - part2: 53481866137\n"
    )
    answers = aoc_repo_check.parse_solve(output)
    assert answers == {
        "0.1": "55",
        "1.2": "6638",
        "2.1": "44487518055",
        "2.2": "53481866137",
    }


def test_parse_solve_ignores_unimplemented_parts() -> None:
    assert aoc_repo_check.parse_solve("Day03 - part1: (not implemented)\n") == {}


def test_tail_keeps_nonempty_lines() -> None:
    assert aoc_repo_check.tail("a\n\nb\nc\n") == "a\nb\nc"
    assert aoc_repo_check.tail("x\ny\n", lines=1) == "y"


def test_build_report_passes_only_when_everything_green(tmp_path: Path) -> None:
    runner = fake_runner(
        {
            (("git", "rev-parse", "HEAD"), str(tmp_path)): (0, "abc123\n"),
            (("git", "rev-parse", "origin/main"), str(tmp_path)): (0, "abc123\n"),
            (("git", "status", "--porcelain"), str(tmp_path)): (0, ""),
            (
                ("uv", "run", "--locked", "ruff", "format", "--check", "."),
                str(tmp_path),
            ): (
                0,
                "16 files already formatted\n",
            ),
            (("uv", "run", "--locked", "ruff", "check", "."), str(tmp_path)): (
                0,
                "All checks passed!\n",
            ),
            (("uv", "run", "--locked", "pytest"), str(tmp_path)): (
                0,
                "Total coverage: 100.00%\n128 passed\n",
            ),
            (("uv", "run", "--locked", "solve"), str(tmp_path)): (
                0,
                "Day02 - part2: 53481866137\n",
            ),
        }
    )
    report = aoc_repo_check.build_report(str(tmp_path), runner=runner)
    assert report["passed"] is True
    assert report["git"]["parity"] is True
    assert report["checks"]["tests"]["passed"] == 128
    assert report["checks"]["tests"]["coverage"] == 100.0
    assert report["checks"]["solve"]["answers"] == {"2.2": "53481866137"}
    assert report["schema"] == "aoc-repo-check-v1"


def test_build_report_fails_on_any_red_check(tmp_path: Path) -> None:
    runner = fake_runner(
        {
            (("git", "rev-parse", "HEAD"), str(tmp_path)): (0, "abc123\n"),
            (("git", "rev-parse", "origin/main"), str(tmp_path)): (0, "abc123\n"),
            (("git", "status", "--porcelain"), str(tmp_path)): (0, ""),
            (
                ("uv", "run", "--locked", "ruff", "format", "--check", "."),
                str(tmp_path),
            ): (
                0,
                "16 files already formatted\n",
            ),
            (("uv", "run", "--locked", "ruff", "check", "."), str(tmp_path)): (
                1,
                "E501 line too long\n",
            ),
            (("uv", "run", "--locked", "pytest"), str(tmp_path)): (
                0,
                "128 passed\n",
            ),
            (("uv", "run", "--locked", "solve"), str(tmp_path)): (
                0,
                "Day02 - part2: 53481866137\n",
            ),
        }
    )
    report = aoc_repo_check.build_report(str(tmp_path), runner=runner)
    assert report["passed"] is False
    assert report["checks"]["lint"]["exitCode"] == 1
    assert report["checks"]["lint"]["passed"] is False


def test_run_command_reports_missing_executable(tmp_path: Path) -> None:
    code, output = aoc_repo_check.run_command(
        ["definitely-not-a-real-command-xyz"], str(tmp_path)
    )
    assert code == 127
    assert "not found" in output


def test_cli_prints_json_report(tmp_path: Path) -> None:
    import subprocess
    import sys

    script = Path(__file__).resolve().parents[1] / "scripts" / "aoc_repo_check.py"
    result = subprocess.run(
        [sys.executable, str(script), "--repo", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["repo"] == str(tmp_path)
    assert report["passed"] is False
