## Purpose
Full-resolution LAND terrain with blended landscape layers (tools/land_terrain.py -> area2/landterrain/), live in the editor. Uses 4 RGBA weight textures for dynamic layer blending, with height-aware blending and weather effects.

## How it is run
The file is run via the `spawn`, `tick`, `swap`, and `clear` functions. It is called from `tools/make_local_queue.py` (line 135), which adds it to the execution queue. The `tick` function is called incrementally from `live_bridge.tick` to place tiles one by one.

## Inputs
- `area2/landterrain/tiles.json` (tile metadata)
- `area2/landterrain/fbx/*.fbx` (terrain tile meshes)
- `area2/landterrain/tex/*.png` (color texture layers)
- `area2/landterrain/Weights/*.png` (weight texture layers)

## Outputs
- Actors with label "LandTerrain_*" in level, placed in folder "SkyBridge/LandTerrain"
- Material instances at `/Game/LandTerrain/MI_LT_<x>_<y>`
- Material at `/Game/LandTerrain/M_LandTerrain`
- Temporary actors for LOD terrain at `/Game/Area2/LandTerrainLOD`

## Key functions
spawn
tick
swap
clear
material
meta
instance
mesh

## Depends on
area2/landterrain/tiles.json
area2/landterrain/fbx/
area2/landterrain/tex/
area2/landterrain/Weights/
/Game/Area2/terrain
/Game/Area2/lodterrain
/Game/Area2Tex/MPC_Weather

## Gotchas
- The material wasn't compiled properly when enabled: showed grey checkerboard due to missing layer textures under `area2/landterrain/tex`
- Only 4 tiles were imported (tiles.json has 9 entries), and terrain was never finished
- Material requires specific textures that might be missing
- Old terrain assets at `/Game/Area2/terrain` must exist to be toggled with `swap`
- Only supports up to 16 layers per tile (4 RGBA textures)

Source: read, not executed.
