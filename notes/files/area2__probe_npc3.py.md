## Purpose
Monitors NPC animation states and pose budgets in SkyrimUnrealBridge, printing real-time debug data about active NPCs. Designed for runtime inspection of animation states and bone rotations during development.

## How it is run
Command line: `python probe_npc3.py` (requires Python interpreter). No other files in the project call this file (git grep shows no references).

## Inputs
Reads from `npc_live._state` (e.g., `st["actors"]`, `st["pose_budget"]`, `st["seq"]`).

## Outputs
Console output with formatted NPC data including:
- Actor labels
- "ready" status and plan lengths
- Bone rotation differences (e.g., "L-upperarm deg from bind")
- Bone counts (`comp.get_num_bones()`)

## Key functions
get_bone_transform_by_name
get_num_bones
mat_to_quat
print

## Depends on
npc_live.py (via `sys.modules["npc_live"]`)

## Gotchas
- Only processes first 6 NPCs (due to `list(st["actors"].items())[:6]` slicing).
- Fails if `npc_live` module is not loaded (KeyError in `sys.modules["npc_live"]`).
- Relies on `unreal.BoneSpaces.COMPONENT_SPACE` (Unreal Engine enum, must be valid).

Source: read, not executed.
