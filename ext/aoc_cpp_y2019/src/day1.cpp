#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstdint>
#include <vector>

namespace py = pybind11;

// AoC 2019 Day 1 — single-step fuel calculation: mass / 3 - 2 (integer division).
static long long fuel_for_mass(long long mass) {
    return mass / 3 - 2;
}

// Part 2 — iterative recursive fuel: apply fuel_for_mass to the mass, then to
// the resulting fuel, accumulating while positive. Stops on <= 0.
static long long total_fuel(long long mass) {
    long long total = 0;
    long long current = fuel_for_mass(mass);
    while (current > 0) {
        total += current;
        current = fuel_for_mass(current);
    }
    return total;
}

// Part 1 — sum fuel_for_mass across all masses, clamping negative per-item to 0.
static long long day1_part1(const std::vector<long long>& masses) {
    long long total = 0;
    for (long long m : masses) {
        long long f = fuel_for_mass(m);
        if (f > 0) total += f;
    }
    return total;
}

// Part 2 — sum total_fuel across all masses.
static long long day1_part2(const std::vector<long long>& masses) {
    long long total = 0;
    for (long long m : masses) total += total_fuel(m);
    return total;
}

PYBIND11_MODULE(aoc_cpp_y2019, m) {
    m.doc() = "AoC 2019 Day 1 — C++ extension built with GCC and pybind11";
    m.def("day1_part1", &day1_part1, "Sum of fuel_for_mass across masses (Part 1)");
    m.def("day1_part2", &day1_part2, "Sum of recursive fuel across masses (Part 2)");
}
