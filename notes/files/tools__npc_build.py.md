## Purpose
Builds a single NPC (body and baked FaceGen head/hair/eyes/brows/beard) as a skinned FBX file for Unreal Engine. The output includes an armature + one mesh file and textures shared with the static pipeline.

## How it is run
Command line: `python -I tools/npc_build.py <base_npc_form_id_hex> <male|female>`
Other files that call it: `tools/npc_batch.py` (uses subprocess to call it with base ID, sex, optional --face, --slots, and gear paths).

## Inputs
- Base NPC form ID (8-digit hex string, e.g., "00012345")
- Sex ("male" or "female")
- Optional flags: 
  `--face=<form_id_hex>` (uses baked head from specified NPC)
  `--slots=<hex_mask>` (worn biped slots bitmask, e.g., 0x1 for head)
- Gear paths (relative to meshes/, e.g., "meshes/armor.nif")

## Outputs
- File: `area2/npc/export/npc_<base_id>.fbx` (armature + one mesh)
- File: `area2/npc/obj/npc_<id>.mtl` (material file)
- Textures in `area2/tex` (shared with static pipeline)
- Intermediate JSONs in `area2/npc/skin/` (e.g., `face_<id>.json`, `gear_<id>_*.json`)

## Key functions
run: subprocess wrapper

## Depends on
tools/npc_extract.py
tools/npc_skin.py
tools/textures.py
tools/textures_pbr.py
tools/npc_blender.py

## Gotchas
- Helmets (worn head/hair slot) trigger removal of hair shapes from FaceGen JSON
- `--face` flag requires 8-digit hex ID; defaults to base ID if omitted
- Armor texture overrides in `area2/npc/swaps_<base_id>.json` apply to gear JSONs
- Texture paths normalized to "textures\" prefix
- Skyrim Data path hardcoded as `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`

Source: read, not executed.
