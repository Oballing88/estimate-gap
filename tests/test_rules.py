import pytest

from estimate_gap.normalize import normalize_estimate as est
from estimate_gap.rules import load_rules, run_rules, validate_rule


def ids(flags):
    return [f.rule_id for f in flags]


def test_missing_operation():
    rule = [{"id": "M", "type": "missing_operation"}]
    a = est(
        "a",
        "r",
        [
            {"op": "R&I", "part_area": "sensor"},
            {"op": "R&I", "part_area": "clip", "included_in_parent": True},
        ],
    )
    flags = run_rules(a, est("b", "t", []), rule)
    assert ids(flags) == ["M"] and flags[0].ref_line == 1
    only_rr = [{"id": "M", "type": "missing_operation", "ops": ["R&R"]}]
    assert run_rules(a, est("b", "t", []), only_rr) == []


def test_hours_delta_threshold():
    rule = [{"id": "H", "type": "hours_delta", "threshold": 0.3}]
    a = est("a", "r", [{"op": "blend", "part_area": "door", "hours": 1.2}])
    assert (
        len(run_rules(a, est("b", "t", [{"op": "blend", "part_area": "door", "hours": 0.8}]), rule))
        == 1
    )
    assert (
        run_rules(a, est("b", "t", [{"op": "blend", "part_area": "door", "hours": 1.0}]), rule)
        == []
    )


def test_refinish_missing():
    rule = [{"id": "R", "type": "refinish_missing", "panels": ["hood"]}]
    bare = est("b", "t", [{"op": "R&R", "part_area": "hood"}])
    assert ids(run_rules(est("a", "r", []), bare, rule)) == ["R"]
    with_line = est(
        "b", "t", [{"op": "R&R", "part_area": "hood"}, {"op": "refinish", "part_area": "hood"}]
    )
    assert run_rules(est("a", "r", []), with_line, rule) == []
    with_hours = est("b", "t", [{"op": "R&R", "part_area": "hood", "refinish_hours": 2}])
    assert run_rules(est("a", "r", []), with_hours, rule) == []
    other_panel = est("b", "t", [{"op": "R&R", "part_area": "mirror"}])
    assert run_rules(est("a", "r", []), other_panel, rule) == []


def test_not_included_corrosion_protection():
    rule = [
        {
            "id": "C",
            "type": "not_included_op",
            "when": {"op": "R&R", "part_area": "quarter panel"},
            "expect": {"desc_contains": "corrosion protection"},
        }
    ]
    t = est("b", "t", [{"op": "R&R", "part_area": "quarter panel", "side": "R"}])
    assert ids(run_rules(est("a", "r", []), t, rule)) == ["C"]
    t2 = est(
        "b",
        "t",
        [
            {"op": "R&R", "part_area": "quarter panel"},
            {"op": "materials", "part_area": "qp", "desc": "Corrosion protection"},
        ],
    )
    assert run_rules(est("a", "r", []), t2, rule) == []


def test_not_included_blend_same_side():
    rule = [
        {
            "id": "B",
            "type": "not_included_op",
            "when": {"op": "refinish", "part_area": "fender"},
            "expect": {"op": "blend", "part_area": "front door", "side": "same"},
        }
    ]
    wrong_side = est(
        "b",
        "t",
        [
            {"op": "refinish", "part_area": "fender", "side": "L"},
            {"op": "blend", "part_area": "front door", "side": "R"},
        ],
    )
    assert ids(run_rules(est("a", "r", []), wrong_side, rule)) == ["B"]
    ok = est(
        "b",
        "t",
        [
            {"op": "refinish", "part_area": "fender", "side": "L"},
            {"op": "blend", "part_area": "front door", "side": "L"},
        ],
    )
    assert run_rules(est("a", "r", []), ok, rule) == []


def test_inactive_rule_and_validation():
    assert (
        run_rules(
            est("a", "r", [{"op": "R&I", "part_area": "x"}]),
            est("b", "t", []),
            [{"id": "M", "type": "missing_operation", "active": False}],
        )
        == []
    )
    with pytest.raises(ValueError):
        validate_rule({"id": "X", "type": "nope"})
    with pytest.raises(ValueError):
        validate_rule({"id": "X", "type": "not_included_op"})


def test_default_rules_load():
    rules = load_rules()
    assert {r["type"] for r in rules} == {
        "missing_operation",
        "hours_delta",
        "refinish_missing",
        "not_included_op",
    }


def test_flag_accept_dismiss():
    f = run_rules(
        est("a", "r", [{"op": "R&I", "part_area": "x"}]),
        est("b", "t", []),
        [{"id": "M", "type": "missing_operation"}],
    )[0]
    assert f.accept().status == "accepted" and f.status == "open"
    assert f.dismiss("already on another line").dismiss_reason
    with pytest.raises(ValueError):
        f.dismiss("")
