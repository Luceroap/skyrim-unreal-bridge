## Purpose
Processes Skyrim-derived OBJ files (Z-up coordinate system) by scaling Skyrim units to meters (1 unit = 1.4287 cm) and exports FBX files. Joins multiple mesh objects per building into a single mesh while preserving material slots.

## How it is run
Command line: `D:\blender.exe -b -P blender_export.py -- <obj_dir> <out_dir>`.  
Other files calling it: `tools/asset_service.py` (line 48), `tools/auto_build.py` (line 54), `tools/lod_objects.py` (lines 13, 418), `tools/lod_terrain.py` (line 6), `tools/tamriel_terrain.py` (line 276).

## Inputs
- `obj_dir`: Directory containing Skyrim-derived OBJ files (Z up).
- `out_dir`: Output directory for FBX files.
- `FORCE` environment variable (optional): Forces re-export even if file exists.

## Outputs
- FBX files (`.fbx`) in `out_dir` named after input OBJ base names (e.g., `whiterun.fbx`).
- Console output: `EXPORTED <name> <number> objects <number> verts` per file.

## Key functions
obj_import  
transform_apply  
join  
export_fbx  
scale_meshes  

## Depends on
Blender Python API (bpy), sys, os, glob (standard libraries).

## Gotchas
- Skips files if output `.fbx` exists and `FORCE` not set (incremental export).
- Scale factor is hardcoded as `0.014287` (1 Skyrim unit = 1.4287 cm).
- Only exports FBX (GLB not implemented despite docstring claim).
- Joins meshes only if multiple per building (preserves material slots).
- Sets export axis_forward `-Y`, axis_up `Z` to match Skyrim coordinate system.

Source: read, not executed.
