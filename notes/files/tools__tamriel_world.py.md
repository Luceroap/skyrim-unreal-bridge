## Purpose
Processes Skyrim's world data from official master files to generate JSON files for Unreal Engine. Maps form IDs to a consistent runtime order across Skyrim's master files, categorizes objects into "far" and "near" tiles for streaming, and excludes non-essential items like loose items and effects.

## How it is run
Command line: `python tools/tamriel_world.py [--stats]`  
Called by `unreal/SkyBridge/tamriel_live.py` (line 3 in file), referenced in `COORDINATION.md` (line 141), and depends on `tools/distant_world.py` (line 166).

## Inputs
- Skyrim master files at `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data` (hard-coded path).
- Master filenames: `Skyrim.esm`, `Update.esm`, `Dawnguard.esm`, `HearthFires.esm`, `Dragonborn.esm`.
- Worldspace data via ESM file parsing (WRLD/CELL/REFR/LAND/LTEX/TXST records).

## Outputs
- `area2/tamriel/models.json`: `[asset name, nif path]` list.
- `area2/tamriel/mountains.json`: Mountain/cliff data (always drawn).
- `area2/tamriel/f_<tx>_<ty>.json`: "Far" objects (16x16-cell tiles).
- `area2/tamriel/n_<tx>_<ty>.json`: "Near" objects (4x4-cell tiles).
- `area2/tamriel/index.json`: Tile counts and configurations.
- `area2/tamriel/worlds.json`: `{edid: full name}` for worldspaces.
- `area2/tamriel/city_cells.json`: City worldspace cell coverage.

## Key functions
keep - Filters out loose items/effects/markers
kind - Categorizes models (mountain/far/near)
read_masters - Parses ESM plugin order
Remap - Maps form IDs to runtime order
scan - Processes ESM data records
main - Generates output files

## Depends on
- `tools/distant_world.py` (imports `subs`, `MODEL_TYPES`).
- `unreal/SkyBridge/tamriel_live.py` (consumes output files).
- `COORDINATION.md` (references `tamriel_world.py` for skip condition).

## Gotchas
- Hard-coded Skyrim Data path `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data` (unadjustable).
- Deletes existing `n_*.json`/`f_*.json` before writing new ones.
- Skips any model name containing a space (`" " in m`).
- Uses 4096 units per cell (as per comment: "a cell is 4096 units").
- Only processes exterior cells (ignores interior cells/quest data).

Source: read, not executed.
