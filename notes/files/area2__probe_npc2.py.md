## Purpose
This script profiles the performance of bone transformation operations for NPCs by timing get and set operations on up to 80 bones in the rest pose. It verifies bone count consistency between the rest JSON data and streamed actor data.

## How it is run
Run directly via `python area2/probe_npc2.py`. No other files call this script (git grep found no references).

## Inputs
- Current actor state via `npc_live._state["actors"]`
- Bone names from `e["rest0"]` (first 80 entries)
- Male NPC rest pose data via `nl.rest_pose("male")`

## Outputs
- Console output: `bones [count] 80 sets [X] ms, 80 gets [Y] ms`
- First 5 bone names from `e["rest0"]`
- Count of bones in `nl.rest_pose("male")` and streamed bones per actor

## Key functions
get_bone_transform_by_name
set_bone_transform_by_name
rest_pose (from npc_live)
read_actors (from npc_live)
bone_transform timing

## Depends on
- `npc_live.py` (via `sys.modules["npc_live"]`)
- Unreal Engine `unreal` module (for bone transforms)

## Gotchas
- Hardcoded to male NPC rest poses (`rest_pose("male")`)
- Truncates bone list to first 80 entries (`[:80]`)
- Fails if no actors exist in `_state["actors"]`
- Processes only the first actor found (`next(iter(...))`)
- Measures bone transforms on a single actor only

Source: read, not executed.
