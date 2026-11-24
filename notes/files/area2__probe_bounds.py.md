## Purpose
This script debugs actor bounding volumes and bone transformations in the Skyrim-Unreal bridge by logging data for the first four actors' components. It checks specific skeletal bones to verify pose and transform consistency.

## How it is run
Run directly via command line (e.g., `python area2/probe_bounds.py`). No other files call it, confirmed by `git grep` search.

## Inputs
`npc_live._state["actors"]` data structure containing actor and component references.

## Outputs
Console output listing actor labels, locations, bounds origins, extents, and bone transforms for specific bones.

## Key functions
get_actor_bounds
get_actor_location
get_bone_index
get_bone_transform_by_name
get_ref_pose_transform

## Depends on
npc_live.py (via `sys.modules["npc_live"]`)
unreal.BoneSpaces.COMPONENT_SPACE

## Gotchas
Processes only the first 4 actors (list[:4]).
Hardcoded bone names like "NPC-Pelvis-_Pelv_" may not exist in all skeletons.
Assumes bone names match exact strings (e.g., "NPC-Head-_Head_").
Console output is the sole output; no files or shared memory written.
Bone checks skip actors missing specified bones.

Source: read, not executed.
