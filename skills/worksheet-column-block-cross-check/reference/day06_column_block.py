#!/usr/bin/env python3
"""Independent column-block worksheet reference for AoC 2025 Day06 part1.

The trash-compactor worksheet is a grid of problems laid out side by side:
each problem is a vertical stack of numbers with its operation symbol (``+``
or ``*``) below them. ``src/aoc2025/day06.py`` reads it by splitting every
line on whitespace, so each problem is the ``i``-th token of every line. That
is correct whenever problems are separated by a full column of only spaces.

This reference instead parses the raw character grid: it finds the columns
that are spaces in *every* line (the full-space separator columns), slices the
grid into blocks between those separators, and reads each block's rows as the
problem's numbers/operator. It never splits a line on whitespace and shares no
helper with ``day06.read_worksheet`` or ``day06.part1``, so agreement on the
sample, the real input, and the boundary banks is structurally independent
acceptance-adjacent evidence.

It is a self-checking demonstration for the ``worksheet-column-block-cross-check``
skill: it prints each total and asserts column-block == implementation
throughout. It is read-only against the repository (bank worksheets are written
to a temporary directory) and needs no third-party packages.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from aoc2025 import day06

REPO_ROOT = Path(__file__).resolve().parents[3]

BANKS: dict[str, tuple[str, int]] = {
    "single-problem-right-aligned": ("123\n 45\n  6\n*\n", 33210),
    "single-problem-left-aligned": ("123\n45 \n6  \n*\n", 33210),
    "single-number-row": ("7 2\n+ +\n", 9),
    "mixed-operators": ("1 2 3\n4 5 6\n* + *\n", 29),
    "wide-and-narrow": ("1000 7\n2    3\n*    +\n", 2010),
    "trailing-spaces": (
        "123 328  51 64 \n 45 64  387 23 \n  6 98  215 314\n*   +   *   +  \n",
        4277556,
    ),
    "one-problem-many-rows": ("5\n5\n5\n5\n+\n", 20),
    "adjacent-single-digits": ("1 2 3 4\n+ * + *\n", 10),
}

INVALID_BANK = "12 34\n123 5\n* +\n"


def column_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """Return ``(start, end)`` column ranges of the worksheet's problems.

    A full-space column (spaces in every line, operator line included) is a
    separator; the blocks between separators are the problems. Runs in
    O(lines * width) time.
    """
    width = max(len(line) for line in lines)
    rows = [line.ljust(width) for line in lines]
    separators = {col for col in range(width) if all(row[col] == " " for row in rows)}
    blocks: list[tuple[int, int]] = []
    start: int | None = None
    for col in range(width):
        if col not in separators and start is None:
            start = col
        elif col in separators and start is not None:
            blocks.append((start, col - 1))
            start = None
    if start is not None:
        blocks.append((start, width - 1))
    return blocks


def column_block_parse(text: str) -> tuple[list[list[int]], list[str]]:
    """Parse worksheet ``text`` by character columns into rows and operators.

    Each block between full-space separator columns contributes one token per
    line; the final line holds the operators. A token containing an inner
    space means two numbers share a block (the separator invariant is broken),
    so the input is not a valid worksheet and ValueError is raised.
    """
    lines = text.splitlines()
    if len(lines) < 2:
        raise ValueError(
            "worksheet needs at least one number line and one operator line"
        )
    width = max(len(line) for line in lines)
    rows = [line.ljust(width) for line in lines]
    operators: list[str] = []
    number_rows: list[list[int]] = []
    for index, row in enumerate(rows):
        tokens: list[str] = []
        for start, end in column_blocks(lines):
            token = row[start : end + 1].strip()
            if " " in token:
                raise ValueError(
                    "separator invariant violated: two numbers share a column block"
                )
            tokens.append(token)
        if index == len(rows) - 1:
            operators = tokens
        else:
            number_rows.append([int(token) for token in tokens])
    return number_rows, operators


def grand_total(number_rows: list[list[int]], operators: list[str]) -> int:
    """Return the sum of every problem's folded answer."""
    if not operators:
        return 0
    total = 0
    for problem, operator in enumerate(operators):
        values = [row[problem] for row in number_rows]
        if operator == "+":
            total += sum(values)
            continue
        answer = 1
        for value in values:
            answer *= value
        total += answer
    return total


def cross_check(text: str, expected: int, label: str) -> None:
    """Assert column-block, implementation, and ``expected`` totals agree."""
    column_block = grand_total(*column_block_parse(text))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "worksheet.txt"
        path.write_text(text, encoding="utf-8")
        worksheet = day06.read_worksheet(path)
        impl = day06.part1(worksheet)
    assert column_block == impl == expected, (label, column_block, impl, expected)
    print(f"{label:28s} column-block={column_block} impl={impl}")


def main() -> None:
    sample = (REPO_ROOT / "inputs" / "Day06Test.txt").read_text(encoding="utf-8")
    real = (REPO_ROOT / "inputs" / "Day06.txt").read_text(encoding="utf-8")
    cross_check(sample, 4277556, "sample")
    cross_check(real, 6378679666679, "real")
    for name, (text, expected) in BANKS.items():
        cross_check(text, expected, name)

    try:
        column_block_parse(INVALID_BANK)
    except ValueError:
        print("invalid-bank: ValueError raised as expected")
    else:
        raise AssertionError("invalid bank should raise ValueError")

    print(f"boundaries: {len(BANKS)} banks verified")
    print("column-block == implementation on all checks")


if __name__ == "__main__":
    main()
