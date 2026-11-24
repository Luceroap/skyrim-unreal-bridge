## Purpose
This script generates a visual comparison of terrain texture baking results for Skyrim cells in the Whiterun area. It processes terrain data, compares new and old tile outputs, and produces a side-by-side image for debugging.

## How it is run
Executed directly via `python probe_bake.py` in the project root. No other files in the project call this script (verified by `git grep`).

## Inputs
- Terrain data loaded via `tamriel_terrain.load_land()`
- Existing terrain tiles (`C:\Users\Aidan\SkyrimUnrealBridge\area2\terrain_tile_x_y.png`)
- Whiterun cell data (hardcoded via `tt.whiterun_cells()`)

## Outputs
- Saves `prev_cmp.png` (1536x512 RGB image) to `area2\`:
  - Left: New baked cell (`b.cell(c, 512)`)
  - Middle: Modified bake (`b.cell(cv, 512)`)
  - Right: Original tile (`terrain_tile_x_y.png`)

## Key functions
- load_land: Loads terrain data structure
- Baker: Bakes cell layers into textures
- cell processing: Analyzes cell vertex colors and layers
- Image comparison: Combines three images into one output

## Depends on
- `tools/tamriel_terrain.py` (via `import tamriel_terrain as tt`)
- `PIL.Image` (Python Imaging Library)

## Gotchas
- Hardcoded Windows paths (C:\Users\Aidan\...)
- Processes Whiterun cells only (via `tt.whiterun_cells()`)
- Resizes original tiles to 512x512
- Requires existing `terrain_tile_x_y.png` files
- Generates output in `area2/prev_cmp.png` (overwrites existing)

Source: read, not executed.
