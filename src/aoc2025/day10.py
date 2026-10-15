"""Day10: press buttons to configure each factory machine's indicator lights.

Each machine line lists an indicator light diagram (``.`` off, ``#`` on), one
or more button wiring schematics, and joltage requirements. Pushing a button
toggles every light it is wired to. Because pushing a button twice cancels
itself out, each button is effectively pushed either zero or one times, and the
fewest total presses that light the diagram exactly is the minimum-weight
solution of a linear system over GF(2). Part 1 sums that minimum across every
machine; the joltage requirements are irrelevant and ignored.
"""

import re
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

_MACHINE_PATTERN = re.compile(
    r"\[(?P<diagram>[.#]+)\]"
    r"(?P<buttons>(?:\s+\(\d+(?:,\d+)*\))+)"
    r"\s+\{(?P<joltages>\d+(?:,\d+)*)\}"
)
_BUTTON_PATTERN = re.compile(r"\((\d+(?:,\d+)*)\)")


class Machine(NamedTuple):
    """One factory machine's diagram, button wiring, and joltage requirements."""

    diagram: str
    buttons: tuple[tuple[int, ...], ...]
    joltages: tuple[int, ...]


def read_machines(filename: str | Path) -> list[Machine]:
    """Read one machine spec per line into a list of machines.

    Each nonblank line holds an indicator light diagram in ``[..]`` (``.`` off,
    ``#`` on), one or more button wiring schematics in ``(...)`` (comma-separated
    light indices), and joltage requirements in ``{...}`` (comma-separated
    non-negative integers). A blank or malformed line, an out-of-range button
    index, or a non-integer value raises ValueError; a missing file raises
    FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    machines: list[Machine] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                raise ValueError(f"line {line_number} is blank")
            match = _MACHINE_PATTERN.fullmatch(text)
            if match is None:
                raise ValueError(f"line {line_number} has invalid machine {text!r}")
            diagram = match.group("diagram")
            num_lights = len(diagram)
            buttons = tuple(
                tuple(int(piece) for piece in button.split(","))
                for button in _BUTTON_PATTERN.findall(match.group("buttons"))
            )
            joltages = tuple(int(piece) for piece in match.group("joltages").split(","))
            if any(
                light < 0 or light >= num_lights
                for button in buttons
                for light in button
            ):
                raise ValueError(f"line {line_number} has an out-of-range button index")
            machines.append(Machine(diagram, buttons, joltages))
    return machines


def _solve_gf2(augmented: list[int], num_vars: int) -> tuple[int, list[int]] | None:
    """Reduce augmented GF(2) rows and return a particular solution and null basis.

    Each row's low ``num_vars`` bits are the coefficients and bit ``num_vars`` is
    the right-hand side. Gaussian elimination produces reduced row echelon form;
    free variables are fixed to zero for the particular solution, and each free
    variable yields one null-space basis vector. Returns ``None`` when the system
    is inconsistent, otherwise ``(particular, null_basis)`` as variable bitmasks.
    """
    rows = augmented[:]
    num_rows = len(rows)
    pivot_rows: dict[int, int] = {}
    rank = 0
    for column in range(num_vars):
        pivot = None
        for row in range(rank, num_rows):
            if (rows[row] >> column) & 1:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(num_rows):
            if row != rank and (rows[row] >> column) & 1:
                rows[row] ^= rows[rank]
        pivot_rows[column] = rank
        rank += 1

    coefficient_mask = (1 << num_vars) - 1
    for row in rows:
        if row & coefficient_mask == 0 and (row >> num_vars) & 1:
            return None

    particular = 0
    for column, row in pivot_rows.items():
        if (rows[row] >> num_vars) & 1:
            particular |= 1 << column

    free_columns = [c for c in range(num_vars) if c not in pivot_rows]
    null_basis: list[int] = []
    for free in free_columns:
        vector = 1 << free
        for column, row in pivot_rows.items():
            if (rows[row] >> free) & 1:
                vector |= 1 << column
        null_basis.append(vector)

    return particular, null_basis


def _min_presses(diagram: str, buttons: Sequence[Sequence[int]]) -> int:
    """Return the fewest presses lighting ``diagram`` using the given ``buttons``.

    Button ``j`` toggles light ``i`` exactly when bit ``i`` of button ``j``'s
    light mask is set, so the desired configuration is a GF(2) linear system
    ``A x = target``. The minimum press count is the minimum popcount over every
    solution, found by enumerating the null space around a particular solution.
    Raises ValueError when no press combination reaches the diagram. Runs in
    O(2^f) time for ``f`` free variables.
    """
    num_lights = len(diagram)
    target = 0
    for light, state in enumerate(diagram):
        if state == "#":
            target |= 1 << light

    num_buttons = len(buttons)
    button_masks = []
    for button in buttons:
        mask = 0
        for light in button:
            mask |= 1 << light
        button_masks.append(mask)

    augmented = []
    for light in range(num_lights):
        coefficients = 0
        for button, mask in enumerate(button_masks):
            if (mask >> light) & 1:
                coefficients |= 1 << button
        augmented.append(coefficients | (((target >> light) & 1) << num_buttons))

    solved = _solve_gf2(augmented, num_buttons)
    if solved is None:
        raise ValueError("machine cannot be configured")
    particular, null_basis = solved

    best = particular.bit_count()
    for choice in range(1, 1 << len(null_basis)):
        candidate = particular
        for index, vector in enumerate(null_basis):
            if (choice >> index) & 1:
                candidate ^= vector
        best = min(best, candidate.bit_count())
    return best


def part1(machines: Sequence[Machine]) -> int:
    """Return the fewest total presses to configure every machine's lights.

    Each button is pushed zero or one times (pushing twice cancels), so each
    machine contributes the minimum-weight GF(2) solution of its toggle system.
    The joltage requirements are ignored. An empty machine list contributes
    zero presses.
    """
    return sum(_min_presses(machine.diagram, machine.buttons) for machine in machines)
