#!/usr/bin/env python3
"""constify: find repeated string literals and suggest constants."""

import argparse
import os
import sys

from scanner import scan_directory
from reporter import format_text, format_json, format_summary


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="constify",
        description="Find repeated string literals in source code.",
    )
    parser.add_argument("path", nargs="?", default=".", help="directory to scan")
    parser.add_argument("--min-count", type=int, default=3, help="minimum occurrences (default 3)")
    parser.add_argument("--min-length", type=int, default=4, help="minimum string length (default 4)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    parser.add_argument("--limit", type=int, default=50, help="max results to show")
    parser.add_argument("--exclude", default="", help="comma-separated dir names to exclude")
    parser.add_argument("--ext", default="", help="comma-separated extensions to include (e.g. .py,.js)")
    args = parser.parse_args(argv)

    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    exclude = set(x.strip() for x in args.exclude.split(",") if x.strip())
    extensions = None
    if args.ext:
        extensions = set(x.strip().lower() for x in args.ext.split(",") if x.strip())

    result = scan_directory(
        root,
        extensions=extensions,
        exclude=exclude if exclude else None,
        min_length=args.min_length,
        min_count=args.min_count,
    )

    if args.format == "json":
        print(format_json(result, limit=args.limit), end="")
    else:
        print(format_summary(result))
        print()
        print(format_text(result, limit=args.limit), end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
