from __future__ import annotations

import json

from .model import Estimate, Flag


def to_text(ref: Estimate, target: Estimate, flags: list[Flag]) -> str:
    out = [
        f"Gap check: {ref.id} ({ref.source}) vs {target.id} ({target.source})",
        "Read-only: no changes were made to either estimate.",
        "",
    ]
    for i, f in enumerate(flags, 1):
        out.append(f"#{i} [{f.rule_id}] {f.kind}: {f.message}  status={f.status}")
    hours = round(sum(f.hours_hint for f in flags), 2)
    out += ["", f"Summary: {len(flags)} flag(s); about {hours}h to review."]
    return "\n".join(out)


def to_json(ref: Estimate, target: Estimate, flags: list[Flag]) -> str:
    return json.dumps(
        {"reference": ref.id, "target": target.id, "flags": [f.to_dict() for f in flags]}, indent=2
    )
