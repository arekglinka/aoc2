"""AoC 2019 Day 1: The Tyranny of the Rocket Equation.

Cross-language comparison runner — Python, Rust (maturin), C++ (pybind11).
PureScript SPA also exists at purescript/e2019/ but runs in a browser separately.
"""

from __future__ import annotations

import argparse

from aoc.env import data_ints


def fuel_for_mass(mass: int) -> int:
    return mass // 3 - 2


def total_fuel(mass: int) -> int:
    total = 0
    current = fuel_for_mass(mass)
    while current > 0:
        total += current
        current = fuel_for_mass(current)
    return total


def python_solve(masses: list[int]) -> tuple[int, int]:
    part1 = sum(max(fuel_for_mass(m), 0) for m in masses)
    part2 = sum(total_fuel(m) for m in masses)
    return part1, part2


def _try_extension(name: str, masses: list[int]) -> tuple[int, int] | None:
    """Attempt to call into a compiled extension. Return None if not available."""
    try:
        mod = __import__(name)
    except ImportError:
        return None
    return mod.day1_part1(list(masses)), mod.day1_part2(list(masses))


def run(test: bool = False) -> None:
    masses = data_ints(2019, 1, test=test)
    label = "TEST" if test else "REAL"
    print(f"\n=== AoC 2019 Day 1 ({label}, {len(masses)} masses) ===")

    py_part1, py_part2 = python_solve(masses)
    rust_result = _try_extension("aoc_rust_y2019", masses)
    cpp_result = _try_extension("aoc_cpp_y2019", masses)

    # Verify implementations agree.
    for name, result in [("rust", rust_result), ("cpp", cpp_result)]:
        if result is None:
            print(f"  [warn] {name} extension not built — skipping cross-check")
            continue
        r_p1, r_p2 = result
        assert r_p1 == py_part1, f"{name} part1 mismatch: {r_p1} != {py_part1}"
        assert r_p2 == py_part2, f"{name} part2 mismatch: {r_p2} != {py_part2}"

    # Pretty comparison table.
    rows = [("python", py_part1, py_part2)]
    if rust_result is not None:
        rows.append(("rust", *rust_result))
    if cpp_result is not None:
        rows.append(("cpp", *cpp_result))

    header = f"  {'impl':<10} {'part1':>12} {'part2':>12}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for name, p1, p2 in rows:
        print(f"  {name:<10} {p1:>12} {p2:>12}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="AoC 2019 Day 1 — rocket equation")
    parser.add_argument("--test", action="store_true", help="use test input")
    args = parser.parse_args()
    run(test=args.test)


if __name__ == "__main__":
    main()
