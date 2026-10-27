import pytest

from estimate_gap.normalize import (
    norm_bool,
    norm_hours,
    norm_op,
    norm_part,
    norm_side,
    normalize_line,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Repl", "R&R"),
        ("R/I", "R&I"),
        ("rfn", "refinish"),
        ("Blnd", "blend"),
        ("RPR", "repair"),
        ("???", "other"),
    ],
)
def test_norm_op(raw, expected):
    assert norm_op(raw) == expected


def test_norm_side_part_hours_bool():
    assert norm_side("LT") == "L" and norm_side("right") == "R" and norm_side("") == "na"
    assert norm_part("  Front-Bumper  Cover ") == "front bumper cover"
    assert norm_hours("1.25h") == 1.25 and norm_hours(None) == 0.0
    with pytest.raises(ValueError):
        norm_hours(-1)
    assert norm_bool("yes") and norm_bool(True) and not norm_bool("no")


def test_normalize_line_defaults():
    line = normalize_line({"op": "Repl", "part_area": "Hood"}, default_no=7)
    assert line.line_no == 7 and line.key == ("R&R", "hood", "na") and line.hours == 0.0
