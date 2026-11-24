## Purpose
This script processes Skyrim's object LOD data (buildings and trees) to generate optimized assets for Unreal Engine. It skips objects already represented in the distant layer (mountains, cliffs, rocks, trees) or within detailed terrain cells, producing OBJ/MTL files, textures, and metadata.

## How it is run
Command line: `python tools/lod_objects.py [--radius 700000] [--l4 60000] [--l8 150000] [--texmax 2048] [--no-blender] [--trees-only | --objects-only] [--keep-near]`  
Called by: Build system (documented in `COORDINATION.md` as part of "objlod" step), with `unreal/SkyBridge/lod_objects_live.py` as a related but separate file.

## Inputs
- Skyrim Data folder: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`
- Object data: `meshes\terrain\tamriel\objects\tamriel.<lvl>.<x>.<y>.bto`
- Tree data: `meshes\terrain\tamriel\trees\tamriel.lst`, `meshes\terrain\tamriel\trees\tamriel.4.<x>.<y>.btt`
- Terrain cells: `area2/terrain_obj/terrain.obj`
- Distant references: `area2/distant_refs.json`
- Masked textures: `area2/tex/alpha_masked.txt`, `area2/tex/alpha_masked_extra.txt`

## Outputs
- `area2/lodobj/obj/` (OBJ/MTL files per block: `lodobj_<lvl>_<x>_<y>.obj/mtl`, `lodtree_card.obj`)
- `area2/lodobj/export/` (FBX files via `blender_export.py`)
- `area2/lodobj/tex/` (PNG textures derived from DDS)
- `area2/lodobj/manifest.json` (block metadata)
- `area2/lodobj/trees.json` (tree atlas and instances)

## Key functions
arc
read_data
list_lod
choose_blocks
convert_objects
convert_trees
write_card
main
dds_to_png
make_texture
distant_refs
near_cells

## Depends on
- `bsa.py` (BSA archive reader)
- `nif2obj.py` (NIF mesh extractor)
- `blender_export.py` (FBX generation)

## Gotchas
- Hardcoded Skyrim Data path `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`
- Skips objects in detailed terrain cells (area2/terrain_obj/terrain.obj) unless `--keep-near`
- Skips trees drawn in distant layer (via `distant_refs.json` for tree kind)
- Uses fixed Whiterun center (23000.0, -6000.0) for distance calculations

Source: read, not executed.
