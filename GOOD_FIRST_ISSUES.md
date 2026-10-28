# Good first issues

Starter tasks for new contributors. Each one is small and has clear acceptance criteria. To claim one, open an issue with the title and say you're working on it. Read [CONTRIBUTING.md](CONTRIBUTING.md) first.

Ground rules for all of them: add tests, keep the tool read-only, use synthetic data only, and never copy labor times, procedure text or op codes from any vendor.

## 1. Pre-commit config for ruff
**Scope:** Add a `.pre-commit-config.yaml` that runs `ruff check` and `ruff format` on commit, and document it in CONTRIBUTING.md. CI already runs both.
**Acceptance:**
- `pre-commit run --all-files` passes on a clean checkout.
- CONTRIBUTING.md has a short "set up pre-commit" step.
- `pre-commit` is added to the `dev` extra in `pyproject.toml`.

## 2. Vendor-term CI guard
**Scope:** Add a small script (and a CI job) that fails if tracked files outside NOTICE and README.md's disclaimer text contain vendor names or trademarks. Keep the term list in one plain file so it is easy to edit.
**Acceptance:**
- The script exits non-zero and prints file and line for a match, and zero on the current repo.
- A test shows one hit and one miss.
- The CI workflow runs it.
- The allowed-files list is documented in CONTRIBUTING.md.

## 3. More synthetic sample estimates
**Scope:** Add two or three new made-up estimate pairs under `samples/` that exercise different situations (for example a bumper-only job, a door with a blend, a pair with no gaps at all). Update `samples/README.md`.
**Acceptance:**
- Each file has `"synthetic": true` and no real names, VINs, claim numbers or vendor names.
- Each pair has a test that asserts the exact flags expected (including a "no flags" pair).
- `samples/README.md` lists each pair and what it demonstrates.

## 4. CSV column-mapping config
**Scope:** Let users map their own CSV column headers to the tool's field names, using a small JSON file passed with `--columns`. For example `{"Operation": "op", "Part": "part_area", "Labor": "hours"}`.
**Acceptance:**
- `estimate-gap compare a.csv b.csv --columns map.json` works with renamed headers.
- Unmapped columns are ignored, and a mapping to an unknown field gives a clear error.
- Tests cover a renamed-header CSV, an unknown field, and no `--columns` (unchanged behavior).
- The README input-format section documents the option.

## 5. Optional YAML rule loader
**Scope:** Allow rule files in YAML (`.yaml` / `.yml`) as well as JSON, with the same structure. YAML support must be an optional extra (`pip install 'estimate-gap[yaml]'`) so the core keeps zero runtime dependencies.
**Acceptance:**
- `--rules my_rules.yaml` loads and runs the same rules as the JSON equivalent.
- A missing PyYAML gives a clear message that names the extra.
- Tests check that a YAML file and its JSON twin produce the same flags.
- README rule-format section mentions YAML.

## 6. Standalone HTML report
**Scope:** Add `--format html` that writes a single self-contained HTML page (no external scripts or fonts): flags grouped by rule, with the two matching lines side by side.
**Acceptance:**
- Output is one file with inline CSS only and opens in a browser offline.
- All text from estimate files is HTML-escaped (test with a description containing `<script>`).
- A test checks the flag count and one escaped value.
- Existing `text` and `json` outputs are unchanged.

## 7. Rule documentation generator
**Scope:** Add a command, `estimate-gap rules --list` (or a script), that prints a Markdown table of every rule in a rules file: id, type, when it flags, and whether it is active. Use it to generate `docs/rules.md` for the built-in examples.
**Acceptance:**
- Output covers all four rule types and shows `active: false` rules as inactive.
- A test fails if `docs/rules.md` is out of date with `default_rules.json`.
- No rule text is copied from any vendor.

## 8. Rule-file validation command
**Scope:** Add `estimate-gap rules --validate FILE` that checks a rules file and reports problems: missing `id`, duplicate ids, unknown `type`, missing required parameters, and wrong value types.
**Acceptance:**
- Exit code 0 for a valid file (including the built-in examples), non-zero otherwise.
- Each error names the rule id (or position) and the problem.
- Tests include one valid file and at least four invalid ones.

## 9. Per-type summary and exit-code option
**Scope:** The text report already ends with `Summary: N flag(s); about Xh to review.` Extend it with a count per rule type (for example `1 missing op, 2 hours, 1 refinish, 2 companion`). Add `--fail-on-flags` so scripts can get a non-zero exit code when any flag is found.
**Acceptance:**
- The per-type counts add up to the total flags listed.
- `--fail-on-flags` exits 1 with flags, 0 without. Default behavior stays exit 0.
- Tests cover both modes and the summary text.

## 10. Plain-language glossary
**Scope:** Add `docs/glossary.md` explaining each term the tool uses (R&I, R&R, refinish, blend, sublet, included in parent, companion op) in your own words, for someone who is new to the tool. Link it from the README.
**Acceptance:**
- Every `op` value in the README's input table has an entry.
- Definitions are written from scratch with no copied vendor text.
- A shop estimator or other reviewer confirms in the pull request that the definitions read correctly.
