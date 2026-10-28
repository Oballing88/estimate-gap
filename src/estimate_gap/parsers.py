"""Parsers for the simple synthetic JSON and CSV estimate formats (see docs in README).

All problems with an input file are raised as ValueError (or OSError for unreadable files);
the CLI turns them into a one-line message and exit code 2.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .model import Estimate
from .normalize import normalize_estimate


def _build(path, est_id, source, raw_lines, synthetic=True) -> Estimate:
    try:
        est = normalize_estimate(est_id, source, raw_lines, synthetic)
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not est.lines:
        raise ValueError(f"{path}: estimate has no lines")
    return est


def parse_json(path: str | Path) -> Estimate:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: not valid JSON ({exc.msg}, line {exc.lineno})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object with a 'lines' list")
    if "lines" not in data:
        raise ValueError(f"{path}: missing 'lines'")
    if not isinstance(data["lines"], list):
        raise ValueError(f"{path}: 'lines' must be a list")
    return _build(
        path,
        data.get("id", Path(path).stem),
        data.get("source", "other"),
        data["lines"],
        data.get("synthetic", True),
    )


def parse_csv(path: str | Path, est_id: str | None = None, source: str = "other") -> Estimate:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        if "op" not in header:
            raise ValueError(f"{path}: CSV needs a header row with an 'op' column")
        rows = list(reader)
    return _build(path, est_id or Path(path).stem, source, rows)


def load(path: str | Path) -> Estimate:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return parse_json(path)
    if suffix == ".csv":
        return parse_csv(path)
    raise ValueError(f"{path}: unsupported file type {suffix or '(none)'}; use .json or .csv")
