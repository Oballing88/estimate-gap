"""Line-by-line matching of two estimates on (op, part_area, side)."""

from __future__ import annotations

from .model import Estimate, Match


def diff(ref: Estimate, target: Estimate) -> list[Match]:
    remaining = list(target.lines)
    matches: list[Match] = []
    for line in ref.lines:
        hit = next((t for t in remaining if t.key == line.key), None)
        if hit is not None:
            remaining.remove(hit)
        matches.append(Match(line, hit))
    matches.extend(Match(None, t) for t in remaining)
    return matches
