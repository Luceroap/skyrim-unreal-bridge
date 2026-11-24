## Purpose
Extracts geometry from Skyrim SE NIF files (version 20.2.0.7, BS stream 100) into Wavefront OBJ format, preserving node transforms and basic material references. Handles BSTriShape meshes while ignoring skinned/animated data by default.

## How it is run
Command line: `python -I nif2obj.py in.nif out.obj`. Called by `grass_placement.py` (line 24), `make_local_queue.py` (lines 80, 137), `README.md` (line 55), and referenced in `COORDINATION.md` (line 13).

## Inputs
Binary Skyrim SE NIF file (version 20.2.0.7, BS stream ≥83) with NiNode hierarchy and BSTriShape geometry.

## Outputs
- OBJ file containing vertices, UVs, triangles, and object names.
- MTL file with material definitions referencing texture names (e.g., `# skyrim diffuse: texture.png`).
- Default grey material (Kd 0.8 0.8 0.8) if no texture is found.

## Key functions
parse
extract
write_obj
_skinned_as_static
avobject
mat_mul
xform

## Depends on
tools/npc_skin.py (for fallback handling of skinned models), other project files via `git grep` references.

## Gotchas
- Skinned/animated geometry ignored by default; only processed via `_skinned_as_static` if `npc_skin.py` exists.
- UV coordinates flipped vertically (u, 1.0 - v) during output.
- Requires NIF BS stream ≥83; older versions fail validation.
- Uses default grey material in MTL if texture path is missing.
- Relies on `npc_skin.py` for skinned model fallback (fails silently if missing).

Source: read, not executed.
