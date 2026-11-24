## Purpose
Generates full-resolution terrain for Tamriel using Skyrim's LAND records (VHGT, VNML, VCLR) and blends landscape textures (BTXT/ATXT/VTXT) into layered PNG textures. Replaces baked-tile terrain and covers water cells specified in water_wide.csv.

## How it is run
Command-line: `python tools/land_terrain.py [--radius 32768] [...]`. Called by `tools/make_local_queue.py` (listed in its dependency array) and invoked as part of terrain processing workflows.

## Inputs
- Skyrim.esm and Update.esm (LAND records)
- area2/water_wide.csv (water cell coordinates)
- area2/terrain_obj/terrain.obj (old baked terrain for reference)
- Command-line arguments (radius, center, tile size, etc.)

## Outputs
- area2/landterrain/tiles/*.npz (mesh vertex/normal data)
- area2/landterrain/tex/*.png (texture layers and normals)
- area2/landterrain/tiles.json (tile metadata)
- area2/landterrain/fbx/*.fbx (Blender exports, if --no-fbx not used)
- area2/landterrain/lod/landlod.obj (LOD terrain when --lod used)

## Key functions
parse_land - Converts LAND record to height/normals/colours.
cell_weights - Computes per-vertex texture blend weights.
convert_layer - Converts LTEX/TXST to PNG texture layers.
selected_cells - Determines cells within radius and water zones.
main - Orchestrates terrain processing pipeline.
blender_main - Exports meshes to FBX via Blender.
trim_lod - Creates LOD terrain without covered cells.

## Depends on
tools/bsa.py (for ESM file parsing)

## Gotchas
Hardcoded data path: `D:\SteamLibrary\...\Data`.
Hardcoded Blender path: `D:\blender.exe`.
Default texture for missing LTEX: `landscape\dirt02.dds`.
Uses `--no-tex` to skip texture conversion.
Requires `water_wide.csv` for water cell processing.

Source: read, not executed.
