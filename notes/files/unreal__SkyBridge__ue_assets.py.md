## Purpose
This file provides helper functions for importing converted Skyrim models (FBX) and their textures into Unreal Engine. It handles creating PBR materials from textures (including normal maps and roughness/metallic/ao maps) and applying them to mesh slots during the live bridge process.

## How it is run
The file is executed as part of the `live_bridge.py` script (invoked via command line: `python live_bridge.py`). It is called by `unreal/SkyBridge/live_bridge.py` and referenced in `remaster_materials.py` (though the latter imports it for material functionality).

## Inputs
- `AREA` directory path: `C:\Users\Aidan\SkyrimUnrealBridge\area2`
- Texture files in `AREA/tex/` (PNG format with specific naming patterns)
- `alpha_masked.txt` and `foliage_textures.txt` (texture key lists for material rules)
- FBX models in `AREA/export/`

## Outputs
- Texture assets at `/Game/Area2Tex/{key}` in Unreal content browser
- Material assets at `/Game/Area2Tex/M_{key}`
- Mesh assets at `/Game/Area2/{model_name}` with applied materials
- Updated Unreal assets via `save_loaded_asset()`

## Key functions
_lines
_task
_texture
material_for
legacy_material_for
hidden_material
import_model
slot_material

## Depends on
unreal (Unreal Engine API)
remaster_materials.py

## Gotchas
- Texture files with spaces (e.g., "old wood 24.png") are automatically renamed to "old_wood_24.png" during import
- Effect card textures (names starting with "textures_effects_") are treated as hidden materials
- `remaster_materials` module is fallback to legacy material system when unavailable
- Normal map (`_n`) and roughness/metallic/ao (`_rmaos`) textures require explicit sRGB=false and compression settings

Source: read, not executed.
