from estimate_gap.diff import diff
from estimate_gap.normalize import normalize_estimate


def test_diff_matches_unmatched_and_extra():
    a = normalize_estimate("a", "ref", [{"op": "R&R", "part_area": "hood"}, {"op": "R&I", "part_area": "grille"}])
    b = normalize_estimate("b", "tgt", [{"op": "Repl", "part_area": "Hood"}, {"op": "blend", "part_area": "fender", "side": "L"}])
    m = diff(a, b)
    assert len(m) == 3
    assert m[0].ref_line and m[0].target_line
    assert m[1].ref_line.part_area == "grille" and m[1].target_line is None
    assert m[2].ref_line is None and m[2].target_line.op == "blend"


def test_diff_side_matters():
    a = normalize_estimate("a", "ref", [{"op": "R&R", "part_area": "fender", "side": "L"}])
    b = normalize_estimate("b", "tgt", [{"op": "R&R", "part_area": "fender", "side": "R"}])
    assert all(x.ref_line is None or x.target_line is None for x in diff(a, b))
