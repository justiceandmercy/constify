# constify

Find repeated string literals in your source code and suggest extracting them into constants.

## Description

`constify` scans a codebase for string literals that appear multiple times and reports them with
locations, so you can replace magic strings with named constants. It is language-agnostic (regex
based) and works on Python, JavaScript, TypeScript, Go, Rust, Java and more.

## Features

- Recursively scans a directory for source files
- Detects single- and double-quoted string literals
- Filters by minimum occurrence count and minimum length
- Ignores strings inside comments heuristically
- Groups results by string with all `file:line` locations
- JSON output for CI integration
- Zero external dependencies (standard library only)

## Install

```sh
git clone https://github.com/yourname/constify.git
cd constify
python3 constify.py --help
```

Or copy `constify.py`, `scanner.py`, `reporter.py` into your project.

## Usage

```sh
# Scan current directory, strings appearing 3+ times, min length 4
python3 constify.py .

# Custom thresholds
python3 constify.py src/ --min-count 2 --min-length 6

# JSON output
python3 constify.py . --format json

# Exclude directories
python3 constify.py . --exclude node_modules,dist,.git
```

Example output:

```
"application/json"  (4 occurrences)
  src/api.py:12
  src/api.py:45
  src/client.js:8
  tests/test_api.py:3

"error"  (3 occurrences)
  src/handler.py:20
  src/handler.py:33
  src/util.py:7
```

## License

MIT
