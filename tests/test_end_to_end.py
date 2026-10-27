import json

from estimate_gap.cli import main
from estimate_gap.parsers import load
from estimate_gap.rules import load_rules, run_rules


def test_sample_run_flags(samples):
    a = load(samples / "estimate_a_synthetic.json")
    b = load(samples / "estimate_b_synthetic.json")
    before = (a, b, (samples / "estimate_b_synthetic.json").read_bytes())
    flags = run_rules(a, b, load_rules())
    got = sorted((f.rule_id, f.kind) for f in flags)
    assert got == sorted(
        [
            ("EX-001", "missing_in_target"),  # parking sensors R&I
            ("EX-002", "hours_delta"),  # LT fender refinish hours
            ("EX-002", "hours_delta"),  # LT door blend 1.2 vs 0.8
            ("EX-003", "refinish_missing"),  # LT fender replaced, no refinish
            ("EX-004", "not_included_op"),  # quarter panel, no corrosion protection
            ("EX-006", "not_included_op"),  # bumper refinish, no adhesion promoter
        ]
    )
    # read-only: inputs unchanged
    assert before == (a, b, (samples / "estimate_b_synthetic.json").read_bytes())


def test_cli_text_and_json(samples, capsys):
    args = [
        "compare",
        str(samples / "estimate_a_synthetic.json"),
        str(samples / "estimate_b_synthetic.json"),
    ]
    assert main(args) == 0
    assert "6 flag(s)" in capsys.readouterr().out
    assert main(args + ["--format", "json"]) == 0
    assert len(json.loads(capsys.readouterr().out)["flags"]) == 6
