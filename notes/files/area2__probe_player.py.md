## Purpose
Measures Skyrim's frame rate (FPS), game-time progression relative to real time, and player movement speed. Outputs metrics for debugging and performance monitoring of the Skyrim-Unreal bridge.

## How it is run
Command line: `python area2/probe_player.py`. Called from README.md (section 297) as an example usage.

## Inputs
Reads from Windows shared memory segment named "Local\\SkyrimUnrealBridge_v1" via `OpenFileMappingW`/`MapViewOfFile` APIs.

## Outputs
Prints to stdout:
- Real duration, frame count, FPS, game-time scale
- Player speed (max/median units/s) with Skyrim context (walk ~80, run ~250-300)

## Key functions
rd() - reads shared memory data  
sampling loop - collects 60 samples at 0.1s intervals  
game time calculation - handles day/hour transition  
speed calculation - computes 2D Euclidean distance per time  
time formatting - outputs metrics with Skyrim context

## Depends on
None (only standard libraries: ctypes, struct, time, math)

## Gotchas
Uses 60 samples collected at 100ms intervals  
Game time calculation switches to hour-based fallback if day change is negligible  
Player speed derived from 2D position (x/y) only  
Output includes hardcoded Skyrim speed benchmarks  
Print statements use exact Skyrim value ranges (walk 80, run 250-300)

Source: read, not executed.
