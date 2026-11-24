## Purpose
Imports Skyrim area meshes and textures into Unreal Engine, creates texture-driven materials (with masked blending for specified textures), and assigns materials to mesh slots based on naming conventions.

## How it is run
Executed as part of the build pipeline (via Unreal's Python API) after `build_area.py`, `textures.py`, and `blender_export.py` (per `README.md` sequence). Command line not applicable; runs during build automation.

## Inputs
- FBX files: `area/export/*.fbx`
- Textures: `area/tex/*.png`
- Masked texture keys: `area/tex/alpha_masked.txt`

## Outputs
- Meshes: Saved to `/Game/Area/`
- Textures: Saved to `/Game/AreaTex/`
- Materials: Created as `M_`*key*` in `/Game/AreaTex/`
- Updated meshes: Saved with assigned materials (via `save_loaded_asset`)

## Key functions
Import FBX assets
Import texture assets
Create materials with masked blending
Assign materials by slot name pattern
Save updated mesh assets

## Depends on
None (uses Unreal API modules; no other project files imported)

## Gotchas
- Hardcoded Windows path (`C:\Users\Aidan\SkyrimUnrealBridge`)
- Material slot names must end with `_key_dds` (e.g., `wood_dds`)
- `alpha_masked.txt` must exist for masked material handling
- Slot naming pattern must match exactly (e.g., `_wood_dds`)
- Uses PNG textures but checks slot names for `_dds` (potential inconsistency)

Source: read, not executed.
