"""Day01: decode the secret entrance password from the safe dial rotations.

The safe dial is labelled ``0`` through ``99`` in order and starts pointing at
``50``. Each line of the puzzle input describes one rotation: a direction letter
``L`` (toward lower numbers) or ``R`` (toward higher numbers) followed by a
distance in clicks. The dial wraps around, so turning left from ``0`` reaches
``99`` and turning right from ``99`` reaches ``0``. Part 1 counts how many
rotations leave the dial pointing exactly at ``0``.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

DIAL_SIZE = 100
START_POSITION = 50


class Rotation(NamedTuple):
    """One dial rotation: a direction (``L`` or ``R``) and a click distance."""

    direction: str
    distance: int


def read_rotations(filename: str | Path) -> list[Rotation]:
    """Read one rotation per line from a UTF-8 input file.

    Each nonblank line is a direction letter ``L`` or ``R`` followed by a
    nonnegative integer distance. Blank lines, a missing direction, or a
    malformed distance raise ValueError; a missing file raises
    FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    rotations: list[Rotation] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                raise ValueError(f"line {line_number} is blank")
            direction, distance_text = text[0], text[1:]
            if direction not in ("L", "R"):
                raise ValueError(
                    f"line {line_number} has invalid direction {direction!r}"
                )
            if not distance_text.isdigit():
                raise ValueError(
                    f"line {line_number} has invalid distance {distance_text!r}"
                )
            rotations.append(Rotation(direction, int(distance_text)))
    return rotations


def apply_rotation(rotation: Rotation, position: int) -> int:
    """Return the dial position after applying ``rotation`` from ``position``.

    Positions wrap modulo ``DIAL_SIZE``: ``L`` decreases the position and ``R``
    increases it. A direction other than ``L`` or ``R`` raises ValueError.
    """
    direction, distance = rotation
    if direction == "L":
        return (position - distance) % DIAL_SIZE
    if direction == "R":
        return (position + distance) % DIAL_SIZE
    raise ValueError(f"invalid direction {direction!r}")


def part1(rotations: Sequence[Rotation]) -> int:
    """Return how many rotations leave the dial pointing at ``0``.

    Starting from ``START_POSITION``, each rotation is applied in order and the
    final position after each rotation is inspected. Runs in O(n) time with
    O(1) extra space for ``n`` rotations.
    """
    position = START_POSITION
    zero_count = 0
    for rotation in rotations:
        position = apply_rotation(rotation, position)
        if position == 0:
            zero_count += 1
    return zero_count
