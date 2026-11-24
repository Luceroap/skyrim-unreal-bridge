## Purpose
Builds skinned FBX models for creatures (wolves, dragons, draugr, etc.) from Skyrim race skeletons and body-skin meshes. Outputs Unreal Engine-compatible FBX files and skeleton JSON configurations.

## How it is run
Command line: `python -I npc_build_creature.py <actor base form id hex> <skeleton nif> <body skin addon nif> [more nifs...]`. Called by `npc_batch.py` (line 75) and referenced in `COORDINATION.md`.

## Inputs
- Actor base form ID (hex, 8 digits, e.g., `00012345`)
- Skeleton NIF path (relative to `meshes/`)
- Body skin addon NIF paths (e.g., `meshes/cow_body.nif`)
- `area2/npc/swaps_<id>.json` (texture overrides from `npc_batch.py`)

## Outputs
- `area2/npc/export/npc_<id>.fbx` (Unreal-compatible FBX)
- `area2/npc/skin/skeleton_<key>.json` (key = skeleton path with non-alphanumeric → `_`)
- `area2/npc/obj/npc_<id>.mtl` (texture mapping definitions)

## Key functions
Extract skeleton and body meshes  
Skinned meshes conversion  
Rest pose binding patch  
Texture override application  
Blender FBX export  

## Depends on
- Tools: `npc_extract.py`, `npc_skin.py`, `textures.py`, `textures_pbr.py`, `npc_blender.py`
- Input files: `Data/meshes/` (Skyrim NIFs), `area2/npc/swaps_<id>.json`
- Environment: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`

## Gotchas
- Skeleton NIF must exist; missing file causes immediate exit (line 26).
- Mesh NIFs must exist; missing ones skipped but cause exit if no valid meshes remain.
- Rest pose must be patched to match the bind pose for correct Unreal animation.
- Texture paths must start with `textures\` (otherwise prepended).
- Output paths use ID from actor base form (e.g., `npc_00012345.fbx`).

Source: read, not executed.
