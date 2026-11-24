## Purpose
Imports terrain texture files and FBX mesh into Unreal Engine, configuring materials with texture mappings and roughness settings for the Area2 terrain mesh.

## How it is run
Executed directly within Unreal Engine's Python environment; no other project files call it (git grep found no callers).

## Inputs
- Texture files: `area2/tex/terrain_tile_*.png`
- Mesh file: `area2/export/terrain.fbx`

## Outputs
- Materials written to: `/Game/Area2Tex/`
- Updated terrain mesh saved at: `/Game/Area2/terrain`
- Log message: `TERRAIN3 materials %d/%d ext=(%.0f,%.0f,%.0f)`

## Key functions
task
create_asset
load_asset
delete_all_material_expressions
create_material_expression
connect_material_property
recompile_material
save_loaded_asset
set_material
mesh.get_bounds
mesh.static_materials
eal.does_asset_exist
eal.save_loaded_asset

## Depends on
None (relies on external assets, no other project files imported)

## Gotchas
- Hard-coded absolute path `C:\Users\Aidan\SkyrimUnrealBridge\area2` may break if project location changes.
- Requires material slot names to exactly match texture asset names (e.g., slot `Diffuse` requires texture `Diffuse`).
- Skips material slots without matching textures in `/Game/Area2Tex`.
- Assumes terrain mesh is named `terrain` at `/Game/Area2/terrain`.
- Overwrites existing materials in `/Game/Area2Tex` without confirmation.

Source: read, not executed.
