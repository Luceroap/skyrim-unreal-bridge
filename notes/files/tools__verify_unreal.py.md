## Purpose
Compares Unreal engine's placed-object bounds (from `area2/ue_actors.csv`) with Skyrim game data (from `refs_with_bounds.tsv`), converting both to Unreal coordinate space to detect mismatches. Reports errors per object and model.

## How it is run
Command: `python -I verify_unreal.py refs_with_bounds.tsv area2`
Called by `unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.cpp` at line 84 during game runtime.

## Inputs
- `refs_with_bounds.tsv`: TSV file containing game reference data (line 13+ of code).
- `area2` directory: Contains `placements.csv` (game placements) and `ue_actors.csv` (Unreal actor data).

## Outputs
Prints summary statistics to stdout:
- Total objects, matched objects, and missing matches.
- Models with mismatched bounds (top 30 ranked by error).
- Format: `MISMATCH [model] refs=[count] bound-centre err=[value] (x radius) radius ratio=[value]`.

## Key functions
- `asset`: Normalizes mesh paths (removes `meshes/`, `.nif` suffix).
- Position matching: Finds nearest Unreal actor to game position (Euclidean distance).
- Error calculation: Computes normalized error between bounds.
- Threshold check: Flags models with error >0.35 or radius ratio outside 0.5–2.0.
- Res storage: Accumulates error metrics per model.

## Depends on
- Imports: `sys`, `os`, `math`, `collections`.
- File dependencies: `area2/placements.csv`, `area2/ue_actors.csv`, `refs_with_bounds.tsv`.

## Gotchas
- Uses fixed unit conversion factor `U = 1.4287` for coordinate system alignment.
- Skips terrain placements (filter `r[0] != "terrain"`).
- Ignores TSV rows where `f[11] == "1"`.
- Requires `.nif` mesh files (skips other formats).
- Fails if `asset()` returns `None` (invalid file path).

Source: read, not executed.
