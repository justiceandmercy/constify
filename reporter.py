"""Reporter: format scan results for humans or machines."""

import json
from typing import List

from scanner import ScanResult


def _sorted_items(result: ScanResult):
    return sorted(result.counts.items(), key=lambda kv: (-kv[1], kv[0]))


def format_text(result: ScanResult, limit: int = 50) -> str:
    lines = []
    items = _sorted_items(result)[:limit]
    if not items:
        lines.append("No repeated string literals found.")
        return "\n".join(lines)
    for value, count in items:
        lines.append(f'"{value}"  ({count} occurrences)')
        for occ in result.locations[value]:
            lines.append(f"  {occ.path}:{occ.line}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_json(result: ScanResult, limit: int = 50) -> str:
    items = []
    for value, count in _sorted_items(result)[:limit]:
        items.append({
            "string": value,
            "count": count,
            "locations": [{"path": o.path, "line": o.line} for o in result.locations[value]],
        })
    return json.dumps({"results": items}, indent=2) + "\n"


def format_summary(result: ScanResult) -> str:
    total = sum(result.counts.values())
    unique = len(result.counts)
    return f"Found {unique} repeated string literal(s) across {total} occurrence(s)."
