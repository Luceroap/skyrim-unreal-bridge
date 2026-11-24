## Purpose
This script debugs bone transformation data for the NPC character Aela in Skyrim, comparing rendered vs. set bone positions and LOD levels during pose rendering.

## How it is run
Not executed directly from command line. Invoked via `npc_live._apply_pose` function (referenced in README.md). No other files call it directly based on available grep results.

## Inputs
Game state actor data via `npc_live._state["actors"]`, specifically searching for actors with "Aela" in their label.

## Outputs
Console output listing bone names, parent bones, render coordinates, set coordinates, and reference rotations for 6 specific bones (e.g., "NPC L Clavicle [LClv]").

## Key functions
get_num_lods
get_predicted_lod_level
get_forced_lod
get_socket_location
get_bone_transform_by_name
rest0q access

## Depends on
npc_live.py
unreal module

## Gotchas
Hardcoded NPC name "Aela" (fails if Aela not present).
Hardcoded bone names (e.g., "NPC L Clavicle [LClv]") may not match other NPC models.
Outputs debug data to console (not for production use).

Source: read, not executed.
