"""Parsers for the simple synthetic JSON and CSV estimate formats (see docs in README)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .model import Estimate
from .normalize import normalize_estimate


def parse_json(path: str | Path) -> Estimate:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "lines" not in data:
        raise ValueError(f"{path}: missing 'lines'")
    return normalize_estimate(
        data.get("id", Path(path).stem),
        data.get("source", "other"),
        data["lines"],
        data.get("synthetic", True),
    )


def parse_csv(path: str | Path, est_id: str | None = None, source: str = "other") -> Estimate:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if rows and "op" not in rows[0]:
        raise ValueError(f"{path}: CSV needs an 'op' column")
    return normalize_estimate(est_id or Path(path).stem, source, rows)


def load(path: str | Path) -> Estimate:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return parse_json(path)
    if suffix == ".csv":
        return parse_csv(path)
    raise ValueError(f"unsupported file type: {suffix}")
