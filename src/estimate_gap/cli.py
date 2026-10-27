from __future__ import annotations

import argparse
import sys

from .parsers import load
from .report import to_json, to_text
from .rules import load_rules, run_rules


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="estimate-gap", description="Read-only gap check between two estimates.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compare", help="compare a reference estimate (a) to a target estimate (b)")
    c.add_argument("a", help="reference estimate, e.g. a Mitchell-style export (.json or .csv)")
    c.add_argument("b", help="target estimate, e.g. a CCC-style export (.json or .csv)")
    c.add_argument("--rules", help="path to a rules JSON file (default: built-in examples)")
    c.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)
    ref, target = load(args.a), load(args.b)
    flags = run_rules(ref, target, load_rules(args.rules))
    print(to_json(ref, target, flags) if args.format == "json" else to_text(ref, target, flags))
    return 0


if __name__ == "__main__":
    sys.exit(main())
