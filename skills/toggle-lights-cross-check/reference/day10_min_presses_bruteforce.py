"""Independent Day10 part1 reference: fewest presses by subset enumeration.

The implementation under review models each machine as a GF(2) linear system
``A x = target`` and finds the fewest presses by Gaussian elimination over an
augmented coefficient matrix, reading a particular solution from the pivots,
computing the null-space basis, and searching the null space for the minimum
popcount. This reference shares none of that machinery.

It keeps only the official structure (board diagram plus button wiring, parser
``day10.read_machines``) and, for every machine, enumerates every button mask
``0..2^b-1`` (each button pressed 0 or 1 times; pressing twice cancels), then
*simulates* the toggles on a plain boolean light list
(``lights[light] = not lights[light]``) and keeps the smallest popcount among
masks that end exactly on the target diagram. It never builds a coefficient
row, performs a pivot, computes a rank, derives a particular solution, a null
vector, or a GF(2) linear combination, so agreement with the implementation on
the sample and the real input is genuinely independent acceptance-adjacent
evidence, not a re-run of the same algebra.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day10


def _fewest_presses_bf(diagram: str, buttons: tuple[tuple[int, ...], ...]) -> int:
    """Fewest presses lighting ``diagram`` by enumerating every button subset.

    Each button is pushed 0 or 1 times (pushing twice cancels), so every
    configuration is one subset mask. For each mask we simulate toggles on a
    plain boolean light list and accept the mask whose resulting lights equal
    ``diagram``. Returns the smallest popcount among accepted masks; raises
    ``ValueError`` when no mask reaches the diagram.
    """
    target = tuple(light == "#" for light in diagram)
    num_lights = len(diagram)
    num_buttons = len(buttons)

    best: int | None = None
    for mask in range(1 << num_buttons):
        if best is not None and mask.bit_count() >= best:
            continue
        lights = [False] * num_lights
        for button_index in range(num_buttons):
            if (mask >> button_index) & 1:
                for light in buttons[button_index]:
                    lights[light] = not lights[light]
        if tuple(lights) == target:
            best = mask.bit_count()
    if best is None:
        raise ValueError("machine cannot be configured")
    return best


def _bank_total(bank: list[tuple[str, tuple[tuple[int, ...], ...]]]) -> int:
    """Independent minimum-press total over a synthetic machine bank."""
    return sum(_fewest_presses_bf(diagram, buttons) for diagram, buttons in bank)


def _main() -> int:
    failures: list[str] = []
    inputs = Path(__file__).resolve().parents[3] / "inputs"

    def check(label: str, got: int, expected: int) -> None:
        if got != expected:
            failures.append(f"{label}: got {got}, expected {expected}")
            print(f"  {label}: {got} (expected {expected}) [MISMATCH]")
        else:
            print(f"  {label}: {got} (expected {expected}) [ok]")

    print("Day10 part1 independent brute-force cross-check (toggle-lights)")
    print(
        "Reference: enumerate every button-subset mask, simulate toggles on "
        "a boolean light list"
    )

    print("Official sample (inputs/Day10Test.txt):")
    sample_total = _bank_total(
        [(m.diagram, m.buttons) for m in day10.read_machines(inputs / "Day10Test.txt")]
    )
    check("  sample total", sample_total, 7)

    print("Real input (inputs/Day10.txt):")
    real_total = _bank_total(
        [(m.diagram, m.buttons) for m in day10.read_machines(inputs / "Day10.txt")]
    )
    check("  real total", real_total, 417)

    print("Boundary banks (GF(2) null-space searches get these wrong):")
    boundary = {
        "single light required-on": (("#", ((0,),)), 1),
        "single light required-off": ((".", ((0,),)), 0),
        "redundant button pair (same light wired twice)": (("#", ((0,), (0,))), 1),
        "two independent lights": (("##", ((0,), (1,))), 2),
        "one button wiring both lights": (("##", ((0, 1),)), 1),
        "unconfigurable (required-on light wired to no button)": (
            ("#.", ((1,),)),
            None,
        ),
    }
    for label, (bank, expected) in boundary.items():
        try:
            got = _bank_total([bank])
        except ValueError:
            if expected is None:
                print(f"  {label}: unconfigurable (expected) [ok]")
                continue
            failures.append(f"{label}: raised, expected {expected}")
            print(f"  {label}: raised (expected {expected}) [MISMATCH]")
            continue
        if expected is None:
            failures.append(f"{label}: got {got}, expected unconfigurable")
            print(f"  {label}: {got} (expected unconfigurable) [MISMATCH]")
            continue
        check(f"  {label}", got, expected)

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
