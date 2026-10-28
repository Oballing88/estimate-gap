"""Regression tests: bad input gives a one-line error and exit code 2, never a traceback."""

import pytest

from estimate_gap.cli import main
from estimate_gap.parsers import load, parse_csv

HEADER = "line_no,op,part_area,side,desc,hours,refinish_hours,labor_type,included_in_parent\n"


def run(capsys, *argv):
    code = main(["compare", *map(str, argv)])
    cap = capsys.readouterr()
    return code, cap.out, cap.err


def one_line_error(code, out, err):
    assert code == 2
    assert out == ""
    assert err.startswith("error: ")
    assert err.count("\n") == 1  # exactly one line
    assert "Traceback" not in err


def test_csv_sample_matches_json_sample(samples):
    """Fix for F1: the CSV sample is equivalent to the JSON sample."""
    j, c = load(samples / "estimate_b_synthetic.json"), load(samples / "estimate_b_synthetic.csv")
    assert [ln.key for ln in j.lines] == [ln.key for ln in c.lines]
    assert [(ln.hours, ln.refinish_hours) for ln in j.lines] == [
        (ln.hours, ln.refinish_hours) for ln in c.lines
    ]


def test_csv_and_json_samples_give_same_flags(samples, capsys):
    a = samples / "estimate_a_synthetic.json"
    code_j, out_j, _ = run(capsys, a, samples / "estimate_b_synthetic.json")
    code_c, out_c, _ = run(capsys, a, samples / "estimate_b_synthetic.csv")
    assert code_j == code_c == 0

    def flags(out):
        return [ln.split("  status")[0] for ln in out.splitlines() if ln.startswith("#")]

    assert flags(out_j) == flags(out_c)
    assert out_c.splitlines()[-1] == out_j.splitlines()[-1]  # same summary: 6 flags, same hours


def test_missing_file(samples, capsys):
    res = run(capsys, "nope.json", samples / "estimate_b_synthetic.json")
    one_line_error(*res)
    assert "nope.json" in res[2]


def test_missing_rules_file(samples, capsys):
    a, b = samples / "estimate_a_synthetic.json", samples / "estimate_b_synthetic.json"
    res = run(capsys, a, b, "--rules", "nope.json")
    one_line_error(*res)
    assert "nope.json" in res[2]


def test_unsupported_type(samples, capsys):
    res = run(capsys, samples / "estimate_a_synthetic.json", samples / "README.md")
    one_line_error(*res)
    assert ".md" in res[2]


def test_bad_json(tmp_path, samples, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    res = run(capsys, samples / "estimate_a_synthetic.json", bad)
    one_line_error(*res)
    assert "not valid JSON" in res[2] and "bad.json" in res[2]


@pytest.mark.parametrize(
    "body, text",
    [
        ("[1, 2]", "expected a JSON object"),
        ('{"id": "x"}', "missing 'lines'"),
        ('{"lines": "oops"}', "'lines' must be a list"),
        ('{"lines": [5]}', "line 1"),
        ('{"lines": [{"part_area": "door"}]}', "missing 'op'"),
        ('{"lines": [{"op": "R&R", "hours": "abc"}]}', "line 1"),
        ('{"lines": [{"op": "R&R", "hours": -1}]}', "negative hours"),
    ],
)
def test_json_schema_errors(tmp_path, samples, capsys, body, text):
    f = tmp_path / "t.json"
    f.write_text(body)
    res = run(capsys, samples / "estimate_a_synthetic.json", f)
    one_line_error(*res)
    assert text in res[2]


def test_bad_csv_hours_names_line(tmp_path, samples, capsys):
    f = tmp_path / "t.csv"
    f.write_text(HEADER + "1,R&R,door,L,x,1.0,0,body,\n2,R&R,hood,,x,abc,0,body,\n")
    res = run(capsys, samples / "estimate_a_synthetic.json", f)
    one_line_error(*res)
    assert "line 2" in res[2] and "t.csv" in res[2]


def test_bad_rules_file(tmp_path, samples, capsys):
    a, b = samples / "estimate_a_synthetic.json", samples / "estimate_b_synthetic.json"
    for body in ("{bad", '{"rules": 5}', '{"rules": [{"id": "X", "type": "bogus"}]}'):
        f = tmp_path / "r.json"
        f.write_text(body)
        one_line_error(*run(capsys, a, b, "--rules", f))


@pytest.mark.parametrize(
    "name, body",
    [
        ("empty.json", '{"lines": []}'),
        ("empty.csv", ""),
        ("header_only.csv", HEADER),
        ("no_op_column.csv", "foo,bar\n"),
        ("no_op_column_rows.csv", "foo,bar\n1,2\n"),
    ],
)
def test_empty_or_invalid_target_rejected(tmp_path, samples, capsys, name, body):
    """Fix for F3: an empty or invalid target is an error, not 6 'missing' flags."""
    f = tmp_path / name
    f.write_text(body)
    res = run(capsys, samples / "estimate_a_synthetic.json", f)
    one_line_error(*res)
    assert name in res[2]


def test_empty_reference_rejected(tmp_path, samples, capsys):
    f = tmp_path / "empty.json"
    f.write_text('{"lines": []}')
    one_line_error(*run(capsys, f, samples / "estimate_b_synthetic.json"))


def test_parse_csv_without_rows_raises(tmp_path):
    f = tmp_path / "h.csv"
    f.write_text(HEADER)
    with pytest.raises(ValueError, match="no lines"):
        parse_csv(f)


def test_no_na_in_output(samples, capsys):
    """Fix for F4: a blank side prints no '(na)'; a real side still shows."""
    code, out, _ = run(
        capsys, samples / "estimate_a_synthetic.json", samples / "estimate_b_synthetic.json"
    )
    assert code == 0
    assert "(na)" not in out
    assert "R&I parking sensors is on reference line 2" in out
    assert "(L)" in out
