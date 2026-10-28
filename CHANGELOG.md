# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- `samples/estimate_b_synthetic.csv` now holds the same five lines as the JSON sample, so both give the same 6 flags.
- Bad input (missing file, bad JSON/CSV, schema errors, bad rules file) now prints a one-line error and exits with code 2 instead of a traceback.
- An estimate with no lines, or a CSV with no `op` column (even with no rows), is rejected instead of producing a flood of "missing" flags.
- A blank side is no longer printed as `(na)` in flag messages.

## [0.1.0] - Unreleased

### Added
- JSON and CSV estimate parsers and a normalizer for operation names and part areas.
- Line-by-line differ between a reference estimate (A) and a target estimate (B).
- Rule engine with six generic example rules: missing operation, labor-hours difference over 0.3 h, replaced panel with no refinish time, and expected companion operations.
- `estimate-gap compare` CLI with a read-only text report; estimates are never modified.
- Synthetic, vendor-neutral samples (`samples/estimate_a_synthetic.json`, `samples/estimate_b_synthetic.json`, `samples/estimate_b_synthetic.csv`).
- Test suite, ruff lint/format config, CI (tests, ruff, gitleaks), issue and PR templates.
