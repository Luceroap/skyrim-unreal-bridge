## Purpose
This script processes Skyrim's grass data for the Unreal remaster, converting LTEX (grass layer textures) and GRAS (grass models) data into a format suitable for Unreal Engine. It handles grass placement rules including density, slope, water interaction, and positioning based on Skyrim's terrain.

## How it is run
Command line: `python tools/grass_placement.py [--world tamriel|whiterunworld|all] [--center 23000 -6000] [--radius 14000] [--spacing 35] [--seed 1] [--vanilla] [--models] [--preview [x y]] [--stats]`

Called from `tools/make_local_queue.py` as a dependency in the build process, and documented in `COORDINATION.md` as part of the grass placement workflow.

## Inputs
- Skyrim's Data directory (`D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`)
- Skyrim .esm files (Skyrim.esm, Update.esm)
- Skyrim plugins in load order (from plugins.txt and Skyrim.ccc)
- Grass mod configuration (iMinGrassSize in .ini files)

## Outputs
- `area2/grass_place/<world>/models.json` (grass model metadata per cell)
- `area2/grass_place/<world>/[name].bin` (grass placement data)
- `area2/grass_place/obj/` (OBJ files for grass models)
- `area2/grass_place/tex/` (PNG textures)
- `area2/grass_place/fbx/` (FBX files for grass models)
- `area2/grass_place/preview_<world>.png` (grass preview image)

## Key functions
arg - Parse command line arguments
min_grass_size - Find iMinGrassSize from Skyrim .ini files
load_order - Determine Skyrim's load order
read_plugin - Parse Skyrim plugin data (LTEX/GRAS)
scatter_cell - Distribute grass instances within a terrain cell
place - Main grass placement function
convert_models - Convert NIF to OBJ/PNG
preview - Create grass preview image
main - Entry point function

## Depends on
tools/distant_world.py (subrecord iterator)
tools/grass_blender.py (Blender integration)
nif2obj.py (NIF processing)
Blender at D:\blender.exe
Skyrim's Data directory structure

## Gotchas
- Requires Skyrim installed at D:\SteamLibrary\...
- Depends on Blender being installed at D:\blender.exe
- Uses SKGR file format for grass placement data
- Requires specific Skyrim .esm files (Skyrim.esm, Update.esm)
- Assumes terrain cell size is 4096 units

Source: read, not executed.
