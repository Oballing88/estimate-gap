import json

import pytest

from estimate_gap.parsers import load, parse_csv, parse_json


def test_parse_json_sample(samples):
    est = parse_json(samples / "estimate_a_synthetic.json")
    assert est.id == "SYNTH-1042-A" and est.source == "estimate-a" and est.synthetic
    assert len(est.lines) == 6
    assert est.lines[0].op == "R&R"


def test_parse_csv_sample(samples):
    est = parse_csv(samples / "estimate_b_synthetic.csv", source="estimate-b")
    assert len(est.lines) == 3
    assert est.lines[2].side == "L" and est.lines[2].op == "R&R"


def test_load_dispatch_and_errors(tmp_path, samples):
    assert load(samples / "estimate_b_synthetic.json").id == "SYNTH-1042-B"
    with pytest.raises(ValueError):
        load(tmp_path / "x.txt")
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"id": "x"}))
    with pytest.raises(ValueError):
        parse_json(bad)
    badcsv = tmp_path / "bad.csv"
    badcsv.write_text("foo,bar\n1,2\n")
    with pytest.raises(ValueError):
        parse_csv(badcsv)
