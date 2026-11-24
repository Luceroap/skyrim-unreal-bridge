## Purpose
Imports terrain geometry from a pre-exported FBX file into Unreal Engine, applies a custom material using a detail texture, and updates the terrain mesh with the new material. Logs bounding box dimensions for the terrain.

## How it is run
Called by `build_area.py` during the area construction workflow. The exact command line is not directly exposed but triggered as part of the automated build pipeline (`build_area.py` → `textures.py` → `blender_export.py` → `import_area2.py` + `import_terrain2.py`).

## Inputs
- `C:\Users\Aidan\SkyrimUnrealBridge\area2\export\terrain.fbx` (hard-coded source FBX)
- `/Game/Area2Tex/terrain_detail` (detail texture asset)
- `/Game/Area2/terrain` (terrain mesh asset)

## Outputs
- Material `M_Terrain2` created or loaded at `/Game/Area2/`
- Terrain mesh `/Game/Area2/terrain` updated with new material assignments
- Console log: `TERRAIN2 slots=X ext=(X,Y,Z)`

## Key functions
import_asset_tasks - Imports FBX into Unreal
create_asset - Creates M_Terrain2 material
load_asset - Loads texture/mesh references
connect_material_expressions - Links texture and vertex color
recompile_material - Compiles final material
save_loaded_asset - Saves modified mesh/material

## Depends on
`build_area.py` (triggers execution), Unreal Engine Python API (`unreal` module), `textures.py` (asset paths)

## Gotchas
- Hard-coded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\area2\export\terrain.fbx` must exist
- Material `M_Terrain2` name may conflict if pre-existing
- Requires terrain mesh named `terrain` at `/Game/Area2/`
- Detail texture path `/Game/Area2Tex/terrain_detail` must match
- Assumes `Area2` folder structure exists

Source: read, not executed.
