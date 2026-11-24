## Purpose
Compares game model bounds from plugin dumps against converted Unreal models, checking geometric alignment, coverage of models in placements, and scale discrepancies. Validates that imported models match the game's coordinate system and bounding volumes.

## How it is run
Command line: `python -I verify_models.py <refs.tsv> <area2 dir> [placements.csv]`. No other project files call this script (confirmed via `git grep`).

## Inputs
- `refs.tsv`: TSV file with model reference data (columns 30+ required).
- `area2 dir`: Directory containing `obj/` subdirectory and `placements.csv` (default path).
- Optional `placements.csv` (defaults to `<area2 dir>/placements.csv`).

## Outputs
- Prints summary reports to stdout (geometry OK counts, suspicious models).
- Writes `verify_report.json` to `area2` directory containing `suspicious` and `not_converted` lists.

## Key functions
asset: Normalizes NIF model paths to lowercase with underscore separators.
obj_bounds: Calculates OBJ file bounding box center and radius from vertex data.

## Depends on
Standard Python modules: sys, os, math, collections, json.

## Gotchas
- Skips TSV entries with fewer than 30 columns.
- Skips entries where TSV column 11 (game code) is "1".
- Requires valid OBJ files in `area2/obj/` for geometry comparison.
- Models without matching OBJ files are marked as "loaded but not converted".
- Uses model scale and game bounds to calculate radius ratio (affects geometry pass/fail).

Source: read, not executed.
