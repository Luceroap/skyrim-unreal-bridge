## Purpose
This script debugs NPC skeletal animation data by retrieving bone names from a live NPC actor. It verifies bone naming conventions and structure alignment between Skyrim and Unreal Engine.

## How it is run
Executed via `python tools/debug/npc_names.py` command line. No other project files call it, as confirmed by empty `git grep` results for "npc_names.py".

## Inputs
- `npc_live._state["actors"]` (from the NPC live sync module)
- Unreal Engine's `unreal` module (via `import unreal`)

## Outputs
- Console output: Total bone count followed by first 14 bone names
- Filtered bone names containing "UpperArm" or "Thigh" (first 6 matches)

## Key functions
get_bone_name
get_num_bones

## Depends on
npc_live.py
unreal module

## Gotchas
- Hardcoded Windows path (`C:\Users\Aidan\...`) breaks on non-Windows systems
- Assumes `npc_live._state["actors"]` contains at least one actor
- No error handling if `npc_live._state["actors"]` is empty
- Output only to console; no file persistence
- Requires active Unreal Engine session

Source: read, not executed.
