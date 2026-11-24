## Purpose
This script checks which actors are moving in Skyrim and calculates how much their limb bones deviate from the rest pose. It provides speed, limb angle deviations, and camera-relative positioning data for debugging animations.

## How it is run
Command line: `python tools/debug/walk_check.py`  
Other files calling it: `tools/debug/walk_check_lib.py` (via `git grep` output)

## Inputs
- Skyrim actor data via `npc_live` (Real-time data from Unreal bridge)
- Rest pose JSON files: `area2/npc/skin/skeleton_male.json`, `area2/npc/skin/skeleton_female.json`
- Camera position from memory-mapped file `Local\\SkyrimUnrealBridge_v1`

## Outputs
Console output with per-actor data:  
`speed, name, gender, distance from camera, off-axis angle, "stuck" status, limb angles`

## Key functions
snap() - Captures current actor data from Skyrim bridge  
limb_angles() - Computes bone angles relative to rest pose  
camera() - Reads camera position and direction from memory-mapped file

## Depends on
`npc_live.py` (from `unreal/SkyBridge`)  
`area2/npc/skin/skeleton_male.json`  
`area2/npc/skin/skeleton_female.json`  
`walk_check_lib.py` (caller)

## Gotchas
- Requires Skyrim running in-world (not in menu)
- Camera data sourced from `Local\\SkyrimUnrealBridge_v1` memory-mapped file
- Rest pose JSON paths are hardcoded in `area2/npc/skin/`
- Uses hardcoded 0.6-second sleep between actor snapshots
- "Stuck" detection triggered when limb angle spread < 6.0 degrees

Source: read, not executed.
