## Purpose
This script identifies NPCs moving at speeds exceeding 25 units and adjusts the Unreal viewport camera to follow them. If no such NPCs are detected, it lists all non-walking NPCs in the console.

## How it is run
Command line: `python tools/debug/npc_view3.py`. Other files that call it: unsure.

## Inputs
Reads actor data from `npc_live._state` (specifically `npc_live._state["actors"]`) and Unreal's runtime actor state.

## Outputs
Console output showing target NPC details (label, speed, location) and sets the Unreal viewport camera via `live.ues.set_level_viewport_camera_info`.

## Key functions
- get_actor_location
- find_look_at_rotation
- get_actor_label
- set_level_viewport_camera_info

## Depends on
npc_live, unreal

## Gotchas
- Hardcoded speed threshold of 25
- Camera position uses fixed offsets (x+300, y+150, z+140)
- Prints list of non-walking NPCs when no target found
- Relies on `npc_live._state` being populated
- Uses Unreal Vector coordinates for camera positioning

Source: read, not executed.
