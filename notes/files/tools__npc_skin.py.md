## Purpose
Extracts skeleton rest poses and skinned mesh data from Skyrim NIF files for Unreal Engine NPC rendering. Outputs JSON files containing vertex positions, UVs, bone weights, and texture references aligned with Unreal's requirements.

## How it is run
Command-line: `python -I npc_skin.py skeleton <skeleton.nif> <out.json>` or `python -I npc_skin.py mesh <body.nif> <out.json>`. Called by `tools/npc_build.py`, `tools/npc_build_creature.py`, `tools/npc_blender.py`, `tools/npc_batch.py`, and `tools/npc_autobuild.py`.

## Inputs
NIF files (skeleton or mesh), optional skeleton JSON path for mesh mode (defaults to `skeleton_male.json` if omitted).

## Outputs
JSON files containing skeleton rest poses (`skeleton.nif` output) or mesh vertex data (`body.nif` output), including bones, weights, UVs, and texture paths.

## Key functions
skeleton
meshes
tex_of
name_of
to_skeleton

## Depends on
nif2obj.py

## Gotchas
- CREATURE mode (via `--creature`) ignores bone offsets, keeping vertices in shape space.
- Mesh mode defaults to `skeleton_male.json` if skeleton path not specified.
- Skips meshes without skin attributes (checks `has_skin`).
- Skips textures from non-"Lighting" shaders (e.g., emissive properties).
- Uses row-major NIF rotation matrices directly (no conversion).

Source: read, not executed.
