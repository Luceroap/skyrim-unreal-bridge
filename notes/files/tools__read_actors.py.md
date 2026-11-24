## Purpose
Reads and prints a summary of actor pose data from the Skyrim plugin's shared memory segment, verifying memory layout offsets for debugging and synchronization.

## How it is run
Command: `python tools\read_actors.py`. Called directly by developers as noted in `COORDINATION.md` as the reference tool for actor data offsets.

## Inputs
Shared memory segment named "Local\\SkyrimUnrealBridge_actors_v1" created by the Skyrim plugin.

## Outputs
Console text summarizing:
- Memory header (magic, version, sequence, tick, actor count)
- Bone names (first 96 entries)
- Up to 8 actor poses (ID, position, yaw, skeleton name, bone data for first actor)

## Key functions
Open shared memory
Parse header structure
Print actor data
Process bone data
Decode name strings

## Depends on
ctypes, ctypes.wintypes (Windows API access), Skyrim plugin's shared memory output.

## Gotchas
- Plugin must be loaded and running (mapping not found → exit)
- Actor names truncated to 40-character buffers
- Memory layout structure hardcoded (plugin version changes break parsing)
- Only prints first 8 actors (min(nA, 8))
- Only prints bone data for first actor's first 4 bones

Source: read, not executed.
