"""Day06 examples, worksheet parsing, and fold boundaries."""

from pathlib import Path

import pytest

from aoc2025 import day06
from aoc2025.day06 import Worksheet

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_ROWS = [
    [123, 328, 51, 64],
    [45, 64, 387, 23],
    [6, 98, 215, 314],
]
SAMPLE_OPERATORS = ["*", "+", "*", "+"]

SAMPLE_GRID = [
    "123 328  51 64 ",
    " 45 64  387 23 ",
    "  6 98  215 314",
    "*   +   *   +  ",
]


def worksheet(rows: list[list[int]], operators: list[str]) -> Worksheet:
    return Worksheet(rows, operators)


def grid(*lines: str) -> list[str]:
    width = max(len(line) for line in lines)
    return [line.ljust(width) for line in lines]


def test_part1_sample() -> None:
    assert day06.part1(worksheet(SAMPLE_ROWS, SAMPLE_OPERATORS)) == 4277556


def test_part1_bundled_sample_file() -> None:
    parsed = day06.read_worksheet(INPUTS / "Day06Test.txt")
    assert parsed.number_rows == SAMPLE_ROWS
    assert parsed.operators == SAMPLE_OPERATORS
    assert day06.part1(parsed) == 4277556


def test_part1_real_input() -> None:
    parsed = day06.read_worksheet(INPUTS / "Day06.txt")
    assert day06.part1(parsed) == 6378679666679


def test_part1_single_add_problem() -> None:
    assert day06.part1(worksheet([[3], [4], [5]], ["+"])) == 12


def test_part1_single_multiply_problem() -> None:
    assert day06.part1(worksheet([[2], [3], [4]], ["*"])) == 24


def test_part1_single_number_row() -> None:
    assert day06.part1(worksheet([[7], [2]], ["+"])) == 9


def test_part1_mixed_operators_sum_answers() -> None:
    rows = [[1, 2, 3], [4, 5, 6]]
    operators = ["*", "+", "*"]
    assert day06.part1(worksheet(rows, operators)) == 4 + 7 + 18


def test_part1_empty_worksheet() -> None:
    assert day06.part1(worksheet([], [])) == 0


def test_read_worksheet_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day06.read_worksheet("")


def test_read_worksheet_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day06.read_worksheet(tmp_path / "missing.txt")


def test_read_worksheet_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1 2\n3 4\n+ *", encoding="utf-8")
    assert day06.read_worksheet(path) == Worksheet([[1, 2], [3, 4]], ["+", "*"])


def test_read_worksheet_blank_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1\n\n+", encoding="utf-8")
    with pytest.raises(ValueError, match="blank"):
        day06.read_worksheet(path)


def test_read_worksheet_single_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="number line and one operator"):
        day06.read_worksheet(path)


@pytest.mark.parametrize(
    "content",
    [
        "1 2\n3\n+ *\n",
        "1\n3 4\n+ *\n",
        "a 2\n3 4\n+ *\n",
        "1 2\n3 4\nx *\n",
        "1 -2\n3 4\n+ *\n",
    ],
)
def test_read_worksheet_invalid_content(tmp_path: Path, content: str) -> None:
    path = tmp_path / "input.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        day06.read_worksheet(path)


def test_part2_sample() -> None:
    assert day06.part2(SAMPLE_GRID) == 3263827


def test_part2_bundled_sample_file() -> None:
    assert day06.part2(day06.read_grid(INPUTS / "Day06Test.txt")) == 3263827


def test_part2_real_input() -> None:
    assert day06.part2(day06.read_grid(INPUTS / "Day06.txt")) == 11494432585168


def test_part2_single_add_column() -> None:
    assert day06.part2(grid("1", "2", "3", "+")) == 123


def test_part2_single_multiply_column() -> None:
    assert day06.part2(grid("2", "3", "4", "*")) == 234


def test_part2_single_problem_right_aligned() -> None:
    assert day06.part2(grid("123", " 45", "  6", "*  ")) == 8544


def test_part2_single_problem_left_aligned() -> None:
    assert day06.part2(grid("123", "45 ", "6  ", "*  ")) == 10950


def test_part2_mixed_operators() -> None:
    assert day06.part2(grid("1 2 3", "4 5 6", "* + *")) == 75


def test_part2_single_number_row() -> None:
    assert day06.part2(grid("7 2", "+ +")) == 9


def test_part2_wide_next_to_narrow() -> None:
    assert day06.part2(grid("1000 7", "2    3", "*    +")) == 73


def test_part2_empty_grid() -> None:
    assert day06.part2([]) == 0


def test_part2_trailing_separator_column() -> None:
    assert day06.part2(grid("7 2 ", "+ + ")) == 9


def test_read_grid_preserves_columns() -> None:
    assert day06.read_grid(INPUTS / "Day06Test.txt") == SAMPLE_GRID


def test_read_grid_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day06.read_grid("")


def test_read_grid_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day06.read_grid(tmp_path / "missing.txt")


def test_read_grid_single_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="number line and one operator"):
        day06.read_grid(path)


def test_read_grid_blank_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1\n\n+", encoding="utf-8")
    with pytest.raises(ValueError, match="blank"):
        day06.read_grid(path)


def test_read_grid_pads_to_widest_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("123\n45\n6\n*\n", encoding="utf-8")
    assert day06.read_grid(path) == ["123", "45 ", "6  ", "*  "]
