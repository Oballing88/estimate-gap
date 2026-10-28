# estimate-gap

A small, read-only tool that compares two collision repair estimates for the same job line by line, then lists possible gaps for an estimator to accept or dismiss.

Status: early (v0.1.0). Inputs are a simple JSON/CSV format. Real export formats are not supported yet.

## For collision estimators
**What it does.** You give it two estimates for the same job (for example, your estimate and a second one you want to check against). It compares them line by line and flags things worth a second look:
- an operation that is on one estimate but not the other,
- labor hours that differ by more than a set amount (0.3 h by default),
- a replaced panel with no refinish on it,
- companion operations that are commonly forgotten (the built-in examples include corrosion protection and adhesion promoter).

Each flag is a suggestion. You accept it or dismiss it. The tool decides nothing.

**What it doesn't do.**
- It does not change anything in your estimating system. It only reads files and prints a report.
- It is not affiliated with or endorsed by any estimating or data vendor.
- It ships with synthetic sample estimates only. There are no real jobs, customers or vendor data in this repo.
- It is early (v0.1.0). It reads a simple JSON/CSV format, not your system's native export, and the example rules are generic starting points. Check them against your own references.

**Try it in 2 minutes.** You need Python 3.10 or newer.
```bash
git clone https://github.com/Oballing88/estimate-gap && cd estimate-gap
python -m venv .venv && . .venv/bin/activate
pip install -e .
estimate-gap compare samples/estimate_a_synthetic.json samples/estimate_b_synthetic.json
```
You should see 6 flags on the sample pair.

**Suggest a rule.** Tell us what your estimators catch by hand, in your own words. Use the [rule proposal form](https://github.com/Oballing88/estimate-gap/issues/new?template=rule_proposal.md). Please don't paste labor times, procedure text or op codes from any vendor, and don't post real estimates or customer details.

## What it is
- A parser for a simple JSON or CSV estimate format, plus a normalizer for operation names (e.g. `Repl` → `R&R`), sides, part names and hours.
- A differ that matches lines on operation + part + side.
- A deterministic rule engine. The rules are data (JSON), and each hit becomes a flag with status `open`, `accepted` or `dismissed`.
- A CLI and a test suite.

## What it isn't
- It does not change any estimate or write to CCC ONE, Mitchell or any other system. It only reads files and prints a report.
- It is not a source of labor times or procedures. It ships no MOTOR, CCC or Mitchell data or text. The example rules are generic and written from scratch, so check them against your own references before relying on them.
- It is not affiliated with, endorsed by or sponsored by CCC Intelligent Solutions, Mitchell International or MOTOR Information Systems. Those names are trademarks of their owners. The sample files are named "estimate A" and "estimate B" and contain no vendor names.
- It does not give repair, legal or insurance advice.

## Install
Requires Python 3.10 or newer. There are no runtime dependencies.
```bash
git clone <this repo> && cd estimate-gap
python -m venv .venv && . .venv/bin/activate
pip install -e '.[test]'
pytest
```

## Quickstart
```bash
estimate-gap compare samples/estimate_a_synthetic.json samples/estimate_b_synthetic.json
estimate-gap compare a.json b.json --format json
estimate-gap compare a.json b.csv --rules my_rules.json
```
`a` is the reference estimate and `b` is the target being checked. With the synthetic samples the tool reports 6 flags: a missing R&I, two hour differences, a replaced panel with no refinish, a missing corrosion protection line and a missing adhesion promoter line.

## Input format
JSON: `{"id": "...", "source": "...", "synthetic": true, "lines": [ ... ]}`. CSV uses one row per line with the same column names.

| field | meaning |
|---|---|
| `line_no` | line number (defaults to its position) |
| `op` | `R&I`, `R&R`, `repair`, `refinish`, `blend`, `sublet`, `materials` (common abbreviations are normalized) |
| `part_area` | part or area, e.g. `front door` |
| `side` | `L`, `R` or blank |
| `desc` | free text |
| `hours`, `refinish_hours` | numbers |
| `labor_type` | e.g. `body`, `refinish` |
| `included_in_parent` | true if the op is already included in another line |

## Rule format
Rules live in a JSON file: `{"rules": [ ... ]}`. Every rule has an `id` and a `type`, and can set `"active": false` to switch it off. The built-in examples are in `src/estimate_gap/rules/default_rules.json`.

| type | parameters | flags when |
|---|---|---|
| `missing_operation` | `ops` (optional filter) | a reference line has no matching target line and isn't `included_in_parent` |
| `hours_delta` | `threshold` (default 0.3) | matched lines differ in `hours` or `refinish_hours` by more than the threshold |
| `refinish_missing` | `panels` (optional list) | a target `R&R` panel has no refinish line and no refinish hours |
| `not_included_op` | `when`, `expect`, `hours_hint`, `message` | a target line matches `when` but no other target line matches `expect` |

`when` and `expect` can match on `op`, `part_area`, `part_area_in`, `desc_contains`, and `side: "same"` (expect only). Example:
```json
{"id": "EX-004", "type": "not_included_op",
 "when": {"op": "R&R", "part_area": "quarter panel"},
 "expect": {"desc_contains": "corrosion protection"}, "hours_hint": 0.5}
```

## Open-core boundary
This repo contains the open core: parsers, normalizer, differ, rule engine, example rules, synthetic samples, CLI and tests. A hosted service, tuned rule packs and support are separate, closed offerings and are not included here.

## Data policy
Only synthetic data belongs here (see `samples/README.md`). Never commit real estimates, VINs, claim numbers, names, insurer details or vendor data or text.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).

## License
Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
