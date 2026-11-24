## Purpose
This document describes lines 674-846 of `unreal/SkyBridge/remaster_materials.py`, which is part 2 of a 2-part file. The code focuses on material instance creation, mesh material conversion, and terrain/landscape adjustments for the Skyrim-to-Unreal project.

## How it is run
Command line: `UnrealEditor-Cmd.exe SkyBridge.uproject -run=pythonscript -script=unreal/SkyBridge/remaster_materials.py`  
Other files that call it: `live_bridge.py`, `npc_live.py` (confirmed via `git grep`).

## Inputs
- File: `area2/export/lodterrain.fbx` (for `lod_terrain`)
- Textures: `area2/tex/<key>.png` (via `_import_tex` for `hair_instance`)

## Outputs
- Material instances saved in `DEST` (e.g., `MI_hair_<key>_<rrggbb>`)
- Modified static meshes in `/Game/Area2` (material slot updates)
- Nanite enabled on landscape meshes (via `nanite_landscape`)

## Key functions
hair_instance(key, tint) - Creates hair material instance from texture.
npc_skin(mi) - Configures skin material to use subsurface profile.
lod_terrain() - Imports and textures LOD terrain mesh.
fix_missing_slots() - Fills missing material slots in meshes.
nanite_landscape() - Enables Nanite on landscape meshes (headless only).
ensure_usage(m) - Sets material usage flags to avoid runtime recompilation.
convert_all() - Main function: converts all materials and updates assets.

## Depends on
- Project modules: `eal`, `mel`, `at`, `ue_assets`.
- Other project functions: `master()`, `hair_material()`, `instance_for(key)`, `rain_material()`, `water_material()`.

## Gotchas
- Enabling Nanite with `nanite_landscape` requires headless operation (crashes in live editor).
- `lod_terrain` function requires `area2/export/lodterrain.fbx` to exist.
- `fix_missing_slots` only processes meshes under `/Game/Area2`.
- `hair_instance` generates unique names from RGB tint values (0-255).
- `convert_all` reconfigures instances via `configure(mi, mi.get_name()[3:])`.

Source: read, not executed.
