"""Day00 examples, input parsing, and invalid-input behavior."""

from pathlib import Path

import pytest

from aoc2025 import day00

INPUTS = Path(__file__).resolve().parents[1] / "inputs"
FIB_1000 = int(
    "434665576869374564356885276750406258025646605173717804024817290895365554179490"
    "518904038798400792551692959225930803226347752096896232398733224711616429964409"
    "06533187938298969649928516003704476137795166849228875"
)


@pytest.mark.parametrize("n,expected", [(0, 0), (1, 1), (2, 1), (10, 55), (20, 6765)])
def test_fibonacci(n: int, expected: int) -> None:
    assert day00.fib(n) == expected


def test_large_fibonacci() -> None:
    assert day00.fib(1000) == FIB_1000


def test_negative_index() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        day00.fib(-1)


@pytest.mark.parametrize("filename", ["Day00.txt", "Day00Test.txt"])
def test_bundled_inputs_and_parts(filename: str) -> None:
    values = day00.read_file(INPUTS / filename)
    assert values == [10, 1000]
    assert day00.part1(values) == 55
    assert day00.part2(values) == FIB_1000


def test_parts_use_first_and_last_values() -> None:
    assert day00.part1([2, 10, 20]) == 1
    assert day00.part2([2, 10, 20]) == 6765
    assert day00.part1([10]) == day00.part2([10]) == 55


@pytest.mark.parametrize("part", [day00.part1, day00.part2])
def test_empty_part_input(part) -> None:
    with pytest.raises(ValueError, match="empty"):
        part([])


def test_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day00.read_file("")


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day00.read_file(tmp_path / "missing.txt")


@pytest.mark.parametrize("content", ["10\ninvalid\n", "10\n\n1000\n"])
def test_malformed_input(tmp_path: Path, content: str) -> None:
    path = tmp_path / "input.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        day00.read_file(path)


def test_whitespace_and_missing_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text(" 10 \n\t1000", encoding="utf-8")
    assert day00.read_file(path) == [10, 1000]


def test_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.touch()
    assert day00.read_file(path) == []
