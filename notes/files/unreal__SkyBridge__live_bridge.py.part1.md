## Purpose
This is part 1 of 2 for the `live_bridge.py` script, which runs inside the Unreal editor to mirror Skyrim's world into the editor environment. It reads shared-memory streams for camera and world data, mirrors Skyrim's camera, objects, lights, time, and weather, and handles asset requests for missing models.

## How it is run
Run via: `UnrealEditor.exe SkyBridge.uproject -ExecutePythonScript=live_bridge.py`. This is called by the Unreal Editor directly; no other files explicitly run it. The script is triggered during the editor's startup process when the project is loaded.

## Inputs
- Shared memory streams from Skyrim plugin (camera and world streams)
- `area2/requests.txt` (for missing models)
- `area2/ready.txt` (for imported models)
- `area2/large_preview.json` (for previewing large assets)
- `area2/water_wide.csv` (for cell water placement)
- Shared memory for weather data

## Outputs
- Updates to Unreal editor scene (camera, actors, lighting)
- Writes to `area2/requests.txt` (when missing models are detected)
- Writes to `area2/models.json` (mapping asset names to paths)
- Writes to `area2/ready.txt` (when models are ready for import)
- Creates actors in Unreal (static mesh actors, point lights, sky environment)

## Key functions
Live.__init__ - Initializes the Live class and environment
spawn - Spawns new actor in Unreal editor
build_environment - Sets up atmosphere, lighting, and sky systems
spawn_static_world - Spawns terrain and water
spawn_cell_water - Spawns cell-based water from Skyrim data
weather_setup - Configures weather parameters
update_sky - Updates sky, weather, and lighting
read_world - Reads world stream from shared memory
apply_world - Applies world stream data to Unreal
apply_lights - Updates light sources in the scene
import_ready - Imports models from area2/ready.txt
spawn_some - Spawns requested models

## Depends on
- `atmosphere.py` (for environmental rendering)
- `remaster_materials.py` (for material handling)
- `ue_assets.py` (for model import routines)
- `tools/asset_service.py` (for converting models)
- Unreal Engine Python API (unreal module)
- `area2/` directory (for asset request files)

## Gotchas
- Requires Skyrim's plugin to be running with shared memory streams
- Must be run from within the Unreal Editor (not standalone)
- Large asset requests can cause memory issues (up to 53GB reported)
- Spaces in asset names require special handling (area2/spaced_names_ok.txt)
- The script handles only exterior cells (interior cells hide sun, clouds, rain)

Source: read, not executed.
