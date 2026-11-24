## Purpose
This file defines a custom Unreal Engine game mode that spawns a Skyrim-mirroring camera and a debug reference grid. The implementation visualizes camera motion within an empty map environment during development.

## How it is run
Automatically initialized during Unreal Engine game startup. Invoked by `SkyBridgeGameMode.cpp` (as confirmed by `git grep` output) without command-line arguments. The engine loads this game mode when the project launches.

## Inputs
unsure

## Outputs
None

## Key functions
ASkyBridgeGameMode constructor
BeginPlay override

## Depends on
CoreMinimal.h
GameFramework/GameModeBase.h
SkyBridgeGameMode.generated.h

## Gotchas
Requires an empty map to visualize camera motion.
Debug grid is intended solely for development debugging.

Source: read, not executed.
