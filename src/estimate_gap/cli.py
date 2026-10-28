from __future__ import annotations

import argparse
import sys

from .parsers import load
from .report import to_json, to_text
from .rules import load_rules, run_rules


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="estimate-gap", description="Read-only gap check between two estimates."
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compare", help="compare a reference estimate (a) to a target estimate (b)")
    c.add_argument(
        "a",
        help="reference estimate, e.g. a file exported from one estimating system (.json or .csv)",
    )
    c.add_argument(
        "b", help="target estimate, e.g. a file exported from another system (.json or .csv)"
    )
    c.add_argument("--rules", help="path to a rules JSON file (default: built-in examples)")
    c.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)
    try:
        ref, target = load(args.a), load(args.b)
        flags = run_rules(ref, target, load_rules(args.rules))
    except OSError as exc:
        print(
            f"error: cannot read {exc.filename or 'file'}: {exc.strerror or exc}", file=sys.stderr
        )
        return 2
    except ValueError as exc:  # includes bad JSON/CSV, schema and rule errors
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(to_json(ref, target, flags) if args.format == "json" else to_text(ref, target, flags))
    return 0


if __name__ == "__main__":
    sys.exit(main())
