"""Normalize raw line dicts into model objects."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from .model import Estimate, Line

_OP_ALIASES = {
    "r&i": "R&I",
    "r/i": "R&I",
    "remove and install": "R&I",
    "remove/install": "R&I",
    "r&r": "R&R",
    "r/r": "R&R",
    "replace": "R&R",
    "remove and replace": "R&R",
    "remove/replace": "R&R",
    "repl": "R&R",
    "repair": "repair",
    "rpr": "repair",
    "refinish": "refinish",
    "refn": "refinish",
    "rfn": "refinish",
    "paint": "refinish",
    "blend": "blend",
    "blnd": "blend",
    "sublet": "sublet",
    "subl": "sublet",
    "materials": "materials",
    "mat": "materials",
}
_SIDE_ALIASES = {"l": "L", "lt": "L", "left": "L", "r": "R", "rt": "R", "right": "R"}
_TRUE = {"true", "yes", "y", "1", "incl", "included"}


def norm_op(value: Any) -> str:
    key = re.sub(r"\s+", " ", str(value or "").strip().lower())
    return _OP_ALIASES.get(key, "other")


def norm_side(value: Any) -> str:
    return _SIDE_ALIASES.get(str(value or "").strip().lower(), "na")


def norm_part(value: Any) -> str:
    text = re.sub(r"[^a-z0-9 ]+", " ", str(value or "").lower())
    return re.sub(r"\s+", " ", text).strip()


def norm_hours(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    text = str(value).strip().lower().rstrip("h").strip()
    hours = float(text)
    if hours < 0:
        raise ValueError(f"negative hours: {value!r}")
    return round(hours, 2)


def norm_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in _TRUE


def normalize_line(raw: dict, default_no: int) -> Line:
    return Line(
        line_no=int(raw.get("line_no") or default_no),
        op=norm_op(raw.get("op")),
        part_area=norm_part(raw.get("part_area")),
        desc=str(raw.get("desc") or "").strip(),
        side=norm_side(raw.get("side")),
        hours=norm_hours(raw.get("hours")),
        labor_type=str(raw.get("labor_type") or "body").strip().lower(),
        refinish_hours=norm_hours(raw.get("refinish_hours")),
        included_in_parent=norm_bool(raw.get("included_in_parent")),
    )


def normalize_estimate(
    est_id: str, source: str, raw_lines: Iterable[dict], synthetic: bool = True
) -> Estimate:
    lines = tuple(normalize_line(r, i) for i, r in enumerate(raw_lines, start=1))
    return Estimate(
        id=str(est_id), source=str(source or "other"), lines=lines, synthetic=bool(synthetic)
    )
