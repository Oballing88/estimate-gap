# Contributing

1. Fork, create a branch, and run `pip install -e '.[test]' && pytest`.
2. Add tests for every change. A new rule type needs tests that show both a hit and a miss.
3. Use synthetic data only. Do not include real estimates, VINs, names, claim numbers or insurer details, and do not copy labor times, procedure text or op codes from MOTOR, CCC, Mitchell or any other vendor. Rules must be your own wording.
4. Never commit secrets. CI runs gitleaks.
5. Open a pull request that explains the change. By contributing you agree that your work is licensed under Apache-2.0.
