## Purpose
Bakes high-resolution landscape textures for Skyrim's terrain, resolving base textures (BTXT), alpha layers (ATXT), and vertex colors (VCLR) over water cells and surrounding terrain. It creates full-resolution textures and previews for Unreal Engine import, prioritizing smooth transitions between terrain materials.

## How it is run
Command line: `python tools/land_textures.py [--water-radius 64000] [--near 24000] [--ring 1] [--force] [--only 5,-1;6,-1] [--no-bake] [--no-fbx] [--no-lod] [--core-px 4096]`. Called by `tools/make_local_queue.py` (listed in its `to_run` array).

## Inputs
- `area2/terrain_obj/terrain.obj` (core terrain cells)
- `area2/water_wide.csv` (water cell coordinates)
- Skyrim Data folder (plugins, BSA archives, `Skyrim.esm`)
- Command line arguments (`--water-radius`, `--near`, etc.)
- `AREA` directory structure (e.g., `area2`)

## Outputs
- `area2/landtex/tex/` (baked textures: `LX_<gx>_<gy>.png`, `_n.png`, `_s.png`)
- `area2/landtex/preview/` (512px thumbnails: `LX_<gx>_<gy>.jpg`)
- `area2/landtex/layers/` (raw layer textures: `*.png`, `*_n.png`)
- `area2/landtex/tiles/` (`.npz` mesh data for Unreal)
- `area2/landtex/fbx/` (Blender-exported FBX tiles if `--no-fbx` omitted)
- `area2/landtex/lod/` (trimmed LOD terrain: `lodterrain_trim.obj`)
- `area2/landtex/cells.json`, `tiles.json`, `layers.json` (metadata)

## Key functions
arg: Parse command line arguments
load_order: Determine Skyrim load order
read_load_order: Parse plugin data (LTEX/TXST/LAND)
wanted_cells: Compute target cells from water data
cell_weights: Calculate texture weights per cell
stitch: Merge weights at cell edges
blend: Texture blending function
bake_cell: Bake single cell texture
write_tiles: Generate mesh tile data
trim_lod: Trim LOD terrain
Layers: Layer texture cache manager
TexSource: Texture archive source handler
parse_land: Parse LAND record data

## Depends on
tools/land_textures_blender.py (Blender script executor)

## Gotchas
- Hardcoded Skyrim installation path: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition`
- Hardcoded Blender path: `D:\blender.exe`
- Hardcoded Whiterun center: `(23000.0, -6000.0)`
- Requires `area2/terrain_obj/terrain.obj` and `area2/water_wide.csv` to exist
- Uses Windows-specific paths (non-portable)

Source: read, not executed.
