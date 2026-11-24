## Purpose
Exports large references (e.g., city walls, towers, castles) from Skyrim.esm for Unreal preview spawns until live streaming via plugin. Outputs structured JSON data for Unreal scene placement.

## How it is run
Command: `python -I large_refs_preview.py [worldspace edid]` (default worldspace: `whiterunworld`). Referenced in `README.md:118`, `COORDINATION.md:141`, and `HANDOFF_FOR_CURSOR.md:57` as the generator for `area2/large_preview.json`. No other code files in project call it directly (verified via `git grep`).

## Inputs
- Optional worldspace EDID (e.g., `whiterunworld` for Windhelm).
- Skyrim.esm (hardcoded path: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\Skyrim.esm`).

## Outputs
- `area2/large_preview.json`: JSON array of objects with `id`, `model`, `pos` (3D position), `rot` (3x3 matrix row-major), `scale`.

## Key functions
- `subs`: Parses ESM buffer into (type, data) pairs.
- `rot_from_angles`: Converts Euler angles to 3x3 rotation matrix (matches plugin).
- `walk`: Recursively processes ESM groups to collect large references.

## Depends on
- `Skyrim.esm` at fixed path.
- `area2/` directory structure.
- Hardcoded `ROOT` (`C:\Users\Aidan\SkyrimUnrealBridge`).

## Gotchas
- Skips models with spaces in path (e.g., `effects/` or `marker`).
- Excludes references with `rot` computed from plugin's `RotFromAngles` (matching `distant_world.py`).
- Hardcoded default worldspace `whiterunworld` if no argument provided.
- Requires `Skyrim.esm` in specific Steam library path.
- Uses zlib-compressed data for flagged records (flag `0x40000`).

Source: read, not executed.
