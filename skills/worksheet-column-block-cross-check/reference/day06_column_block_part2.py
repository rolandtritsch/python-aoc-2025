#!/usr/bin/env python3
"""Independent transpose reference for AoC 2025 Day06 part2.

The trash-compactor worksheet is a grid of problems laid out side by side:
each problem is a vertical stack of numbers with its operation symbol (``+``
or ``*``) below them. Part 2 reads cephalopod math right-to-left in columns:
each number is one character column read top-to-bottom (most significant digit
at the top), and each problem's numbers are folded with the operator below the
problem.

``src/aoc2025/day06.py`` ``part2`` reads this directly: it detects the
full-space separator columns, slices the grid into column blocks, and for each
block builds each number by joining the non-space characters of one column
across the number rows, then folds right-to-left.

This reference instead transposes the whole padded grid so each original
character column becomes a row, splits the transposed grid into blocks between
all-space rows (the transposed image of the original separator columns), reads
each block's rows as numbers (dropping the trailing operator character), and
extracts each operator from the last character of the block's rows. It shares
no helper with ``day06.read_grid`` or ``day06.part2``, so agreement on the
sample, the real input, and the boundary banks is structurally independent
acceptance-adjacent evidence for the right-to-left column reading.

It is a self-checking demonstration for the ``worksheet-column-block-cross-check``
skill: it prints each total and asserts transpose == implementation throughout.
It is read-only against the repository (bank worksheets are written to a
temporary directory) and needs no third-party packages.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from aoc2025 import day06

REPO_ROOT = Path(__file__).resolve().parents[3]

BANKS: dict[str, tuple[str, int]] = {
    "single-add-column": ("1\n2\n3\n+\n", 123),
    "single-multiply-column": ("2\n3\n4\n*\n", 234),
    "single-problem-right-aligned": ("123\n 45\n  6\n*  \n", 8544),
    "single-problem-left-aligned": ("123\n45 \n6  \n*  \n", 10950),
    "mixed-operators": ("1 2 3\n4 5 6\n* + *\n", 75),
    "single-number-row": ("7 2\n+ +\n", 9),
    "wide-next-to-narrow": ("1000 7\n2    3\n*    +\n", 73),
    "trailing-separator-column": ("7 2 \n+ + \n", 9),
}

# A worksheet whose numbers bleed across a separator has no full-space column,
# so it reads as one wide problem under both the implementation and the
# transpose reference; the totals must still agree (84).
BLEED_BANK = "12 34\n123 5\n* +\n"


def _transposed_rows(text: str) -> list[str]:
    """Return the padded worksheet text transposed so columns become rows.

    The grid's final line is the operator row, so each transposed row ends
    with its column's operator character (a space for digit-only columns).
    A blank line or a worksheet with fewer than two lines raises ValueError;
    every transposed row is right-padded to the same width.
    """
    lines = text.splitlines()
    if not lines:
        return []
    if len(lines) < 2:
        raise ValueError(
            "worksheet needs at least one number line and one operator line"
        )
    if any(not line for line in lines):
        raise ValueError("worksheet must not contain a blank line")
    width = max(len(line) for line in lines)
    rows = [line.ljust(width) for line in lines]
    return ["".join(rows[row][col] for row in range(len(rows))) for col in range(width)]


def part2_transpose(text: str) -> int:
    """Return the Day06 part2 grand total read from a transposed grid.

    Full-space transposed rows (the image of the original full-space separator
    columns) split the worksheet into problems. Each block's transposed rows
    are the numbers read right-to-left in columns: the trailing character of
    every row is its column's operator symbol (blank for digit columns), and
    each number is the row's remaining characters with spaces removed. The
    block's single non-blank operator is applied to its numbers.
    """
    transposed = _transposed_rows(text)
    if not transposed:
        return 0
    total = 0
    block: list[str] = []
    operator = "+"

    def fold_block() -> None:
        nonlocal total, block, operator
        if not block:
            return
        values: list[int] = []
        for row in block:
            symbol = row[-1]
            if symbol != " ":
                operator = symbol
            values.append(int(row[:-1].replace(" ", "")))
        total += sum(values) if operator == "+" else _product(values)
        block = []
        operator = "+"

    for row in transposed:
        if all(char == " " for char in row):
            fold_block()
        else:
            block.append(row)
    fold_block()
    return total


def _product(values: list[int]) -> int:
    """Return the product of ``values``, multiplying from 1."""
    result = 1
    for value in values:
        result *= value
    return result


def cross_check(text: str, expected: int, label: str) -> None:
    """Assert transpose, implementation, and ``expected`` totals agree."""
    transpose = part2_transpose(text)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "worksheet.txt"
        path.write_text(text, encoding="utf-8")
        impl = day06.part2(day06.read_grid(path))
    assert transpose == impl == expected, (label, transpose, impl, expected)
    print(f"{label:28s} transpose={transpose} impl={impl}")


def main() -> None:
    sample = (REPO_ROOT / "inputs" / "Day06Test.txt").read_text(encoding="utf-8")
    real = (REPO_ROOT / "inputs" / "Day06.txt").read_text(encoding="utf-8")
    cross_check(sample, 3263827, "sample")
    cross_check(real, 11494432585168, "real")
    for name, (text, expected) in BANKS.items():
        cross_check(text, expected, name)

    cross_check(BLEED_BANK, 84, "bleed-across-separator")

    for text in ("1\n", "1\n\n+"):
        try:
            part2_transpose(text)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed worksheet should raise ValueError")

    assert part2_transpose("") == 0, "empty worksheet should total 0"
    print(f"boundaries: {len(BANKS)} banks verified")
    print("transpose == implementation on all checks")


if __name__ == "__main__":
    main()
