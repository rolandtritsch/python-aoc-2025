"""Day10 examples, toggle-system boundary cases, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day10

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_MACHINES = [
    day10.Machine(
        diagram=".##.",
        buttons=((3,), (1, 3), (2,), (2, 3), (0, 2), (0, 1)),
        joltages=(3, 5, 4, 7),
    ),
    day10.Machine(
        diagram="...#.",
        buttons=((0, 2, 3, 4), (2, 3), (0, 4), (0, 1, 2), (1, 2, 3, 4)),
        joltages=(7, 5, 12, 7, 2),
    ),
    day10.Machine(
        diagram=".###.#",
        buttons=((0, 1, 2, 3, 4), (0, 3, 4), (0, 1, 2, 4, 5), (1, 2)),
        joltages=(10, 11, 11, 5, 10, 5),
    ),
]


def test_part1_sample() -> None:
    assert day10.part1(SAMPLE_MACHINES) == 7


def test_part1_bundled_sample_file() -> None:
    machines = day10.read_machines(INPUTS / "Day10Test.txt")
    assert machines == SAMPLE_MACHINES
    assert day10.part1(machines) == 7


def test_part1_real_input() -> None:
    machines = day10.read_machines(INPUTS / "Day10.txt")
    assert day10.part1(machines) == 417


def test_part1_single_light_on() -> None:
    machines = [day10.Machine("#", ((0,),), (0,))]
    assert day10.part1(machines) == 1


def test_part1_single_light_already_off() -> None:
    machines = [day10.Machine(".", ((0,),), (0,))]
    assert day10.part1(machines) == 0


def test_part1_prefers_lighter_null_space_solution() -> None:
    machines = [day10.Machine("##", ((0,), (1,), (0, 1)), (0, 0))]
    assert day10.part1(machines) == 1


def test_part1_redundant_buttons_pick_one() -> None:
    machines = [day10.Machine("#", ((0,), (0,), (0,)), (0,))]
    assert day10.part1(machines) == 1


def test_part1_empty_machine_list() -> None:
    assert day10.part1([]) == 0


def test_part1_unconfigurable_machine_raises() -> None:
    machines = [day10.Machine("#.", ((1,),), (0, 0))]
    with pytest.raises(ValueError, match="cannot be configured"):
        day10.part1(machines)


def test_read_machines_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day10.read_machines("")


def test_read_machines_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day10.read_machines(tmp_path / "missing.txt")


def test_read_machines_blank_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("[#] (0) {1}\n\n[.] (0) {0}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="blank"):
        day10.read_machines(path)


def test_read_machines_malformed_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("[#] (0)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid machine"):
        day10.read_machines(path)


def test_read_machines_non_integer_joltage(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("[#] (0) {x}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid machine"):
        day10.read_machines(path)


def test_read_machines_out_of_range_button(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("[#] (5) {0}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="out-of-range"):
        day10.read_machines(path)


def test_read_machines_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("[#] (0) {1}\n[.] (0) {0}", encoding="utf-8")
    assert day10.read_machines(path) == [
        day10.Machine("#", ((0,),), (1,)),
        day10.Machine(".", ((0,),), (0,)),
    ]


def test_part2_sample() -> None:
    assert day10.part2(SAMPLE_MACHINES) == 33


def test_part2_bundled_sample_file() -> None:
    machines = day10.read_machines(INPUTS / "Day10Test.txt")
    assert day10.part2(machines) == 33


def test_part2_real_input() -> None:
    machines = day10.read_machines(INPUTS / "Day10.txt")
    assert day10.part2(machines) == 16765


def test_part2_empty_machine_list() -> None:
    assert day10.part2([]) == 0


def test_part2_single_counter() -> None:
    machines = [day10.Machine("#", ((0,),), (5,))]
    assert day10.part2(machines) == 5


def test_part2_shared_counter_splits_presses() -> None:
    machines = [day10.Machine("#", ((0,), (0,)), (7,))]
    assert day10.part2(machines) == 7


def test_part2_single_button_increments_all_counters() -> None:
    machines = [day10.Machine("##", ((0, 1),), (3, 3))]
    assert day10.part2(machines) == 3


def test_part2_fractional_relaxation_branches() -> None:
    machines = [
        day10.Machine(
            ".####",
            buttons=((0, 1, 2, 4), (0, 1, 2), (2, 3), (2, 4), (0, 3)),
            joltages=(31, 20, 40, 30, 10),
        )
    ]
    assert day10.part2(machines) == 51


def test_part2_unreachable_counter_raises() -> None:
    machines = [day10.Machine("#.", ((1,),), (1, 0))]
    with pytest.raises(ValueError, match="cannot be configured"):
        day10.part2(machines)
