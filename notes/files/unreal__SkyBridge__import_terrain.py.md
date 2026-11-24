## Purpose
Imports terrain geometry from a pre-exported FBX file into Unreal Engine and applies a material with vertex color support. Configures the terrain mesh with a single flat-brown material without landscape blending or texture blending.

## How it is run
Called by `tools/esm_land.py` (as seen in `git grep` output), which processes Skyrim terrain data through Blender. No direct command-line invocation; executes as a dependency in the terrain import workflow.

## Inputs
- FBX file: `area/export/terrain.fbx`
- Texture asset: `/Game/AreaTex/terrain_detail`
- Preexisting mesh: `/Game/Area/terrain` (loaded for material assignment)

## Outputs
- Material asset: `/Game/Area/M_Terrain2` (modified with texture and vertex color)
- Updated mesh asset: `/Game/Area/terrain` (with new material applied)
- Console log: `TERRAIN2 slots=<count> ext=(x,y,z)`

## Key functions
create_asset
load_asset
set_editor_property
create_material_expression
connect_material_expressions
recompile_material
save_loaded_asset

## Depends on
- `tools/esm_land.py` (invokes this script)
- `area/terrain_obj/terrain.obj` (source data for Blender conversion)
- `/Game/AreaTex/terrain_detail` (texture asset)

## Gotchas
Hardcoded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\`
`replace_existing=True` overwrites existing terrain assets
Uses single flat-brown material without landscape blending
Modifies mesh in-place (`mesh.set_material()`)
Writes console log with terrain dimensions

Source: read, not executed.
