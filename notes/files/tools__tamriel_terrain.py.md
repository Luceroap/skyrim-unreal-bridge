## Purpose
Generates terrain and water for the entire Tamriel map (Skyrim) from Skyrim's LAND records, creating both low-resolution group meshes (for distant viewing) and high-resolution chunks (for close-up). It processes exact elevation data, texture layers, and vertex colors, skipping Whiterun's hand-baked terrain.

## How it is run
Command line:  
- `python tools/tamriel_terrain.py --land` → parses LAND records to `area2/tamriel/land.pkl`  
- `python tools/tamriel_terrain.py --low` → builds all low-res groups + atlases + water to `area2/export`  
- `python tools/tamriel_terrain.py --chunk cx cy` → builds one full-res terrain chunk  
- `python tools/tamriel_terrain.py --serve` → background service for terrain requests  

Other files calling it:  
- `demo.py` (line 28: `--serve`)  
- `play.py` (line 44: `--serve`)  
- `tools/make_local_queue.py` (line 138: includes the file)  
- `unreal/SkyBridge/tamriel_live.py` (line 10: references service)

## Inputs
- Skyrim LAND records (via `tamriel_world.scan`)  
- Landscape textures from `DATA/Skyrim - Textures*.bsa` archives  
- `area2/terrain_obj/terrain.obj` (to skip Whiterun's cells)  
- Water data from `area2/water_wide.csv` (Whiterun)  

## Outputs
- **Files**:  
  - `area2/tamriel/land.pkl` (parsed LAND data)  
  - `area2/export/tlo_*_*.obj` (low-res group meshes)  
  - `area2/tex/tatl_*_*.png` (low-res texture atlases)  
  - `area2/chunk_obj/tch_*_*.obj` (full-res chunk meshes)  
  - `area2/tex/tdet_*_*.png` (full-res chunk textures)  
  - `area2/water_quads.csv` (water strip data)  
  - `area2/tamriel/terrain_requests.txt` (service input)  
  - `area2/tamriel/terrain_ready.txt` (service output)  
- **Folder**: `area2/export` (low-res assets)  

## Key functions
- `parse_land`: Saves parsed LAND records to `land.pkl`  
- `build_low`: Generates low-res terrain groups and atlases  
- `build_water`: Creates water strips excluding Whiterun  
- `build_chunk`: Generates one high-res terrain chunk (4x4 cells)  
- `serve`: Background service for editor terrain requests  
- `Heights`: Handles terrain height/normal queries with skipping  
- `Baker`: Bakes landscape textures with brightness correction  
- `emit_cells`: Creates mesh grid with skirt seams  

## Depends on
- `tamriel_world.py` (LAND record scanning)  
- `bsa.py` (texture BSA archive parsing)  
- `blender.exe` (D:\blender.exe for OBJ→FBX export)  
- Game data: `DATA` (texture archives), `area2/terrain_obj/terrain.obj`  

## Gotchas
- Whiterun's hand-baked terrain (`area2/terrain_obj/terrain.obj`) is skipped entirely in all outputs.
- Low-res groups (tlo) use 16x16 cells (128px/cell atlas), high-res chunks (tch) use 4x4 cells (1024px/cell texture).
- Water strips are generated as 128-unit segments (length) except full cells (4096-unit).
- `--serve` mode reads requests from `area2/tamriel/terrain_requests.txt` and writes to `terrain_ready.txt`.
- The service processes up to 6 chunks per cycle to avoid editor blocking.

Source: read, not executed.
