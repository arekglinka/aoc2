# BLUEPRINT — AoC 2015–2023 in Rust + C++26 (polylith, benchmarked, pedagogical)

This is the complete program specification. `AGENTS.md` is the quick-reference companion (toolchain facts, gates). Follow phases in order; every phase ends at a green gate with conventional commits. Nothing gets pushed without the owner's instruction.

## 0. Requirements (owner's verbatim program)

1. Top-level Python polylith glue project.
2. Rust and C++ implementation bricks.
3. All solutions for the data available at `https://github.com/arekglinka/mp/compare/main...mess-ag` (inventory in §2).
4. Every solution implemented in **both** C++ and Rust.
5. Solutions optimized for speed.
6. A map, per solution, of the language features needed to understand it.
7. After all solutions exist: language features **not covered** by any solution get dedicated teaching implementations on problems that suit them — these are also implemented and speed-optimized (within the teaching requirement).
8. A guide for the owner: the optimal learning path minimizing chances of getting stuck.
9. Use the lambda_cpp26 devcontainer and polylith architecture.
10. Benchmarking is the top-level project's responsibility: Rust-vs-C++ comparison per problem, with explanation.

## 1. Guiding rules

- **Correctness gates outrank speed.** Optimize only after the equality gate is green for the day.
- **Algorithmic wins first** (O-notation, data-structure choice), then constant factors (allocation hoisting, branch reduction, vectorization). Record non-obvious optimizations in that solution's feature-map entry.
- **One native crate/ext per language**, year modules inside. Nine per-language crates would multiply build pain for zero benefit.
- The Python side is **glue + oracle + benchmarker** — never the performance surface.

## 2. Inventory (verified 2026-10-10 via `gh api`)

### Puzzle inputs — 225 days
`advent-of-code/data/<year>/d<N>.txt` for years **2015–2023**, 25 days each, on `mp@mess-ag` (private; `gh` authenticated as `arekglinka`).
Test inputs: `data_test/<year>/d1.txt` for 2016–2023 only (8 files).

### Python reference solutions — 63 days
- 2015: **25/25** · 2016: **25/25** · 2017: **13** (d1, d2, d10–d20)
- Location: `advent-of-code/python/advent_of_code/y<year>/d<N>.py`
- Quality: learner-grade, Polish comments, print answers. They are **semantic oracles** (what to compute), never style or performance references.
- Also in the diff: `advent-of-code/python/advent_of_code/input_downloader/run.py` (ignore; inputs already exist) and a README (one line).

### Additional local references (outside the compare)
`~/wsp/aoc/python/` has solutions for e2020 (partial), e2021 (many days), e2025. **Before trusting any**: hash-compare its `data/e<year>/` inputs against the imported mp inputs; only days whose inputs match may use it as an oracle. 2025 is out of program scope.

### No reference anywhere
2017 d3–d9, d21–d25 · all 2018 · 2019 d2–d25 · all 2022 · all 2023.
For these, derive the spec from the public problem statements (adventofcode.com/<year>/day/<N> — statements are public; inputs are already local). See §5 Answers for verification tiers.

### Import procedure (commands verified)
```bash
# from repo root ~/wsp2/aoc
mkdir -p /tmp/mp_import && gh api repos/arekglinka/mp/tarball/mess-ag > /tmp/mp_import/mp.tgz
tar -xzf /tmp/mp_import/mp.tgz -C /tmp/mp_import   # creates <sha>/advent-of-code/...
MP=/tmp/mp_import/*/advent-of-code
# 1) inputs -> new layout, names normalized to zero-padded d01..d25
for y in 2015 2016 2017 2018 2019 2020 2021 2022 2023; do
  mkdir -p data/$y data_test/$y
  for f in "$MP"/data/$y/d*.txt; do
    n=$(basename "$f" .txt); n=${n#d}; cp "$f" "$(printf 'data/%s/d%02d.txt' "$y" "$((10#$n))")"; done; done
# data_test: only d1 exists for 2016-2023; copy the same way into data_test/
# rename the legacy data/e2019/day1.txt -> data/2019/d01.txt and data_test/e2019/day1.txt -> data_test/2019/d01.txt, then delete the old e-prefixed dirs
# 2) python references (read-only oracle corpus)
mkdir -p reference/python
cp -r "$MP"/python/advent_of_code/y2* reference/python/
# 3) capture oracle answers NOW (see §5)
```
Keep `reference/` untracked-by-benchmark, committed as data (it is small; it documents provenance).

## 3. Target architecture (polylith)

Conventions follow `~/wsp/polylith-template/cookiecutter/{{cookiecutter.project_slug}}/` (layout, `interface.py`/`core.py` split, native-brick pattern `polynomial_cpp`/`polynomial_rust`). Namespace: `aoc`.

