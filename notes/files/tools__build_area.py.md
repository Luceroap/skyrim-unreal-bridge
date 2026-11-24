## Purpose
Converts Skyrim NIF models from area JSON files to OBJ format and generates placement CSV data for Unreal Engine import. Handles mod overrides and manages file outputs while detecting stale conversions.

## How it is run
Command: `python -I build_area.py <Data dir> <area.json> <out_dir>`. Called by `tools/asset_service.py` (via subprocess), `tools/auto_build.py`, and as part of the sequence: `esm_area.py → build_area.py → textures.py → blender_export.py → import_area.py`.

## Inputs
- `Data dir`: Directory containing Skyrim BSA files and loose files (e.g., `Skyrim/Data`).
- `area.json`: Path to area definition JSON file (e.g., `whiterun/area.json`).
- `out_dir`: Output directory for converted files (e.g., `area2`).

## Outputs
- `out/obj/*.obj`: Converted model files.
- `out/nif/*.nif`: Original NIF files.
- `out/placements.csv`: CSV with model placements (format: `model_name,x,y,z,rotation_x,rotation_y,rotation_z,scale`).
- Deletes stale `out/export/*.fbx` and `unreal/SkyBridge/Content/Area2/*.uasset` files when reprocessing.

## Key functions
open_archives - Gather mesh BSAs in order (mods override vanilla)
asset - Mangle filename paths (replace `/` and ` ` with `_`)
extract - Parse NIF geometry data
write_obj - Generate OBJ file
placements CSV - Create placement metadata

## Depends on
tools/bsa.py (BSP archive handling)
tools/nif2obj.py (NIF-to-OBJ conversion)

## Gotchas
- Stale OBJ exports delete old FBX/UAsset files to force rebuild.
- Mod archives override vanilla meshes (mod BSAs processed first).
- Uses `.v2` marker file to detect outdated OBJ conversions.
- Skips models with no geometry (reports "no geometry" failure).
- Only processes mesh-related BSAs (ignores textures/sounds/patches).

Source: read, not executed.
