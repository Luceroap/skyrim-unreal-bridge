## Purpose
Compares architectural reference data from the Skyrim plugin (in a TSV file) with Unreal engine placement data (in a CSV file) for Whiterun structures. It specifically validates if object positions and rotations match exactly or fall within acceptable tolerances, excluding LOD models and terrain entries.

## How it is run
Command: `python -I compare_refs.py <refs.tsv> <placements.csv> [player_x player_y radius]`
Other files that call it: `README.md` (line 96) references it as `tools/compare_refs.py <tsv> area2/placements.csv`.

## Inputs
- `<refs.tsv>`: Plugin-generated reference TSV (e.g., `SkyrimUnrealBridge_refs.tsv`), 13+ fields per line.
- `<placements.csv>`: Unreal placement CSV (e.g., `area2/placements.csv`), comma-separated with 8+ fields per line.
- Optional positional arguments: `player_x player_y radius` (defaults to `20848 -7352 11000`).

## Outputs
Console output showing:
- Counts of total references, Whiterun architecture (non-LOD), and placements.
- Exact matches (position/rotation within 2 units and 1 degree), positional/rotational shifts, and missing references.
- Extra placements not found in-game (within radius, up to 15 samples).
- Top 25 mismatched object categories by model folder (e.g., `meshes/actors`).
- Sample of first 25 mismatches (position, rotation, distance).

## Key functions
asset: Normalizes model paths to clean asset names.

## Depends on
- Python standard libraries: `sys`, `math`, `collections`.
- Input data files: `SkyrimUnrealBridge_refs.tsv` (plugin output) and `area2/placements.csv` (Unreal placements).

## Gotchas
- Skips TSV lines with fewer than 13 fields.
- Skips placements.csv entries with first field "terrain".
- Uses default radius 11000 minus 1500 for extra placements check (9500).
- Prints only first 15 extra placements beyond radius threshold.
- Limits mismatch samples to first 25 entries.

Source: read, not executed.
