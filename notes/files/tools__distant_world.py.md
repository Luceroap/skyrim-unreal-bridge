## Purpose
Processes Skyrim's REFR (Reference) records from plugins to identify distant objects (mountains, cliffs, rocks, trees) that exist beyond the game's loaded cells. Generates JSON files describing these objects for Unreal Engine's live stream to render at long range with high detail.

## How it is run
Command line: `python tools/distant_world.py [--stats]` or with options like `--interiors <edid prefix>`, `--world <ws edid>`, `--water`, or `--dungeons`.

Other files calling it: `unreal/SkyBridge/live_bridge.py` (uses outputs like `area2/distant_refs.json`, `area2/water_wide.csv`), `README.md`, `COORDINATION.md`.

## Inputs
- Skyrim plugin files at `DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"` (Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, Dragonborn.esm).
- Command line arguments for specific outputs (`--interiors`, `--world`, `--water`, `--dungeons`).

## Outputs
- `area2/distant_refs.json`: Main output with object data (43k entries), format: `[id, model, nif, pos, rot, scale, kind]`.
- `area2/world_<ws>.json`: Dumped references for specific worldspaces.
- `area2/interiors_<prefix>.json`: Interior cell references for specified prefixes.
- `area2/water_wide.csv` and `area2/water_quads.csv`: Water cell height data.
- `area2/interiors_dungeons_*.json` and `area2/dungeon_index.json`: Dungeon interior cell data.
- `area2/dungeon_models.txt`: Model statistics for dungeon references.

## Key functions
subs: Unpacks plugin record sub-sections
rot_from_angles: Calculates rotation matrix from Euler angles
read_plugin: Processes Skyrim plugin file data
classify: Categorizes models into mountain/cliff/rock/tree
remapper: Maps plugin form IDs to runtime IDs
scan_refs: Scans references from Skyrim plugins
ref_items: Filters references with models
dump_world: Dumps world references to JSON
dump_interiors: Dumps interior cell references
dump_dungeons: Dumps dungeon interior cell references
main: Command-line entry point
land_heights: Processes land height data from LAND records
read_water: Processes water cell data
write_water_csv: Outputs water cell height data
dump_water: (Not a function name, skipped)

## Depends on
- Imports: json, math, os, struct, sys, zlib, collections.Counter.
- Skyrim plugin files at `DATA` path.
- `live_bridge.py` uses its output files (`distant_refs.json`, `water_wide.csv`).

## Gotchas
- Hardcoded Skyrim data path `D:\SteamLibrary\...` (user-specific).
- Skips models with paths in `SKIP = ("lod", "marker", "/plants/", "/grass/", "effects/")`.
- Uses runtime form IDs instead of plugin-local IDs via `remapper`.
- Main output `distant_refs.json` contains ~43k mountain/cliff/rock/tree entries as noted in README.md.
- Only processes REFR records for objects with models (not LODs or markers).

Source: read, not executed.
