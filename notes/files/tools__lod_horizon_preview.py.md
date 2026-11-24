## Purpose
Generates horizon preview images from Whiterun toward cardinal directions (N/E/S/W) to verify terrain and object LOD rendering. Uses Blender to render terrain (lodterrain.obj + terrain.obj) with water (lodwater.obj) and object/tree LOD from the objlod system.

## How it is run
Command: `python tools/lod_horizon_preview.py [--views N,E,S,W] [--res 1600x640] [...]`  
Other files that call it: `COORDINATION.md` (line 234) references it as producing `area2/lodpreview/*.png`.

## Inputs
- Project directories: `area2/lod_obj`, `area2/terrain_obj`, `area2/lodwater_obj`, `area2/lodobj`
- Command-line arguments: `--views`, `--res`, `--fov`, `--tex`, `--height`, `--pitch`, `--min-commit`
- Precomputed files: `lodterrain.obj`, `terrain.obj`, `lodwater.obj`, `manifest.json`, `trees.json`

## Outputs
- `area2/lodpreview/<view>.png`: Full render with terrain, objects, and trees (e.g., `N.png`)
- `area2/lodpreview/<view>_terrain.png`: Terrain-only render for comparison (e.g., `N_terrain.png`)

## Key functions
free_commit_gb - Checks Windows commit memory (GB) via kernel API.  
in_wedge - Checks if point (x,y) is within view wedge.  
box_in_wedge - Checks if bounding box is within view wedge.  
ground_z - Finds highest terrain vertex near Whiterun.  
small_tex - Resizes textures to avoid memory bloat.  
prepare - Builds JSON job file for Blender.  
run_outside - Main CLI entry point.  
tex_material - Creates Blender material from texture.  
run_inside - Executes Blender rendering pipeline.

## Depends on
`area2/lod_obj/lodterrain.obj`, `area2/terrain_obj/terrain.obj`, `area2/lodwater_obj/lodwater.obj`, `area2/lodobj/manifest.json`, `area2/lodobj/trees.json`, `argparse`, `PIL.Image`, `blender.exe` (hardcoded path).

## Gotchas
- Hardcoded Blender path `D:\blender.exe` (Windows only).
- Waits for 1.5 GB free commit memory before rendering.
- Requires `manifest.json` for object LOD to render; skips objects if missing.
- Requires `trees.json` for tree LOD; omits trees if missing.
- Outputs terrain height relative to Whiterun’s terrain peak (computed via `ground_z`).

Source: read, not executed.
