# AGENTS.md — aoc: Rust + C++26 Advent-of-Code program

You are implementing a multi-phase program in this repo. **Read `docs/BLUEPRINT.md` fully before any work** — it contains the complete requirements, phase plan, acceptance gates, deliverable formats, and the language-feature taxonomy. This file is the always-true quick reference.

## Mission

Implement every Advent of Code day 2015–2023 (225 puzzles) as **speed-optimized Rust and C++26 bricks** inside a **Python polylith glue project**, verify cross-language equality, map the language features each solution teaches, fill feature gaps with dedicated teaching solutions, produce a stuck-proof learning path for the owner, and benchmark Rust vs C++ per problem with mechanistic explanations.

## Repo state (as of 2026-10-10, all pushed)

- `ext/aoc_cpp_y2019/` — pybind11 3.1 + scikit-build-core extension, **C++26** (GCC 16), module `aoc_cpp_y2019` (`day1_part1/day1_part2`). This is the canonical CMake/pyproject pattern to replicate.
- `ext/aoc_rust_y2019/` — PyO3 **0.27 + abi3-py313**, module `aoc_rust_y2019`. Canonical Rust pattern.
- `src/aoc/y2019/day1.py` — cross-language **equality runner** (asserts Python == Rust == C++, prints a table). This runner SOFT-SKIPS missing extensions — see gotcha #8.
- `data/e2019/day1.txt`, `data_test/e2019/day1.txt` — current inputs (note: `eYYYY` naming here; the program migrates to `data/<year>/dNN.txt` per BLUEPRINT Phase 0).
- `.devcontainer/devcontainer.json` — lambda_cpp26-dev image, verified working.
- `purescript/` — legacy browser SPA. **Out of scope. Do not touch.**

## Hard toolchain facts (each earned through debugging — do not relearn them)

1. **Devcontainer**: `ghcr.io/arekglinka/lambda_cpp26-dev:latest` (local). Python 3.14.7 at `/var/lang/bin/python3`, GCC 16.2.0 at `/opt/gcc16/bin/g++`, pybind11 3.1.0, clangd. **NO uv, NO cargo/rustc. Entrypoint is NOT bash** — always: `podman run --rm --entrypoint /bin/bash -v "$(pwd)":/work ghcr.io/arekglinka/lambda_cpp26-dev:latest -lc '...'`
2. **Rust in container**: image has no cargo. Build the abi3 wheel on the host (`uv build --wheel <rust-brick> -o dist/wheels`) and pip-install it in-container; `cp313-abi3` wheels are forward-compatible with 3.14.
3. **Container pip bootstrap order**: rust wheel → cpp brick → root `pip install --no-deps -e .` (the uv workspace `[tool.uv.sources]` are invisible to pip). Container venvs live in `/tmp` only — never inside the mounted repo.
4. **scikit-build-core ≥0.8**: the `cmake.minimum-version` / `ninja.minimum-version` keys are **removed** (hard error) — use `cmake.version = ">=3.30"` / `ninja.version = ">=1.11"` (SpecifierSets). CMake 3.28's GNU feature tables cannot record `cxx_std_26`; ≥3.30 is the real floor (pip resolves a modern CMake wheel regardless).
5. **GCC spells the standard `-std=gnu++26`** (GNU extensions default). Flag evidence lives in `build/Release/compile_commands.json`, NOT the `pip install -v` log (ninja is silent there unless `--config-settings=build.verbose=true`).
6. **CMake idioms** (copy from `ext/aoc_cpp_y2019/CMakeLists.txt`): `CMAKE_EXPORT_COMPILE_COMMANDS ON`; `find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)`; no-op `pybind11_strip()` override **before** `pybind11_add_module` (pybind11 3.x strips Release `.so` unconditionally — the override preserves DWARF for LLDB); `-g` on BOTH compile and link options; exactly ONE `target_compile_features(<target> PRIVATE cxx_std_26)`; `build-dir = "build/Release"` for a stable clangd path.
7. **No** static-libstdc++/`--gc-sections` (not Lambda-deployed) and **no** Conan (zero external deps; pybind11 comes from pip).
8. **The equality runner soft-skips** missing extensions with a `[warn]` line — a green exit code proves nothing. Every gate must grep for the language rows AND assert zero `warn` lines.
9. **Host**: GCC 16.1, uv 0.11.6, cargo 1.93.1, podman working. `.python-version` = 3.14; root `requires-python` stays `>=3.13` (abi3 keeps 3.13 hosts valid).
10. Rust APIs are modern `Bound<'_, PyModule>` style under PyO3 0.27 — if upgrading ever needed, the 0.26/0.27 renames are `Python::with_gil`→`Python::attach`, `.downcast()`→`.cast()`.
11. `grep ... | head` pipelines are **vacuous gates** (head exits 0 on empty input). Use `grep -m1` and assert exit codes.

## External references (same machine / same GitHub account)

- Polylith architecture reference: `~/wsp/polylith-template/cookiecutter/{{cookiecutter.project_slug}}/` — component/base/project layout, `interface.py`/`core.py` conventions, and the `polynomial_cpp`/`polynomial_rust` native-brick patterns.
- Canonical C++26 CMake + devcontainer source: `~/wsp/lambda_cpp26/` (read-only reference — **never modify that repo**).
- Puzzle inputs + Python reference solutions: `mp` repo branch `mess-ag` (private; `gh` is authenticated as `arekglinka`). Import commands in BLUEPRINT Phase 0 (verified working).
- Additional local Python references: `~/wsp/aoc/python/` (e2020, e2021 partial) — hash-verify inputs against imported mp data before trusting.

## Verification gates (apply at every phase boundary)

1. Equality runner per implemented day: Python == Rust == C++ rows present, zero `[warn]`, expected values match captured reference answers (see BLUEPRINT §Answers).
2. Host build green (`uv sync` + runner); in-container gate green after structural changes (`podman` one-liner in toolchain fact #1/#3).
3. `git status --porcelain` clean of unintended tracked drift; conventional commits (`feat(aoc_rust): ...` style used in history).

## Scope boundaries

- Do NOT touch: `purescript/`, `~/wsp/lambda_cpp26/`, anything under `~/wsp/polylith-template/`.
- Do NOT push to any remote unless explicitly instructed.
- Do NOT add CI, Makefiles, or wrapper scripts — Python entry points + documented commands only.
- Speed optimization is required but **never at the cost of correctness gates**; algorithmic wins (O-notation) beat micro-optimizations; document non-obvious optimizations in the solution's feature-map entry.
