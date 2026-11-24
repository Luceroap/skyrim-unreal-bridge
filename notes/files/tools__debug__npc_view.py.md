## Purpose
This script provides a debug view by positioning the Unreal viewport camera to follow a target NPC (e.g., "Aela"), aiding in visualizing NPC locations during development. It dynamically calculates camera angles relative to NPC positions.

## How it is run
Executed manually via `python tools/debug/npc_view.py`. No other files were found to call this script using `git grep` (no results returned).

## Inputs
None (reads from `npc_live._state` and Unreal engine state).

## Outputs
Console output of spawned NPC labels; modifies Unreal viewport camera settings (`set_level_viewport_camera_info`).

## Key functions
tick
get_actor_label
get_actor_location
find_look_at_rotation
set_level_viewport_camera_info

## Depends on
npc_live
unreal

## Gotchas
- Loop executes 8 times, causing repeated camera resets.
- Relies on exact NPC name "Aela" (case-sensitive); defaults to first actor if not found.
- Camera offsets (y+330, z+140) are hardcoded and likely map-specific.
- Modifies `npc_live._state["last"]` which may interfere with other operations.
- Camera target selection prioritizes "Aela" over all other NPCs.

Source: read, not executed.
