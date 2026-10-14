"""Day05 examples, range-membership boundaries, and database parsing."""

from pathlib import Path

import pytest

from aoc2025 import day05
from aoc2025.day05 import IdRange

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_RANGES = [
    IdRange(3, 5),
    IdRange(10, 14),
    IdRange(16, 20),
    IdRange(12, 18),
]
SAMPLE_AVAILABLE = [1, 5, 8, 11, 17, 32]


def test_part1_sample() -> None:
    assert day05.part1(SAMPLE_RANGES, SAMPLE_AVAILABLE) == 3


def test_part1_bundled_sample_file() -> None:
    database = day05.read_database(INPUTS / "Day05Test.txt")
    assert database.ranges == SAMPLE_RANGES
    assert database.available == SAMPLE_AVAILABLE
    assert day05.part1(database.ranges, database.available) == 3


def test_part1_real_input() -> None:
    database = day05.read_database(INPUTS / "Day05.txt")
    assert day05.part1(database.ranges, database.available) == 848


def test_part2_sample() -> None:
    assert day05.part2(SAMPLE_RANGES) == 14


def test_part2_bundled_sample_file() -> None:
    database = day05.read_database(INPUTS / "Day05Test.txt")
    assert day05.part2(database.ranges) == 14


def test_part2_real_input() -> None:
    database = day05.read_database(INPUTS / "Day05.txt")
    assert day05.part2(database.ranges) == 334714395325710


def test_part2_no_ranges() -> None:
    assert day05.part2([]) == 0


def test_part2_single_point_range() -> None:
    assert day05.part2([IdRange(7, 7)]) == 1


def test_part2_inclusive_bounds_count_endpoints() -> None:
    assert day05.part2([IdRange(3, 5)]) == 3


def test_part2_disjoint_ranges_sum_lengths() -> None:
    assert day05.part2([IdRange(1, 3), IdRange(10, 12)]) == 6


def test_part2_overlapping_ranges_count_once() -> None:
    # 16-20 and 12-18 overlap on 16, 17, 18; total distinct fresh IDs is 9.
    assert day05.part2([IdRange(16, 20), IdRange(12, 18)]) == 9


def test_part2_adjacent_ranges_merge_without_double_count() -> None:
    assert day05.part2([IdRange(1, 3), IdRange(4, 6)]) == 6


def test_part2_contained_range_adds_nothing() -> None:
    assert day05.part2([IdRange(10, 20), IdRange(12, 15)]) == 11


def test_part1_no_ranges() -> None:
    assert day05.part1([], [1, 5, 8]) == 0


def test_part1_no_available_ids() -> None:
    assert day05.part1([IdRange(1, 10)], []) == 0


def test_part1_both_empty() -> None:
    assert day05.part1([], []) == 0


def test_part1_inclusive_bounds_are_fresh() -> None:
    ranges = [IdRange(3, 5)]
    assert day05.part1(ranges, [3, 4, 5]) == 3


def test_part1_just_outside_bounds_are_spoiled() -> None:
    ranges = [IdRange(3, 5)]
    assert day05.part1(ranges, [2, 6]) == 0


def test_part1_id_below_every_range() -> None:
    ranges = [IdRange(10, 20), IdRange(30, 40)]
    assert day05.part1(ranges, [5]) == 0


def test_part1_id_above_every_range() -> None:
    ranges = [IdRange(10, 20), IdRange(30, 40)]
    assert day05.part1(ranges, [50]) == 0


def test_part1_id_in_gap_between_ranges() -> None:
    ranges = [IdRange(10, 20), IdRange(30, 40)]
    assert day05.part1(ranges, [25]) == 0


def test_part1_overlapping_ranges_count_id_once() -> None:
    # ID 17 lies in both ranges but is one available ID, counted once.
    ranges = [IdRange(16, 20), IdRange(12, 18)]
    assert day05.part1(ranges, [17, 17, 1]) == 2


def test_merge_ranges_overlap_contained_adjacent_disjoint() -> None:
    ranges = [
        IdRange(10, 20),
        IdRange(12, 15),
        IdRange(16, 30),
        IdRange(40, 50),
    ]
    assert day05._merge_ranges(ranges) == [IdRange(10, 30), IdRange(40, 50)]


def test_merge_ranges_empty() -> None:
    assert day05._merge_ranges([]) == []


def test_merge_ranges_single_range() -> None:
    assert day05._merge_ranges([IdRange(7, 9)]) == [IdRange(7, 9)]


def test_read_database_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day05.read_database("")


def test_read_database_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day05.read_database(tmp_path / "missing.txt")


def test_read_database_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("3-5\n\n1", encoding="utf-8")
    assert day05.read_database(path) == day05.Database([IdRange(3, 5)], [1])


def test_read_database_missing_separator(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("3-5\n10-14\n", encoding="utf-8")
    with pytest.raises(ValueError, match="separator"):
        day05.read_database(path)


def test_read_database_blank_line_before_ranges(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("\n3-5\n\n1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid ID"):
        day05.read_database(path)


@pytest.mark.parametrize(
    "content",
    [
        "3\n\n1\n",
        "3-5-7\n\n1\n",
        "3-\n\n1\n",
        "-5\n\n1\n",
        "a-b\n\n1\n",
        "5-3\n\n1\n",
        "3-5\n\nx\n",
        "3-5\n\n-1\n",
    ],
)
def test_read_database_invalid_content(tmp_path: Path, content: str) -> None:
    path = tmp_path / "input.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        day05.read_database(path)
