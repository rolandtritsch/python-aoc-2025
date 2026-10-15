"""Day10: press buttons to configure each factory machine.

Each machine line lists an indicator light diagram (``.`` off, ``#`` on), one
or more button wiring schematics, and joltage requirements. Part 1 toggles
lights: pushing a button twice cancels, so each button is effectively pushed
zero or one times, and the fewest total presses that light the diagram exactly
is the minimum-weight solution of a linear system over GF(2). Part 2 flips the
lever so every press *increments* the counters named by the button wiring; it
sums the fewest non-negative integer presses that reach each machine's exact
joltage targets.
"""

import re
from collections.abc import Sequence
from fractions import Fraction
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


def _simplex_maximize(
    columns: Sequence[Sequence[int]], costs: Sequence[int], num_rows: int
) -> tuple[Fraction, list[Fraction]] | None:
    """Maximize ``sum(costs[c] * z[c])`` with an exact tableau simplex.

    ``columns[c]`` holds one signed coefficient per row (each in ``{-1, 0, 1}``);
    every row is constrained to ``<= 1`` and every variable ``z[c] >= 0``. This
    is the dual of the joltage linear program, so the returned shadow price of
    row ``r``'s slack is the primal press count ``x[r]``. Returns ``None`` when
    the objective is unbounded, meaning the primal is infeasible.
    """
    num_columns = len(columns)
    width = num_columns + num_rows
    tableau: list[list[Fraction]] = []
    for row in range(num_rows):
        row_values = [Fraction(0)] * (width + 1)
        for column, column_values in enumerate(columns):
            coefficient = column_values[row]
            if coefficient:
                row_values[column] = Fraction(coefficient)
        row_values[num_columns + row] = Fraction(1)
        row_values[width] = Fraction(1)
        tableau.append(row_values)

    objective = [Fraction(0)] * (width + 1)
    for column, cost in enumerate(costs):
        objective[column] = Fraction(cost)

    basis = [num_columns + row for row in range(num_rows)]
    basic = [False] * width
    for variable in basis:
        basic[variable] = True

    while True:
        entering = -1
        for column in range(width):
            if not basic[column] and objective[column] > 0:
                entering = column
                break
        if entering == -1:
            break
        pivot_row = -1
        best_ratio = None
        for row in range(num_rows):
            coefficient = tableau[row][entering]
            if coefficient > 0:
                ratio = tableau[row][width] / coefficient
                if best_ratio is None or ratio < best_ratio:
                    best_ratio = ratio
                    pivot_row = row
        if pivot_row == -1:
            return None
        pivot_row_values = tableau[pivot_row]
        pivot = pivot_row_values[entering]
        for column in range(width + 1):
            pivot_row_values[column] /= pivot
        for row in range(num_rows):
            if row == pivot_row:
                continue
            factor = tableau[row][entering]
            if factor:
                for column in range(width + 1):
                    tableau[row][column] -= factor * pivot_row_values[column]
        factor = objective[entering]
        if factor:
            for column in range(width + 1):
                objective[column] -= factor * pivot_row_values[column]
        basic[basis[pivot_row]] = False
        basic[entering] = True
        basis[pivot_row] = entering

    value = -objective[width]
    shadow = [-objective[num_columns + row] for row in range(num_rows)]
    return value, shadow


def _min_joltage_presses(
    buttons: Sequence[Sequence[int]], joltages: Sequence[int]
) -> int:
    """Return the fewest presses reaching every joltage target exactly.

    Pressing button ``j`` increments counter ``i`` by one for each ``i`` in
    ``buttons[j]``, so the counters satisfy ``A x = joltages`` for the 0/1
    incidence matrix ``A`` and non-negative integer press counts ``x``. The
    minimum total press count is the minimum-weight such ``x``. It is found by
    branch and bound using the exact LP relaxation ``min sum(x)`` subject to
    ``A x = joltages`` and ``x >= 0``: a fractional press count is fixed to its
    floor or ceiling. Raises ValueError when no press counts reach the targets.
    """
    num_counters = len(joltages)
    num_buttons = len(buttons)
    masks = [0] * num_buttons
    for button_index, button in enumerate(buttons):
        for counter in button:
            masks[button_index] |= 1 << counter

    cover = [0] * num_counters
    for counter in range(num_counters):
        for button_index in range(num_buttons):
            if masks[button_index] >> counter & 1:
                cover[counter] |= 1 << button_index

    def relax(
        targets: Sequence[int], upper: Sequence[int | None]
    ) -> tuple[Fraction, list[Fraction]] | None:
        columns: list[list[int]] = []
        costs: list[int] = []
        for counter in range(num_counters):
            column = [0] * num_buttons
            for button_index in range(num_buttons):
                if cover[counter] >> button_index & 1:
                    column[button_index] = 1
            columns.append(column)
            costs.append(targets[counter])
        for counter in range(num_counters):
            column = [0] * num_buttons
            for button_index in range(num_buttons):
                if cover[counter] >> button_index & 1:
                    column[button_index] = -1
            columns.append(column)
            costs.append(-targets[counter])
        for button_index in range(num_buttons):
            if upper[button_index] is not None:
                column = [0] * num_buttons
                column[button_index] = -1
                columns.append(column)
                costs.append(-upper[button_index])
        return _simplex_maximize(columns, costs, num_buttons)

    best: int | None = None

    def search(targets: list[int], upper: list[int | None], cost: int) -> None:
        nonlocal best
        result = relax(targets, upper)
        if result is None:
            return
        value, presses = result
        if best is not None and cost + value >= best:
            return
        if all(press.denominator == 1 for press in presses):
            total = cost + sum(int(press) for press in presses)
            if best is None or total < best:
                best = total
            return
        chosen = max(
            (
                button_index
                for button_index in range(num_buttons)
                if presses[button_index].denominator != 1
            ),
            key=lambda button_index: presses[button_index] - int(presses[button_index]),
        )
        floor = presses[chosen].numerator // presses[chosen].denominator
        if floor >= 0 and (upper[chosen] is None or floor < upper[chosen]):
            next_upper = list(upper)
            next_upper[chosen] = floor
            search(targets, next_upper, cost)
        ceiling = floor + 1
        next_targets = list(targets)
        feasible = True
        for counter in range(num_counters):
            if masks[chosen] >> counter & 1:
                next_targets[counter] -= ceiling
                if next_targets[counter] < 0:
                    feasible = False
        if feasible:
            next_upper = list(upper)
            if upper[chosen] is not None:
                next_upper[chosen] = upper[chosen] - ceiling
                if next_upper[chosen] < 0:
                    feasible = False
            if feasible:
                search(next_targets, next_upper, cost + ceiling)

    search(list(joltages), [None] * num_buttons, 0)
    if best is None:
        raise ValueError("machine cannot be configured")
    return best


def part2(machines: Sequence[Machine]) -> int:
    """Return the fewest total presses to reach every machine's joltage levels.

    Each machine's counters start at zero and every press increments the listed
    counters by one, so each machine contributes the minimum non-negative
    integer solution of ``A x = joltages``. The indicator light diagrams are
    ignored. An empty machine list contributes zero presses.
    """
    return sum(
        _min_joltage_presses(machine.buttons, machine.joltages) for machine in machines
    )
