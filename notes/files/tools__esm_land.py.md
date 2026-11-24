## Purpose
Extracts terrain heightmaps (LAND records) from a Skyrim ESM file, processes tiles within a specified radius of a point, and outputs a textured OBJ file for use in Unreal Engine. Processes only LAND data matching the target worldspace.

## How it is run
Command: `python -I tools/esm_land.py <esm> <out.obj> <worldspace edid> <cx> <cy> <radius>`
Called by `tools/auto_build.py` (line 53) as: `run([PY, "-I", "tools/esm_land.py", "Skyrim.esm", "terrain.obj", "whiterunworld", "23000", "-6000", "14000"])`

## Inputs
- Skyrim ESM file path (e.g., `Skyrim.esm`)
- Output OBJ path (e.g., `area/terrain_obj/terrain.obj`)
- Worldspace EDID (case-insensitive, e.g., `whiterunworld`)
- Center X coordinate (`cx`)
- Center Y coordinate (`cy`)
- Radius (in ESM coordinate units)

## Outputs
- OBJ file containing terrain vertices, texture coordinates, and faces
- Example output: `area/terrain_obj/terrain.obj` (used by `unreal/SkyBridge/import_terrain.py`)

## Key functions
subs: Parses sub-blocks within ESM data structures
walk: Recursively traverses ESM group hierarchies (WRLD/CELL/LAND)
process_land_tiles: Filters and processes LAND tiles within radius
compute_heights: Converts compressed height data to 3D coordinates
write_obj: Generates OBJ file with vertices and faces

## Depends on
- Standard libraries: `struct`, `sys`, `zlib`, `math`
- Called by: `tools/auto_build.py`
- Input ESM file must contain valid LAND records

## Gotchas
- Uses hardcoded flat-brown RGB (0.5, 0.45, 0.35) when LAND color data is missing
- Decompresses LAND data via zlib if flags & 0x40000 is set
- Processes only LAND tiles within specified radius of (cx, cy)
- Case-insensitive worldspace EDID matching (input and file data converted to lowercase)
- Fixed 33x33 tile size per LAND record

Source: read, not executed.
