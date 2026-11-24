## Purpose
Manages the entire Tamriel world (open world of Skyrim) as instanced mesh actors for objects, terrain, and water in the Unreal editor. Loads objects from area2/tamriel/*.json (forts, castles, villages, etc.), terrain from area2/tamriel/terrain_low.txt (low-res atlas) and area2/tamriel/water_quads.csv (water strips), and handles city-worldspace visibility.

## How it is run
Called by `live_bridge.tick` from `unreal/SkyBridge/live_bridge.py`. The global `tick(live)` function initializes a `Tamriel` instance on first call (if models.json exists and camera is present), then updates the layer every frame via `Tamriel.tick()`.

## Inputs
- `live` object (from live_bridge) with `cam_sky`, `mesh`, `mesh_cache` attributes
- Configuration files: `area2/tamriel/models.json`, `area2/tamriel/city_cells.json`, `area2/tamriel/terrain_low.txt`, `area2/tamriel/water_quads.csv`
- `area2/debug_flags.txt` with 'notamriel' flag (disables layer)

## Outputs
- Unreal actors in "SkyBridge/Tamriel" (objects), "SkyBridge/TamrielTerrain" (terrain), "SkyBridge/Water" (water)
- Updated `area2/models.json` and `area2/requests.txt`
- Written to `area2/terrain_requests.txt`
- Reads `area2/ready.txt` and `area2/failed.txt` for asset conversion status

## Key functions
tick(live) - Entry point called by live_bridge
Tamriel.__init__(live) - Initializes model/terrain data
build_some(cam) - Spawns objects from model groups
feed(cam) - Requests new models for conversion
terrain_step(cam) - Handles terrain layers
chunk_step(cam) - Processes terrain chunks
spawn_water() - Creates water strip actor
instanced_actor(m, label, folder) - Builds instanced mesh
cull_for(nif) - Returns cull distance per model
far_material() - Builds M_TerrainFar material

## Depends on
live_bridge (for lb.AREA, lb.U, lb.V), unreal (Unreal API), remaster_materials (material building), `area2/tamriel/*.json`, `area2/tamriel/water_quads.csv`, `area2/tamriel/terrain_low.txt`

## Gotchas
- The 'notamriel' flag in area2/debug_flags.txt disables the layer (requires editor restart to re-enable)
- City worldspaces (Whiterun, Solitude, Windhelm, Markarth, Riften) hide the Tamriel layer while inside
- Water strips are defined by area2/tamriel/water_quads.csv
- Terrain uses two layers: low-res (M_TerrainFar, 128px/cell atlas) and full-res (1024px/cell chunks) that hides low-res in its area
- Updates area2/models.json and area2/requests.txt during operation

Source: read, not executed.
