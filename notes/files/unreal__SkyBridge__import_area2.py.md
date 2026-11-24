## Purpose
This script imports new 3D meshes (FBX), textures (PNG), and corresponding materials into Unreal Engine from a source directory. It only processes assets not already present in the Unreal project and assigns materials to meshes based on slot naming conventions.

## How it is run
Command line: `UE_CMD [UPROJECT] -run=pythonscript -script="unreal/SkyBridge/import_area2.py"`  
Called by: `tools/auto_build.py` (explicitly in line 59) and via the workflow chain from `build_area.py` → `textures.py` → `blender_export.py`.

## Inputs
- Source FBX meshes: `area2/export/*.fbx`
- Source textures: `area2/tex/*.png`
- Mask definition: `area2/tex/alpha_masked.txt` (optional, lists masked textures)

## Outputs
- Imported meshes: `/Game/Area2/<meshname>`  
- Imported textures: `/Game/Area2Tex/<texturename>`  
- Created materials: `/Game/Area2Tex/M_<texturename>`  
- Updated mesh material assignments (via `mesh.set_material()`)

## Key functions
task

## Depends on
unreal API (AssetTools, MaterialEditingLibrary, EditorAssetLibrary)  
Standard libraries: glob, os

## Gotchas
- Hard-coded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\area2` (not portable)
- Skips texture named "terrain_detail" during material creation
- Requires `alpha_masked.txt` to enable masked blend mode (missing = no masking)
- Material assignment requires mesh slot names to end with `_texturename_dds`
- Only applies materials to newly imported meshes (not existing assets)

Source: read, not executed.
