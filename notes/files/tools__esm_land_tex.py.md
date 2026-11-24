## Purpose
Processes Skyrim's ESM terrain data (LAND heightmaps and texture layers) to generate Unreal Engine-compatible terrain assets. Bakes albedo textures per terrain tile and creates an OBJ with UV-mapped materials for each tile.

## How it is run
Command: `python -I esm_land_tex.py <Data dir> <esm> <area dir> <worldspace edid> <cx> <cy> <radius> [bake_px=4096]`  
Called by `tools/land_textures_blender.py` (line 154) and referenced by `tools/tamriel_terrain.py` (line 37).

## Inputs
- `data_dir`: Skyrim data directory path
- `esm`: Skyrim ESM file path
- `area`: Output directory for terrain assets
- `worldspace edid`: Comma-separated worldspace EDIDs (priority order)
- `cx`, `cy`: Center coordinates (world units)
- `radius`: Search radius (world units)
- `bake_px`: Optional texture bake size (default 4096)

## Outputs
- Files: `area/tex/terrain_tile_*_*.png` (albedo textures)
- Files: `area/terrain_obj/terrain.obj` (geometry)
- Files: `area/terrain_obj/terrain.mtl` (material definitions)

## Key functions
subs - Parses ESM data chunks into (type, data) pairs
walk - Traverses ESM records to collect terrain data
tex_image - Loads texture from BSA/data_dir, handles DX10 format
tiled - Tiles texture to match landscape repeat units

## Depends on
`tools/bsa.py` (Bsa class), `PIL.Image` (Python Imaging Library)

## Gotchas
- Default texture `textures\landscape\dirt02.dds` must exist in data_dir/BSA
- Processes only LAND records within circular radius (not square)
- Heightmaps are always 33x33 grid per terrain cell
- Worldspace EDID lookup uses first match in comma-separated list
- Requires valid BTXT/ATXT/VTXT texture layers in ESM

Source: read, not executed.
