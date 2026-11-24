## Purpose
Generates Skyrim landscape grass data from in-game records (LTEX and GRAS), processing terrain heightmaps and texture blends to simulate realistic grass placement. Outputs to area2/grass/ for use in Unreal integration.

## How it is run
Command-line: `python tools/grass_world.py [--world tamriel] [--radius 14000] [...]`. Called by `unreal/SkyBridge/grass_live.py` and referenced in COORDINATION.md for grass placement workflows.

## Inputs
- Skyrim game data directory (`D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`)
- Active plugin load order from `plugins.txt`
- Terrain heightmaps (`LAND` records)
- Grass density/position rules (`GRAS` records)
- Land texture blend data (`LTEX`, `BTXT`, `VTXT`)

## Outputs
- `area2/grass/index.json`: Metadata and model list
- `area2/grass/cell_<gx>_<gy>.json`: Per-cell grass positions (x, y, z, rotation, scale)
- Queued model requests in `area2/requests.txt` for conversion

## Key functions
scatter_cell - Generates grass points per cell using heightmap blending  
read_plugin - Parses LTEX/GRAS/CELL data from plugins  
main - Orchestrates data collection and output  
mesh_sources - Resolves NIF file locations in meshes/  
queue - Enqueues unconverted models for processing  

## Depends on
- `bsa.py` (for BSA archive parsing)
- `build_area.py` (for asset conversion workflow)
- `tools/grass_live.py` (for Unreal integration)
- `area2/models.json` (model path mapping)

## Gotchas
- Uses LAND heightmap data, requiring terrain data from Skyrim.esm/Update.esm  
- Default spacing (48) is higher than Skyrim's game default (20)  
- Active plugins (from plugins.txt) are used by default; `--vanilla` skips mods  
- Missing grass models are queued in `area2/requests.txt` for conversion  
- Per-cell limit capped at 12000 grass instances (MAX_PER_CELL)  

Source: read, not executed.
