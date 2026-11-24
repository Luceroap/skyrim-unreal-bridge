## Purpose
This script corrects material assignments on static meshes by replacing missing or incorrectly named materials with predefined materials (e.g., transparent "hidden" material for unrendered objects). It ensures proper material mapping by resolving Blender's naming conventions and fixing material references in mesh slots.

## How it is run
Executed within the Unreal Editor as a standalone Python script. No other files call it directly (verified by empty `git grep` results for "fix_slots.py").

## Inputs
- Materials in `unreal/SkyBridge/Content/Area2Tex/M_*.uasset`
- Static meshes in `unreal/SkyBridge/Content/Area2/*.uasset` (excluding "terrain" mesh)
- Hard-coded paths (e.g., `C:\Users\Aidan\SkyrimUnrealBridge\...`)

## Outputs
- Modified static meshes saved back to `unreal/SkyBridge/Content/Area2/`
- Log message: `FIXSLOTS hidden=<count> renamed-fixed=<count>`

## Key functions
create_asset
load_asset
set_material
save_loaded_asset
delete_all_material_expressions
connect_material_property
recompile_material

## Depends on
Unreal Engine API (`unreal`, `AssetToolsHelpers`, `EditorAssetLibrary`)
Hard-coded project paths (`/Game/Area2Tex/`, `/Game/Area2/`)
Material naming conventions in `M_*.uasset` files

## Gotchas
- Uses hard-coded absolute paths (`C:\Users\Aidan\SkyrimUnrealBridge`), making it non-portable.
- Skips processing the "terrain" mesh explicitly (`if n == "terrain": continue`).
- Material matching relies on exact suffix patterns (e.g., `_dds`), which may fail if naming conventions change.
- Only processes meshes with `StaticMesh` type (skips non-mesh assets).
- No error handling for missing assets or corrupted mesh data.

Source: read, not executed.
