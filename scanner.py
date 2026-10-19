"""Scanner: extract and count string literals across source files."""

import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set

# Common extensions to scan.
DEFAULT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".rb", ".php", ".swift", ".kt", ".scala",
    ".cs", ".vue", ".svelte",
}

# Strings we never want to report (too generic / structural).
IGNORED = {
    "", " ", "\n", "\t", "utf-8", "utf8", "ascii", "r", "w", "rb",
    "wb", "a", "b", "true", "false", "none", "null", "undefined",
}

# Regex matching single- or double-quoted strings (no triple quotes, no escapes handling beyond simple).
_STRING_RE = re.compile(r'''(?<![A-Za-z0-9_])(?:"((?:\\.|[^"\\])*)"|'((?:\\.|[^'\\])*)')''')

# Heuristic comment stripping: remove // line comments and # line comments outside strings.
_LINE_COMMENT_RE = re.compile(r"(?://|#).*$", re.MULTILINE)


@dataclass
class Occurrence:
    path: str
    line: int


@dataclass
class ScanResult:
    counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    locations: Dict[str, List[Occurrence]] = field(default_factory=lambda: defaultdict(list))


def _strip_comments(text: str) -> str:
    return _LINE_COMMENT_RE.sub("", text)


def extract_strings(text: str) -> List[tuple]:
    """Return list of (string_value, line_number) for all string literals."""
    cleaned = _strip_comments(text)
    results = []
    for m in _STRING_RE.finditer(cleaned):
        value = m.group(1) if m.group(1) is not None else m.group(2)
        # line number based on original text position
        line = text.count("\n", 0, m.start()) + 1
        results.append((value, line))
    return results


def scan_directory(
    root: str,
    extensions: Set[str] = None,
    exclude: Set[str] = None,
    min_length: int = 4,
    min_count: int = 3,
) -> ScanResult:
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS
    if exclude is None:
        exclude = {".git", "node_modules", "__pycache__", "dist", "build", "venv", ".venv"}

    result = ScanResult()
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded dirs
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in extensions:
                continue
            full = os.path.join(dirpath, fn)
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            rel = os.path.relpath(full, root)
            for value, line in extract_strings(text):
                if len(value) < min_length:
                    continue
                if value in IGNORED:
                    continue
                # skip strings that look like paths/urls? keep simple
                result.counts[value] += 1
                result.locations[value].append(Occurrence(path=rel, line=line))

    # filter by min_count
    for key in list(result.counts.keys()):
        if result.counts[key] < min_count:
            del result.counts[key]
            del result.locations[key]

    return result
