## Purpose
This tool generates structured project indexes for Python and C++ symbols, imports, entry points, and TODOs. It processes source files using AST and regex to create reference files stored in notes/index/.

## How it is run
Command: `python tools/make_project_index.py`. Called by `tools/export_data.py` (line 24).

## Inputs
All Python (.py) and C++ source files (excluding directories in SKIP list), plus .bat and .md files.

## Outputs
notes/index/SYMBOLS.md, notes/index/CPP.md, notes/index/IMPORTS.md, notes/index/ENTRYPOINTS.md, notes/index/CONTROLS.md, notes/index/TODO.md, notes/index/STATS.md, notes/index/symbols.json.

## Key functions
files()
read()

## Depends on
ast, collections, glob, json, os, re

## Gotchas
- Skips paths in SKIP list (e.g., .git, build/, deps/)
- C++ index uses approximate regex line numbers
- Dynamic imports are not tracked
- Entry points must contain `if __name__ == '__main__'`
- TODO entries must be under 400 characters

Source: read, not executed.
