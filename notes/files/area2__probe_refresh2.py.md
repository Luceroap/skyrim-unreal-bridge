## Purpose
This script prints real-time bone positions for NPC hands in the Skyrim-Unreal bridge project, primarily for debugging animation synchronization between Skyrim and Unreal Engine. It visualizes socket locations versus bone transform data for each actor's left hand.

## How it is run
Run via command line as `python area2/probe_refresh2.py`; no other files call it (confirmed by `git grep` returning no results).

## Inputs
- The `npc_live` module's `_state["actors"]` data structure containing actor components and bone state.
- Unreal Engine's `ue_bone` function from `npc_live` (accessed via `nl.ue_bone`).
- Bone name "NPC L Hand [LHnd]" hardcoded in the script.

## Outputs
Console output formatted as:
`<actor_name> render (x y z) set (x y z) vis=<bool>`
Example: `NPC123                    render (1.2 3.4 5.6) set (1.1 3.3 5.5) vis=True`

## Key functions
get_world_transform
get_socket_location
get_bone_transform_by_name
print (formatted output)
ue_bone (from npc_live)

## Depends on
area2/npc_live.py (imports `nl`, uses `_state["actors"]`), unreal.BoneSpaces

## Gotchas
- Hardcoded bone name "NPC L Hand [LHnd]" will fail if skeleton uses different naming.
- Relies on `unreal.BoneSpaces.COMPONENT_SPACE` which may change in Unreal Engine updates.
- Outputs only to console; no persistent logs or files generated.
- Assumes `npc_live` module structure remains unchanged (uses private `_state`).
- No error handling for missing actors or bones.

Source: read, not executed.
