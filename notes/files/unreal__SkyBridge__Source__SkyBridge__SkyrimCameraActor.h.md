## Purpose
A Unreal Engine actor that synchronizes a camera's position, rotation, and lighting to match Skyrim's active game state by reading shared-memory packets each frame. Designed for real-time integration between Skyrim and Unreal scenes.

## How it is run
No command-line invocation; placed as a level actor in the Unreal editor. Called via inclusion in `SkyBridgeGameMode.cpp` (game mode initialization) and `SkyrimCameraActor.cpp` (actor implementation).

## Inputs
- Skyrim's shared-memory data packets (position, time, weather)
- Editor-configurable properties: `UnitsToCm` (1.4287f default), `LightIntensityScale` (400f default)
- Player starting position for demo world placement

## Outputs
- `Status` string (debug status)
- `GameHour`, `Weather`, `Cell` (current game time/weather/location)
- Camera position/rotation synced to Skyrim
- Directional lights (`Sun`/`Moon`) and fog (`Fog`) updated for lighting

## Key functions
BeginPlay
Tick
EndPlay
UpdateSky
SpawnDemoWorld
UnitsToCm (property)
LightIntensityScale (property)
Status (property)
GameHour (property)
Weather (property)
Cell (property)

## Depends on
CoreMinimal.h
GameFramework/Actor.h
Camera/CameraComponent.h

## Gotchas
- Raw `void*` pointers (`MapHandle`, `View`) initialized to `nullptr` but not validated during use
- `SpawnDemoWorld` places demo meshes only (not accurate Whiterun layout)
- `LightIntensityScale` requires manual tuning against Skyrim lighting

Source: read, not executed.
