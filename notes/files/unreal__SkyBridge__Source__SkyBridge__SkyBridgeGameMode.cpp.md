## Purpose
ASkyBridgeGameMode configures the Unreal Engine game session for the Skyrim-Unreal bridge, spawning a camera actor at world origin and optionally visualizing a debug grid. The debug grid is disabled by default to avoid visual clutter with real terrain.

## How it is run
Invoked automatically by Unreal Engine during gameplay initialization via `BeginPlay()`. The only reference to this file in other project files is in README.md (line 90), which notes the debug grid is off.

## Inputs
Hardcoded debug flag `bDrawDebugGrid = false`; no external inputs.

## Outputs
Spawns `ASkyrimCameraActor` at world origin (0,0,0) and draws debug grid lines in-game (currently inactive due to disabled flag).

## Key functions
ASkyBridgeGameMode() - Constructor setting DefaultPawnClass to nullptr.  
BeginPlay() - Spawns camera and draws debug grid.  
DrawDebugLine() - Visualizes grid lines with color coding.

## Depends on
SkyrimCameraActor.h, DrawDebugHelpers.h, World.h, Pawn.h.

## Gotchas
- Debug grid disabled by default (bDrawDebugGrid = false).  
- Camera spawned at world origin (0,0,0).  
- Debug grid code present but inactive due to hardcoded false.  
- Comment states grid is off to avoid clutter with real terrain.  
- README.md (line 90) references the debug grid setting.

Source: read, not executed.
