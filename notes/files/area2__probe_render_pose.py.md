## Purpose
This script calculates and prints the upper-arm angle from vertical for NPCs in the Skyrim-Unreal bridge, using socket location data from actor components with sufficient bone counts to determine pose alignment.

## How it is run
Executed via command line (e.g., `python area2/probe_render_pose.py`). No other project files reference this script, as confirmed by `git grep` with no results.

## Inputs
- Actor component data from `npc_live._state["actors"]`
- Socket location data (`NPC L UpperArm [LUar]` and `NPC L Forearm [LLar]`) for actors with ≥100 bones

## Outputs
Console output with formatted lines (e.g., `"ActorLabel rendered upper-arm angle from vertical: X.X deg"`), showing actor name and angle calculation.

## Key functions
get_num_bones
get_world_transform
get_socket_location
inverse_transform_location
calculate_angle_from_vertical

## Depends on
npc_live (module)
unreal.SkyBridgeViewLibrary

## Gotchas
- Processes only first 12 actors (`[:12]`)
- Skips actors with bone count < 100 (`c.get_num_bones() < 100`)
- Relies on fixed socket names `NPC L UpperArm [LUar]` and `NPC L Forearm [LLar]`
- Uses Z-component of vector for angle calculation (`-v.z / n`)
- Prints `apply_pose` availability check even if unused

Source: read, not executed.
