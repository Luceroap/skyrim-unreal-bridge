## Purpose
This script checks which streamed actors in Skyrim are moving by comparing their limb bone angles to the skeleton's rest pose (T/A pose). It calculates angular deviations in degrees using quaternion math to detect movement from the reference pose.

## How it is run
Run via `python tools/walk_check.py` while Skyrim is in the world. Only called by `tools/walk_check.py` (verified by grep search for `walk_check_lib.py` in source files).

## Inputs
- Shared memory segment `SkyrimUnrealBridge_v1` (via Windows memory mapping)
- Skeleton JSON files `area2/npc/skin/skeleton_male.json` and `skeleton_female.json`

## Outputs
- Returns bone angle deviations (dictionary: `{"UpperArm": 15.2, ...}`) via `limb_angles()`
- Returns camera position/forward vector via `camera()`
- No file writes (only shared memory reads)

## Key functions
snap() - Fetches actor data from Skyrim
limb_angles() - Computes bone angle deviations
camera() - Retrieves camera data from shared memory

## Depends on
npc_live.py (for `read_actors()`)
area2/npc/skin/skeleton_*_json
Windows kernel32 (ctypes.wintypes)

## Gotchas
- Windows-only (uses kernel32 API calls)
- Male/female skeleton JSONs only; non-binary NPCs may fail
- Hardcoded shared memory name "SkyrimUnrealBridge_v1"
- Hardcoded memory offsets (40 bytes, 48 bytes)
- Relies on Skyrim's specific memory layout for camera data

Source: read, not executed.