```text
~/wsp2/aoc/
├── pyproject.toml                 # uv workspace root + hatchling; members = bricks; glue package
├── components/aoc/
│   ├── aoc_rust/                  # RUST BRICK (maturin + PyO3 0.27 + abi3-py313)
│   │   ├── pyproject.toml         # maturin; workspace member
│   │   ├── Cargo.toml
│   │   └── src/{lib.rs, y2015/{d01.rs,…}, y2016/…, …}   # one module per day
│   ├── aoc_cpp/                   # C++ BRICK (scikit-build-core + pybind11 3.1, C++26)
│   │   ├── pyproject.toml         # cmake.version >=3.30, build-dir build/Release
│   │   ├── CMakeLists.txt         # idioms per AGENTS.md #6
│   │   └── src/{bindings.cpp, y2015/d01.cpp, …}
│   └── benchmarks/                # pure-Python brick: harness + report generation (§9)
├── bases/aoc/cli/                 # runner base: python -m aoc.cli <year> <day> [--test|--bench]
├── src/aoc/                       # top-level glue: env/data loading, answer registry, equality runner
├── data/<year>/dNN.txt            # real inputs        (225)
├── data_test/<year>/dNN.txt       # sample inputs      (where they exist)
├── answers/y<year>/dNN.json       # captured oracle answers (§5)
├── reference/python/y<year>/…     # imported Python oracles (63)
├── docs/
│   ├── BLUEPRINT.md               # this file
│   ├── FEATURES.md                # master feature×problem matrix + coverage + gaps (§7)
│   ├── features/y<year>/dNN.md    # per-solution feature map (§7)
│   ├── LEARNING_PATH.md           # owner's guide (§8)
│   └── BENCHMARKS.md              # generated tables + hand-written analysis (§9)
└── .devcontainer/devcontainer.json
```

**Native API contract** (both bricks, identical shape): per day, expose typed functions
`y<year>_d<NN>_p<p>(input: &str) -> Answer` where `Answer` is a string-serializable enum (i64/u64/String). Python passes the **raw input text**; parsing happens inside the native solution (it is part of the speed story, §9). Keep the ABI dumb: a `String` return is enough for equality, and benchmarks time the same function.

- Migration of the existing `ext/aoc_*_y2019` into `components/aoc/{aoc_rust,aoc_cpp}` (keeping `y2019::d01` semantics: test 34241/51316, real 3395944/5091036) is **Phase 0's proof** that the pattern works end-to-end.

## 4. Phases

