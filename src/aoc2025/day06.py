"""Day06: total the answers of the cephalopod math worksheet.

The worksheet is a list of problems arranged side by side: each problem is a
vertical group of numbers whose operation symbol (``+`` or ``*``) sits below
them on the final line. Problems are separated by full columns of spaces, so
splitting every line on whitespace yields one token per problem per line.

Part 1 reads each problem left to right, applies its operator to fold its
numbers, and sums every problem's answer into the grand total.
"""

import math
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

_ADD = "+"
_MUL = "*"


class Worksheet(NamedTuple):
    """A cephalopod math worksheet.

    ``number_rows`` has one entry per number line, each a list holding one
    value per problem, and ``operators`` holds the operation symbol for each
    problem in left-to-right order. ``len(number_rows)`` is the height of every
    problem and ``len(operators)`` the number of problems.
    """

    number_rows: list[list[int]]
    operators: list[str]


def read_worksheet(filename: str | Path) -> Worksheet:
    """Read a cephalopod math worksheet file into its rows and operators.

    Every line is split on whitespace. The final line's tokens must be ``+``
    or ``*`` operation symbols (one per problem); every earlier line's tokens
    must be nonnegative integers (one value per problem, top to bottom). All
    lines must hold the same number of tokens, and at least one number line and
    one operator must be present. A blank line, a mismatched token count, a
    non-integer value, or an unexpected symbol raises ValueError; a missing
    file raises FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    tokens_per_line: list[list[str]] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                raise ValueError(f"line {line_number} is blank")
            tokens_per_line.append(text.split())
    if len(tokens_per_line) < 2:
        raise ValueError(
            "worksheet needs at least one number line and one operator line"
        )
    widths = {len(tokens) for tokens in tokens_per_line}
    if len(widths) != 1:
        raise ValueError("worksheet lines have mismatched number of problems")
    operators = tokens_per_line[-1]
    if any(op not in (_ADD, _MUL) for op in operators):
        raise ValueError("operator line contains an unexpected symbol")
    number_rows: list[list[int]] = []
    for tokens in tokens_per_line[:-1]:
        for token in tokens:
            if not token.isdigit():
                raise ValueError(f"number line contains a non-integer value {token!r}")
        number_rows.append([int(token) for token in tokens])
    return Worksheet(number_rows, operators)


def _fold(operator: str, values: Sequence[int]) -> int:
    """Fold ``values`` with ``operator``: add from 0 or multiply from 1."""
    if operator == _MUL:
        return math.prod(values)
    return sum(values)


def part1(worksheet: Worksheet) -> int:
    """Return the grand total of every problem's left-to-right answer.

    Each problem folds its vertical group of numbers with its operation symbol
    (add or multiply), and the grand total sums all those answers. Runs in
    O(P * H) time and O(1) extra space for ``P`` problems each ``H`` numbers
    tall.
    """
    if not worksheet.operators:
        return 0
    height = len(worksheet.number_rows)
    total = 0
    for problem in range(len(worksheet.operators)):
        operator = worksheet.operators[problem]
        values = [worksheet.number_rows[row][problem] for row in range(height)]
        total += _fold(operator, values)
    return total
