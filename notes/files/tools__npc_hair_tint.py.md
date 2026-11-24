## Purpose
This script processes Skyrim NPC face NIF files to extract hair tint color data, converting it into a format usable by Unreal Engine. It stores the hair color information as RGB values multiplied by Skyrim's grey texture system.

## How it is run
Execute `python npc_hair_tint.py` to generate `area2/npc/hair_tint.json` from all face NIF files. Use `--dump <face.nif>` for single-file debug output. Called by `unreal/SkyBridge/npc_live.py` (line 216) and referenced in `unreal/SkyBridge/remaster_materials.py` (line 665).

## Inputs
- Skyrim NIF files in `area2/npc/nif/actors/character/facegendata/facegeom/` (8-character hex names like `00000001.nif`)
- Optional `--dump` argument with a specific NIF path

## Outputs
- `area2/npc/hair_tint.json` (sorted JSON file with structure: `{face_form_id: {texture_path: [r, g, b]}}`)
- Progress output: `X faces with hair tint`

## Key functions
shader_info - Extracts shader properties from NIF data  
tints - Processes NIF file and returns hair tint data  
__main__ - Entry point for main execution

## Depends on
tools/nif2obj.py (imports R, parse, avobject)

## Gotchas
- Only processes BSLightingShaderProperty shaders of type 6 (HairTint)
- Normalizes texture paths to lowercase with backslashes (e.g., `textures\hair\red.nif`)
- Converts RGB values to [0.0, 1.0] range with 4 decimal precision
- Skips problematic files (prints "FAILED" but continues processing)
- Outputs sorted JSON (sort_keys=True in json.dump)

Source: read, not executed.
