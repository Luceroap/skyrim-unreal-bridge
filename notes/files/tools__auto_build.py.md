## Purpose
Rebuilds the Unreal scene incrementally from Skyrim plugin data and game files, converting only new models/textures. Merges live-dump data with Skyrim.esm references, processes assets, and restarts Unreal Editor to apply changes.

## How it is run
Command: `python C:\Users\Aidan\SkyrimUnrealBridge\tools\auto_build.py [--no-restart-ue]`.  
Triggered by README.md line 103 ("`python tools\auto_build.py`"), and called directly by users in the workflow.

## Inputs
- `SKSE_DIR/SkyrimUnrealBridge_refs_all.tsv` (model references)
- `SKSE_DIR/SkyrimUnrealBridge_centers.txt` (position data)
- `whiterun/area_all.json` (area definition)
- `DATA/Skyrim.esm` (game data)
- `area2/tex/*.png` (texture files)
- `DATA` directory (game asset paths)

## Outputs
- `area2/placements.csv` (updated position data, includes terrain)
- `area2/obj/terrain.obj` (generated terrain mesh)
- Re-launches Unreal Editor (`UnrealEditor.exe`)

## Key functions
main
run
running

## Depends on
`merge_area.py`, `build_area.py`, `textures.py`, `textures_pbr.py`, `esm_land.py`, `blender_export.py`, Pillow (PIL)

## Gotchas
- Hardcoded absolute paths (e.g., D:\SteamLibrary, D:\UE_5.8) for Skyrim data/Unreal engine.
- Force-terminates `UnrealEditor.exe` (may lose unsaved work).
- Requires `Pillow` for texture analysis (PIL import).
- Always appends terrain data to `placements.csv` if missing.
- Uses Blender’s CLI (`blender.exe -b -P`) to export models.

Source: read, not executed.
