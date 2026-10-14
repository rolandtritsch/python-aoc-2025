"""Runner output and import side effects."""

import subprocess
import sys
from pathlib import Path

from aoc2025.main import solve

EXPECTED = (
    "Day00 - part1: 55\n"
    "Day00 - part2: "
    "434665576869374564356885276750406258025646605173717804024817290895365554179490"
    "518904038798400792551692959225930803226347752096896232398733224711616429964409"
    "06533187938298969649928516003704476137795166849228875\n"
    "Day01 - part1: 1129\n"
    "Day01 - part2: 6638\n"
    "Day02 - part1: 44487518055\n"
    "Day02 - part2: 53481866137\n"
    "Day03 - part1: 17207\n"
    "Day03 - part2: 170997883706617\n"
    "Day04 - part1: 1356\n"
    "Day04 - part2: 8713\n"
    "Day05 - part1: 848\n"
    "Day05 - part2: 334714395325710\n"
    "Day06 - part1: 6378679666679\n"
)


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
            "import aoc2025.day02; import aoc2025.day03; import aoc2025.day04; "
            "import aoc2025.day05; import aoc2025.day06; import aoc2025.main",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""
    assert result.stderr == ""
