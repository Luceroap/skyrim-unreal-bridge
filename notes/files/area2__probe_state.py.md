## Purpose
Checks if Skyrim is in-world by monitoring shared memory segments created by the Skyrim-Unreal bridge. Reads frame data, position, game time, and UI states from memory.

## How it is run
Executed via `python probe_state.py` command. No other files in the project call it (git grep for `probe_state.py` returned no results).

## Inputs
Shared memory segments named `Local\SkyrimUnrealBridge_v1`, `Local\SkyrimUnrealBridge_world_v1`, `Local\SkyrimUnrealBridge_actors_v1`, and `Local\SkyrimUnrealBridge_gear_v1`.

## Outputs
Console output showing:
- Frame number (offset 12)
- Position (offset 16, 3 floats)
- Game time (offset 92, float)
- UI state (bitmask, offset 300)
- Current cell name (offsets 172-236)
- World state string (offsets 236-300)

## Key functions
OpenFileMappingW: Opens shared memory handles  
MapViewOfFile: Maps memory into process space  
struct.unpack_from: Parses binary memory data  
time.sleep: Delays between frame reads  

## Depends on
None (only standard libraries: ctypes, struct, time).

## Gotchas
- Hardcoded memory offsets (12, 16, 92, 172, 236) will break if Skyrim updates memory layout.
- Checks only for "v1" segments; version changes would require code updates.
- Runs for exactly 3 frames (3 seconds) before exiting.
- Uses per-user "Local" shared memory; multiple users may conflict.
- Relies on fixed bitmask (ui & 64) for "inWorld" check; may break with UI changes.

Source: read, not executed.
