## Purpose
Debugging tool to locate and display the position and scale of cow NPCs within the Unreal Engine viewport. It adjusts the camera to view the cow from a predefined offset relative to its location.

## How it is run
Command line: `python tools/debug/npc_view_cow.py`. No other project files call this script (confirmed by empty `git grep` output).

## Inputs
- `npc_live._state["actors"]` containing actor metadata from the bridge.

## Outputs
- Console output with cow coordinates (rounded X/Y/Z) and scale.
- Updates level viewport camera position and rotation via `live.ues.set_level_viewport_camera_info`.

## Key functions
get_actor_label
get_actor_location
get_actor_scale3d
find_look_at_rotation
set_level_viewport_camera_info

## Depends on
npc_live.py
unreal.py

## Gotchas
- Case-sensitive "Cow" substring check may miss actor labels like "cow" or "COW".
- Hard-coded camera offset (420, 250, 170) may not align with all map layouts.
- Prints "no cow spawned" if cow was despawned or exceeded spawn range.
- Requires valid `npc_live` state with cow data present.
- Camera adjustment uses absolute position; may not work if actors are outside bounds.

Source: read, not executed.
