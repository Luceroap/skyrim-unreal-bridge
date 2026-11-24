## Purpose
This class bridges Skyrim's camera data to Unreal Engine, synchronizing the camera position, rotation, and game time. It spawns a demo world from Skyrim data (static meshes, lights, water) and updates the sky/weather system based on in-game conditions.

## How it is run
Command line: `-SkyBridgeCam=x,y,z,yawDeg,pitchDeg[,hour]` (semicolon-separated values, not commas). Called automatically by Unreal Engine's `Tick()` when Skyrim is running, and via the `BeginPlay()` override to set the player's view target. Other files: Referenced in `README.md` and called by `SpawnDemoWorld()` from `Tick()`.

## Inputs
- `area2/placements.csv` (static mesh positions/rotations from Skyrim)
- `area2/lights.tsv` (light positions/colors from Skyrim)
- `area2/water.csv` (water heights from Skyrim)
- Shared memory (`SkyBridge::kMappingName`) for real-time camera data from Skyrim

## Outputs
- Spawned static mesh actors (via `SpawnActor`), lights, and water planes in Unreal
- `area2/ue_actors.csv` (generated bounding box data for validation)
- Debug logs (`LogTemp` entries for placement/sun updates)

## Key functions
BeginPlay - Sets player view target to this actor
EndPlay - Cleans up shared memory mappings
SpawnDemoWorld - Generates full demo world from CSVs
UpdateSky - Adjusts sun/moon intensity based on weather
Tick - Main loop for camera/data sync

## Depends on
`BridgeShared.h` (shared memory struct)
`area2/placements.csv` (data source)
`area2/lights.tsv` (data source)
`area2/water.csv` (data source)

## Gotchas
- Rotation math swaps X/Y axes and applies matrix corrections for Blender import
- Shared memory uses 4-try seqlock to avoid race conditions during read
- Command line uses semicolon separators (`;`) not commas for arguments
- Water meshes use hardcoded 4096-unit cell size (from Skyrim grid)
- Demo world spawn requires `placements.csv` row "terrain" to exist

Source: read, not executed.
