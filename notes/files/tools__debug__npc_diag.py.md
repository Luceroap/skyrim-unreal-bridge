## Purpose
Debugs NPC bone transformations by comparing current bone positions and rotations to rest poses. Outputs movement metrics (distance and rotation) for the first two actors' specified bones.

## How it is run
Command line: `python tools/debug/npc_diag.py`. No other files found calling it via `git grep` output.

## Inputs
Current NPC actor states from `npc_live._state["actors"]`, accessed as `acts` variable.

## Outputs
Console output displaying:
- NPC actor count
- For first two actors:
  - Actor label
  - Bone name (e.g., "NPC L UpperArm [LUar]")
  - Translation distance (cm) from rest
  - Rotation angle (deg) from rest

## Key functions
ue_bone
get_bone_transform_by_name
quat_to_mat
mul
tr
math.dist
math.acos
math.degrees

## Depends on
`npc_live.py` (imports `npc_live._state`, `npc_live.ue_bone`, `npc_live.quat_to_mat`, `npc_live.mul`, `npc_live.tr`)
Unreal Engine API (`unreal.BoneSpaces.COMPONENT_SPACE`)

## Gotchas
- Hardcoded Windows path in `sys.path` (C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge)
- Only processes first 2 actors (`list(acts.items())[:2]`)
- Bone names must exactly match hardcoded strings (e.g., "NPC L UpperArm [LUar]")
- Uses `math.acos` with clamping (`max(-1, min(1, ...))`) to avoid floating-point errors
- Rotation calculation uses matrix dot product formula for angle (Rrel[0] + Rrel[4] + Rrel[8] - 1)/2

Source: read, not executed.
