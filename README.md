# aoc

Advent of Code solutions in four languages, all sharing the same input data and verified against each other on every run.

Python orchestrates. Rust ships as a Maturin extension. C++ ships as a pybind11 + scikit-build-core extension. PureScript ships as a browser SPA.

## Layout

```
aoc/
├── data/eYYYY/dayN.txt          # shared real puzzle inputs
├── data_test/eYYYY/dayN.txt     # shared sample inputs (one per puzzle)
├── src/aoc/                     # Python package (orchestrator + pure-Python solver)
│   ├── env.py                   # data loader — same path convention as ~/wsp/aoc
│   └── y2019/day1.py            # AoC 2019 Day 1 — runs all four, asserts equality
├── ext/
│   ├── aoc_rust_y2019/          # Rust Maturin extension → `import aoc_rust_y2019`
│   └── aoc_cpp_y2019/           # C++ pybind11 extension → `import aoc_cpp_y2019`
├── purescript/e2019/            # PureScript SPA (browser, fetches data via HTTP)
│   ├── src/Main.purs            # Day 1 solver rendered to <body>
│   └── html/index.html          # SPA host page
├── pyproject.toml               # uv workspace root
└── .python-version              # 3.14 (PyO3 0.27 + abi3-py313)
```

## Setup

Requires: Python 3.14 for development (3.13+ supported — the Rust extension ships as a cp313-abi3 wheel), Rust (cargo), GCC 16+, Node (for PureScript tooling).

```bash
uv sync                          # builds Rust + C++ extensions, installs aoc
cd purescript/e2019 && spago build && spago bundle --bundle-type app --outfile output/app.js
```

## Run

### Python orchestrator (verifies Python = Rust = C++ on every invocation)

```bash
uv run python -m aoc.y2019.day1            # real input
uv run python -m aoc.y2019.day1 --test     # sample input (12, 14, 1969, 100756)
```

Sample output:

```
=== AoC 2019 Day 1 (REAL, 100 masses) ===
  impl              part1        part2
  ------------------------------------
  python          3395944      5091036
  rust            3395944      5091036
  cpp             3395944      5091036
```

If any implementation disagrees, the runner raises `AssertionError` before printing the table.

### PureScript SPA

The SPA needs to fetch puzzle input from `data/e2019/day1.txt` at the repo root, so the HTTP server must serve from the **repo root** (not from `purescript/e2019/`):

```bash
# From repo root
python3 -m http.server 8080
# open http://localhost:8080/purescript/e2019/html/index.html
```

The SPA fetches `../../../data/e2019/day1.txt` (3 levels up from `html/index.html`) and renders Part 1 / Part 2 into the page.

## Adding a new day

1. Drop the input at `data/e{year}/day{N}.txt` (and optionally `data_test/...`).
2. Implement the solver as a pure-Python function in `src/aoc/y{year}/day{N}.py`.
3. If you want native acceleration, add `day{N}_part1` / `day{N}_part2` to both extensions and re-run `uv sync`.
4. Mirror the algorithm in `purescript/e{year}/src/Day{N}.purs` if you want a browser SPA build.

## Toolchain versions this project was built against

- Python 3.14.0 (development; 3.13+ supported via abi3)
- PyO3 0.27 + abi3-py313
- uv 0.11.6
- rustc 1.93.1 / cargo 1.93.1
- GCC 16.1.0
- spago 1.0.4 / purs 0.15.15
- Node 22.22.1