| Phase | Content | Exit gate |
|---|---|---|
| **0** | Import data+references (§2), capture answers (§5), restructure to §3 tree, migrate 2019 d1 into bricks, `python -m aoc.cli 2019 1` green | host runner equality (rows, no warn); in-container gate (AGENTS.md #1–3) |
| **1–9** | One phase per year, 2015→2023. Per day: implement C++ + Rust + glue registration + `docs/features/` entry + answers check. Reference days use Tier A; the rest Tier B (§5) | per-day equality gate; year-end: full-year runner sweep + suite green |
| **10** | Build `docs/FEATURES.md` matrix; compute uncovered taxonomy IDs (§6) | matrix complete; gap list frozen |
| **11** | Gap-teaching solutions (§7): pick suitable problems per gap feature, implement in BOTH languages, optimized within teaching constraint | equality gates green; every gap feature covered by ≥1 teaching solution with feature-map entry |
| **12** | Generate `docs/LEARNING_PATH.md` per §8 algorithm | path validates: prereq-closed, ≤3 new features/step, every taxonomy ID introduced somewhere |
| **13** | Full benchmark run + `docs/BENCHMARKS.md` (§9) | every problem has Rust+C++ timings + explanation; harness re-runnable |

Commit style: `feat(aoc_cpp): y2015 d01-05`, `feat(aoc_rust): y2015 d01-05`, `docs(features): y2015 wave` — atomic, per concern.

## 5. Answers & verification tiers

- **Phase 0 capture**: run each of the 63 reference solutions once against its own input; record printed Part1/Part2 into `answers/y<year>/dNN.json` (schema: `{"p1": "...", "p2": "...", "tier": "A", "source": "reference/python"}`). Learner code is buggy sometimes: if any captured answer later disagrees with BOTH native implementations, investigate; if the Python is wrong, fix the answer file, mark `"override": true` with a one-line justification in the JSON.
- **Tier A** (reference exists — 63 days): native outputs must equal the captured answers, and Rust must equal C++.
- **Tier B** (no reference — 162 days): Rust must equal C++; validate against `data_test` samples where they exist (only d1s); sanity-check magnitude and part1→part2 consistency; record `"tier": "B"` in answers. The owner spot-checks Tier B answers (they solved these before); keep `docs/FEATURES.md` footer listing Tier B days for review.
- Equality runner output contract: rows `python|rust|cpp` + values; assert zero `[warn]` (AGENTS.md #8).

## 6. Language-feature taxonomy (map legend)

Stable IDs; per-solution maps cite these. Extend only with a FEATURES.md changelog note.

### C++26 (`cpp-*`)
01 RAII · 02 move semantics/rvalue refs · 03 smart pointers (`unique/shared`) · 04 `const` correctness · 05 references vs pointers · 06 lambdas (captures, generic) · 07 `auto` + structured bindings · 08 `constexpr`/`consteval`/`constinit` · 09 templates (function/class, specialization) · 10 concepts + `requires` · 11 ranges (views/adaptors: `filter/transform/zip/enumerate/chunk/slide`) · 12 iterators/categories · 13 `std::optional/variant/any` · 14 `std::expected` (error handling without exceptions) · 15 exceptions · 16 `std::span`/`string_view` (non-owning) · 17 `std::format`/`std::print` · 18 operator overloading · 19 three-way comparison `<=>` · 20 designated initializers · 21 ADL + namespaces · 22 variadic templates/fold expressions · 23 coroutines (`co_await/co_yield`, `std::generator`) · 24 atomics/`std::thread`/jthread · 25 parallel algorithms (`std::execution`) · 26 `std::simd` (explicit vectorization) · 27 unordered/ordered containers + hashing · 28 algorithms library mastery (`sort/lower_bound/partition/accumulate…`) · 29 charconv/from_chars (fast parsing) · 30 CRTP/static polymorphism · 31 SFINAE/`if constexpr` compile-time branching · 32 modules (C++20/26 named modules) · 33 reflection (C++26, GCC-16 partial — mark experimental) · 34 `flat_map`/`mdspan` (C++23 containers) · 35 allocators/PMR

### Rust (`rs-*`)
01 ownership · 02 move vs `Copy` · 03 borrowing/shared-vs-exclusive · 04 lifetimes (incl. in structs) · 05 slices/`&str` vs `String` · 06 `Vec`/`HashMap`/`BTreeMap` · 07 enums + exhaustive `match` · 08 pattern matching (guards, bindings, destructuring) · 09 `Option`/`Result` + `?` · 10 error design (`thiserror`/`anyhow` or manual) · 11 traits (+ `derive`, orphan rule) · 12 generics + monomorphization vs trait objects (`dyn`) · 13 iterators + adaptors (`map/filter/fold/scan/windows`) · 14 closures (`Fn/FnMut/FnOnce`) · 15 lifetimes of closures/Higher-ranked trait bounds · 16 modules/visibility/paths · 17 declarative macros (`macro_rules!`) · 18 `Box`/`Rc`/`Arc` + interior mutability (`Cell/RefCell/Mutex`) · 19 `const fn` + statics · 20 zero-cost abstractions (inline, branch hints) · 21 `unsafe` + raw pointers (when justified) · 22 explicit SIMD (`std::arch`) / autovectorization · 23 `rayon` data parallelism · 24 `memchr`/byte-oriented parsing crates (or core-only equivalents) · 25 type inference/turbofish · 26 newtype pattern + conversions (`From/TryFrom`) · 27 smart iterator chaining vs index loops (benchmark trade-off) · 28 `String` UTF-8 invariants vs bytes (`as_bytes`) · 29 stack vs heap layout control (`#[repr]`, arrays) · 30 procedural macros (read-only awareness)

## 7. Feature maps (req 6) and gap teaching (req 7)

**Per solution** — `docs/features/y<year>/dNN.md`:
```markdown
# y2015 d01
## Rust: rs-01, rs-05, rs-07 · ## C++: cpp-01, cpp-16, cpp-29
- Why: parses with from_chars (cpp-29) over string_view (cpp-16)…
- Optimizations: single-pass accumulate, no allocations in loop (…)
- Teaching notes: what a learner must already know (links to taxonomy IDs)
```

**Master** — `docs/FEATURES.md`: sparse matrix (rows = 225 problems + teaching solutions; columns = taxonomy IDs), coverage counters per ID, and the **gap list** (IDs with zero coverage) computed in Phase 10.

**Gap teaching (Phase 11)**: for each uncovered ID, pick a problem whose structure teaches it naturally, e.g.: `std::expected`/`rs-10` ↔ parsing-heavy days; coroutines `cpp-23` ↔ sequence/generator days (e.g. 2015 d10 look-and-say iterations); `cpp-25`/`rs-23` parallelism ↔ grid-automaton days (2020 d11 seating); `cpp-26`/`rs-22` SIMD ↔ 2017 d16 dance, 2021 d6 lanternfish sliding window; `cpp-32` modules ↔ any mid-size multi-file day; `rs-17` macros ↔ repetitive intcode-style dispatch (2019). Implement in **both** languages (the counterpart feature must also be exercised), optimize for speed within the teaching constraint (the feature must remain visibly used, not optimized away), and mark the solution `teaching: <IDs>` in its feature map.

## 8. Learning path (req 8) — generation algorithm

Produce `docs/LEARNING_PATH.md` mechanically, then hand-polish prose:

1. Build the **prerequisite graph** over taxonomy IDs (e.g. `rs-03 → rs-04 → rs-15`; `cpp-09 → cpp-10`; `cpp-02 → cpp-03`; `cpp-11 → cpp-12`).
2. For each problem, `new(p) = features(p) − already_covered`.
3. Greedy walk: start from the problem with the fewest, most-basic features; repeatedly pick the next problem minimizing `|new(p)| ≥ 1`, tie-break by (a) fewer unmet prereqs, (b) year/day order. **Cap: ≤3 new features per step** — this is the anti-stuck guarantee.
4. If no problem introduces a needed feature (gap case), insert its Phase-11 teaching solution at the earliest point all prereqs are met.
5. Each step renders: problem → features introduced → prereqs assumed → 2–4 line "what you'll struggle with" (real compiler-error families: borrow-checker E0502, lifetime E0106, concept diagnostics, template errors) → checkpoint exercise (modify the solution: e.g. "make it handle the sample input").
6. Validate: prereq-closed (every step's prereqs introduced earlier), full taxonomy coverage, no step >3 new features. Emit validation summary at the doc footer.

## 9. Benchmarking (req 10) — owned by the top-level project

**Harness** (`components/aoc/benchmarks`, invoked `python -m aoc.cli <year> <day> --bench` or `--bench-all`):
- Loads input text once; passes the **same string** to both bricks (parse included — it is part of each solution).
- Warmup 3 runs, then ≥10 timed runs; report **median, min, p95** in µs (`time.perf_counter_ns`); GC disabled around timed regions.
- Optional second metric `solve-only` if a day exposes pre-parsed entry points — never required.
- Emits JSON rows; `BENCHMARKS.md` tables are generated from them (regenerable; hand-written analysis lives in separate `### Analysis — yYYYY dNN` blocks so regeneration never destroys prose).

**Per-problem explanation requirements** (the "why" is the deliverable, not just the ratio): each analysis block must address, where relevant:
- allocation profile (count/size per run, Rust `Vec` growth vs C++ `reserve`),
- bounds checking (Rust checked indexing vs C++ unchecked `[]`/`.data()`),
- parsing strategy (`from_chars` vs byte iteration; UTF-8 validation costs),
- vectorization reality (check with `-fopt-info-vec` / `cargo asm` spot checks — cite, don't guess),
- branch/lookup structure (tables vs `match`/`switch` codegen),
- container choice (open-addressing `HashMap` vs `std::unordered_map` bucket walks; sorted `BTreeMap` vs `flat_map`),
- and an honest variance note (same machine, same build flags; report if the gap is within noise).

**Build flags locked for benchmarks**: Rust `--release` (default profile); C++ via the brick's Release (`-O3 -g` per current CMakeLists; `-g` does not slow codegen).

## 10. Definition of Done

- [ ] 225 days × 2 languages, equality gates green (Tier A: match captured answers; Tier B: rust==cpp + data_test where present)
- [ ] `docs/FEATURES.md` matrix complete; every taxonomy ID covered by ≥1 solution or teaching solution
- [ ] Gap-teaching solutions implemented + optimized + mapped
- [ ] `docs/LEARNING_PATH.md` validates (§8.6)
- [ ] `docs/BENCHMARKS.md`: all problems benchmarked with per-problem mechanistic analysis
- [ ] In-container verification passes for the final structure (AGENTS.md bootstrap order)
- [ ] Conventional commits throughout; nothing pushed without instruction

## 11. Known traps (from prior sessions in this repo)

- `grep | head` vacuous gates (AGENTS.md #11); runner `[warn]` soft-skip (#8).
- Container has no cargo — host-build abi3 wheels (#2); venvs in `/tmp` (#3).
- `cmake.version` not `cmake.minimum-version` (#4); `gnu++26` spelling + `compile_commands.json` as flag evidence (#5).
- pip cannot resolve uv workspace sources — bootstrap order (#3).
- Python reference solutions print answers — capture them ONCE in Phase 0 into `answers/`; do not re-run learner code in later gates (regression anchors come from `answers/`, keeping gates deterministic).
- `data/e2019/day1.txt` legacy naming vs new `data/2019/d01.txt` — migrate in Phase 0 and update `src/aoc` loader paths in the same commit.
