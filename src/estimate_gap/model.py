"""Normalized data model. All objects are frozen: nothing here mutates an estimate."""

from __future__ import annotations

from dataclasses import dataclass, replace

OPS = ("R&I", "R&R", "repair", "refinish", "blend", "sublet", "materials", "other")
SIDES = ("L", "R", "na")


@dataclass(frozen=True)
class Line:
    line_no: int
    op: str
    part_area: str
    desc: str = ""
    side: str = "na"
    hours: float = 0.0
    labor_type: str = "body"
    refinish_hours: float = 0.0
    included_in_parent: bool = False

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.op, self.part_area, self.side)


@dataclass(frozen=True)
class Estimate:
    id: str
    source: str  # e.g. "estimate-a", "estimate-b", "other"
    lines: tuple[Line, ...] = ()
    synthetic: bool = True


@dataclass(frozen=True)
class Match:
    ref_line: Line | None
    target_line: Line | None


@dataclass(frozen=True)
class Flag:
    rule_id: str
    kind: str
    message: str
    ref_line: int | None = None
    target_line: int | None = None
    hours_hint: float = 0.0
    status: str = "open"  # open | accepted | dismissed
    dismiss_reason: str = ""

    def accept(self) -> Flag:
        return replace(self, status="accepted", dismiss_reason="")

    def dismiss(self, reason: str) -> Flag:
        if not reason:
            raise ValueError("a dismiss reason is required")
        return replace(self, status="dismissed", dismiss_reason=reason)

    def to_dict(self) -> dict:
        return dict(self.__dict__)
