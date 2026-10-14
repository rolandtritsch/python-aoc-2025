"""Runner output and import side effects."""

import subprocess
import sys
from pathlib import Path

from aoc2025 import day00, day01
from aoc2025.main import solve

INPUTS = Path(__file__).resolve().parents[1] / "inputs"


def expected_output() -> str:
    """Return the full runner output for every implemented part."""
    values = day00.read_file(INPUTS / "Day00.txt")
    rotations = day01.read_rotations(INPUTS / "Day01.txt")
    return (
        f"Day00 - part1: {day00.part1(values)}\n"
        f"Day00 - part2: {day00.part2(values)}\n"
        f"Day01 - part1: {day01.part1(rotations)}\n"
    )


EXPECTED = expected_output()


def test_runner_output(capsys) -> None:
    solve()
    captured = capsys.readouterr()
    assert captured.out == EXPECTED
    assert captured.err == ""


def test_console_command_from_other_directory(tmp_path: Path) -> None:
    command = Path(sys.executable).parent / "solve"
    result = subprocess.run(
        [str(command)], cwd=tmp_path, capture_output=True, text=True, check=True
    )
    assert result.stdout == EXPECTED
    assert result.stderr == ""


def test_imports_are_silent(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import aoc2025; import aoc2025.day00; import aoc2025.day01; "
            "import aoc2025.main",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""
    assert result.stderr == ""
