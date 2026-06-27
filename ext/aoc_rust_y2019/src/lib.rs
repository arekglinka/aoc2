use pyo3::prelude::*;

/// Compute fuel for a single mass: mass / 3 - 2 (integer division).
fn fuel_for_mass(mass: i64) -> i64 {
    mass / 3 - 2
}

/// Iteratively sum fuel for a module, including fuel for the fuel, stopping
/// once the formula returns a non-positive value (which is not added).
fn total_fuel(mass: i64) -> i64 {
    let mut total: i64 = 0;
    let mut current = fuel_for_mass(mass);
    while current > 0 {
        total += current;
        current = fuel_for_mass(current);
    }
    total
}

/// Advent of Code 2019 Day 1, Part 1: sum of `mass // 3 - 2` for each mass.
/// Negative or zero contributions are clamped to 0.
#[pyfunction]
fn day1_part1(masses: Vec<i64>) -> i64 {
    masses
        .iter()
        .map(|&m| {
            let f = fuel_for_mass(m);
            if f > 0 {
                f
            } else {
                0
            }
        })
        .sum()
}

/// Advent of Code 2019 Day 1, Part 2: sum of recursive fuel for each mass.
#[pyfunction]
fn day1_part2(masses: Vec<i64>) -> i64 {
    masses.iter().map(|&m| total_fuel(m)).sum()
}

#[pymodule]
fn aoc_rust_y2019(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(day1_part1, m)?)?;
    m.add_function(wrap_pyfunction!(day1_part2, m)?)?;
    Ok(())
}
