"""Deterministic gap-rule engine. Rules are data (JSON); the engine only reads estimates
and returns Flags for an estimator to accept or dismiss. It never edits an estimate."""

from __future__ import annotations

import json
from collections.abc import Callable
from importlib import resources
from pathlib import Path

from .diff import diff
from .model import Estimate, Flag, Line, Match
from .normalize import norm_op, norm_part

RULE_TYPES = ("missing_operation", "hours_delta", "refinish_missing", "not_included_op")


def load_rules(path: str | Path | None = None) -> list[dict]:
    if path is None:
        text = (
            resources.files("estimate_gap").joinpath("rules/default_rules.json").read_text("utf-8")
        )
    else:
        text = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: not valid JSON ({exc.msg}, line {exc.lineno})") from exc
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise ValueError(f"{path}: rules file must be an object with a 'rules' list")
    rules = data["rules"]
    for r in rules:
        validate_rule(r)
    return rules


def validate_rule(rule: dict) -> None:
    if not isinstance(rule, dict):
        raise ValueError(f"rule must be an object: {rule!r}")
    for key in ("id", "type"):
        if key not in rule:
            raise ValueError(f"rule missing '{key}': {rule}")
    if rule["type"] not in RULE_TYPES:
        raise ValueError(f"unknown rule type {rule['type']!r} in {rule['id']}")
    if rule["type"] == "not_included_op" and not ({"when", "expect"} <= rule.keys()):
        raise ValueError(f"{rule['id']}: not_included_op needs 'when' and 'expect'")


def _line_matches(line: Line, cond: dict, anchor: Line | None = None) -> bool:
    if "op" in cond and line.op != norm_op(cond["op"]):
        return False
    if "part_area" in cond and line.part_area != norm_part(cond["part_area"]):
        return False
    if "part_area_in" in cond and line.part_area not in {
        norm_part(p) for p in cond["part_area_in"]
    }:
        return False
    if "desc_contains" in cond and cond["desc_contains"].lower() not in line.desc.lower():
        return False
    if cond.get("side") == "same" and anchor is not None and line.side != anchor.side:
        return False
    return True


def _label(line: Line) -> str:
    """Operation and part, plus the side only when there is one (no '(na)' noise)."""
    side = "" if line.side == "na" else f" ({line.side})"
    return f"{line.op} {line.part_area}{side}"


def _missing_operation(rule, ref, target, matches):
    ops = {norm_op(o) for o in rule.get("ops", [])}
    for m in matches:
        r = m.ref_line
        if r and m.target_line is None and not r.included_in_parent and (not ops or r.op in ops):
            yield Flag(
                rule["id"],
                "missing_in_target",
                f"{_label(r)} is on reference line {r.line_no} but not on the target.",
                ref_line=r.line_no,
                hours_hint=r.hours,
            )


def _hours_delta(rule, ref, target, matches):
    threshold = float(rule.get("threshold", 0.3))
    for m in matches:
        r, t = m.ref_line, m.target_line
        if r and t:
            for attr in ("hours", "refinish_hours"):
                delta = round(getattr(t, attr) - getattr(r, attr), 2)
                if abs(delta) > threshold:
                    yield Flag(
                        rule["id"],
                        "hours_delta",
                        f"{_label(r)} {attr}: reference {getattr(r, attr)} vs target {getattr(t, attr)} ({delta:+}).",
                        ref_line=r.line_no,
                        target_line=t.line_no,
                        hours_hint=max(0.0, -delta),
                    )


def _refinish_missing(rule, ref, target, matches):
    panels = {norm_part(p) for p in rule.get("panels", [])}
    for t in target.lines:
        if t.op != "R&R" or (panels and t.part_area not in panels) or t.refinish_hours > 0:
            continue
        has_refinish = any(
            o.op == "refinish" and o.part_area == t.part_area and o.side == t.side
            for o in target.lines
        )
        if not has_refinish:
            yield Flag(
                rule["id"],
                "refinish_missing",
                f"Replaced panel {t.part_area}{'' if t.side == 'na' else f' ({t.side})'} on target line {t.line_no} has no refinish.",
                target_line=t.line_no,
            )


def _not_included_op(rule, ref, target, matches):
    for t in target.lines:
        if not _line_matches(t, rule["when"]):
            continue
        if not any(_line_matches(o, rule["expect"], anchor=t) for o in target.lines if o is not t):
            exp = rule["expect"]
            label = " ".join(str(exp[k]) for k in ("op", "part_area", "desc_contains") if k in exp)
            yield Flag(
                rule["id"],
                "not_included_op",
                rule.get("message")
                or f"Target line {t.line_no} ({t.op} {t.part_area}) has no '{label}' line.",
                target_line=t.line_no,
                hours_hint=float(rule.get("hours_hint", 0.0)),
            )


_HANDLERS: dict[str, Callable] = {
    "missing_operation": _missing_operation,
    "hours_delta": _hours_delta,
    "refinish_missing": _refinish_missing,
    "not_included_op": _not_included_op,
}


def run_rules(ref: Estimate, target: Estimate, rules: list[dict]) -> list[Flag]:
    matches: list[Match] = diff(ref, target)
    flags: list[Flag] = []
    for rule in rules:
        validate_rule(rule)
        if rule.get("active", True):
            flags.extend(_HANDLERS[rule["type"]](rule, ref, target, matches))
    return flags
