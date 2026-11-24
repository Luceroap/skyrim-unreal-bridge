## Purpose
Converts Skyrim's distant terrain LOD (mountains) from BSA archive meshes and textures into a Blender-compatible OBJ format. Drops triangles over areas already covered by detailed terrain and sinks the LOD by 60 units to hide seams under detailed terrain.

## How it is run
Command: `python tools/lod_terrain.py`  
Called by: `start_bridge.py`, `demo.py` (via `COORDINATION.md`), `tools/land_terrain.py` (line 472), `tools/lod_objects.py`, and referenced in `README.md`/`HANDOFF_FOR_CURSOR.md`.

## Inputs
- Skyrim BSA archives: `Skyrim - Meshes1.bsa`, `Skyrim - Textures7.bsa`  
- Detailed terrain cell data: `area2/terrain_obj/terrain.obj`  
- Skyrim path: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data` (hardcoded)  
- Center point: `(23000.0, -6000.0)` (Whiterun area, same as detailed terrain)

## Outputs
- `area2/lod_obj/lodterrain.obj` (mesh), `lodterrain.mtl` (material)  
- `area2/tex/lodtex_<lvl>_<x>_<y>.png` (textures)  
- `area2/lodwater_obj/lodwater.obj` (water layer)  
- Triggers `blender_export.py area2/lod_obj area2/export` for Unreal import

## Key functions
read_tex - Fetch texture from BSA or loose path  
process_tiles - Iterate over terrain LOD tiles  
write_obj - Generate OBJ file with UV coordinates  
convert_texture - Convert DDS to PNG (handle DX10)  
exclude_near_cells - Skip triangles over detailed terrain cells

## Depends on
- `bsa.py` (BSP archive reader)  
- `nif2obj.py` (NIF mesh parser)  
- `PIL.Image` (DDS texture conversion)  
- `area2/terrain_obj/terrain.obj` (input cell coverage data)

## Gotchas
- Sinks LOD terrain by 60.0 units (`SINK = 60.0`) to hide seams  
- Excludes triangles from tiles closer than 110,000 units to Whiterun (`NEAR_L8 = 110000.0`)  
- Texture conversion handles DX10 DDS headers (adjusts format)  
- Resizes textures to max 1024x1024 (`TEXMAX = 1024`)  
- Processes water layer as separate mesh (`lodwater.obj`) from terrain tiles

Source: read, not executed.
