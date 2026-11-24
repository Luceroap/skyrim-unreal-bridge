## Purpose
This script processes terrain data for a Skyrim to Unreal bridge project, converting terrain tiles and LOD (Level of Detail) models to FBX format for use in Unreal Engine. It handles both exported tile data and generates visual previews of terrain regions with water and texture mapping.

## How it is run
Command line:
```
blender -b --factory-startup -P tools/land_textures_blender.py -- export <tile.npz ...>
blender -b --factory-startup -P tools/land_textures_blender.py -- lod <lodterrain_trim.obj> <out_dir>
blender -b --factory-startup -P tools/land_textures_blender.py -- preview <out.png> <view> <variant>
```
Called by `tools/land_textures.py` (as confirmed by `git grep` output).

## Inputs
- Terrain tile data: `.npz` files in `area2/landtex/tiles/`
- LOD terrain models: `lodterrain_trim.obj` (trimmed) or `lodterrain.obj` (original) in `area2/landtex/lod/` or `area2/lod_obj/`
- Texture data: `area2/tex/terrain_tile_*` PNGs
- Preview thumbnails: `area2/landtex/preview_old/` (old method) or `area2/landtex/preview/` (new method)
- Terrain metadata: `area2/landtex/tiles.json` and `area2/landtex/cells.json`
- Water geometry: `area2/water_quads.csv`

## Outputs
- FBX files: `area2/landtex/fbx/` (export mode)
- FBX files: Specified output directory (lod mode)
- Preview image: User-specified PNG path (preview mode)

## Key functions
mesh_from_npz - Converts terrain npz data to Blender mesh with UVs and materials.
material - Creates Blender material with texture or color.
export - Exports terrain tiles (npz) to FBX.
lod - Exports LOD terrain OBJ to FBX.
lod_region - Extracts LOD region meshes from terrain data.
water_region - Generates water mesh from water_quads.csv.
old_tiles - Creates terrain tiles for old preview method.
preview - Generates terrain region preview image.

## Depends on
- Blender Python API (`bpy`)
- Python modules: `glob`, `json`, `math`, `os`, `sys`, `numpy`
- Project files: `area2/landtex/` (all subdirectories), `area2/tex/`, `area2/lod_obj/`, `area2/water_quads.csv`

## Gotchas
- Uses fixed scale factor (0.014287) for Skyrim-to-meters conversion
- "old" preview variant uses textures from `area2/landtex/preview_old/`
- "new" preview variant uses textures from `area2/landtex/preview/`
- Water regions processed from `area2/water_quads.csv`
- Requires Blender version with full Python API support

Source: read, not executed.
