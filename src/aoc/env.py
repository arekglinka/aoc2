"""Shared data loader — resolves the same path from any language's perspective.

Mirrors the convention from ~/wsp/aoc/python/env.py: inputs live at
``<repo-root>/data/e{year}/day{day}.txt`` (real) and
``<repo-root>/data_test/e{year}/day{day}.txt`` (samples).
"""

from __future__ import annotations

import os
from pathlib import Path

# src/aoc/env.py → repo root is two parents up: env.py → aoc → src → <root>.
ROOT_DIR = Path(__file__).resolve().parents[2]


def data_path(edition_year: int, day: int, *, test: bool = False) -> Path:
    """Return the absolute path to a puzzle input file."""
    subdir = "data_test" if test else "data"
    return ROOT_DIR / subdir / f"e{edition_year}" / f"day{day}.txt"


def data(edition_year: int, day: int, *, test: bool = False) -> str:
    """Read a puzzle input as text."""
    return data_path(edition_year, day, test=test).read_text()


def data_ints(edition_year: int, day: int, *, test: bool = False) -> list[int]:
    """Read a puzzle input as a list of integers (one per line, skipping blanks)."""
    text = data(edition_year, day, test=test)
    return [int(line) for line in text.split() if line.strip()]
