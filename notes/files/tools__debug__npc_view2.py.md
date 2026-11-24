## Purpose
Adjusts the Unreal Engine viewport camera to focus on an NPC named "Aela" (or the first actor if Aela is not found), using hardcoded positional offsets for camera placement and rotation relative to the target's location.

## How it is run
Manually executed via command line (e.g., `python tools/debug/npc_view2.py`). No other files call this script, as confirmed by `git grep` returning no results.

## Inputs
- `npc_live._state["actors"]`: Dictionary of active NPC actors from the live simulation.
- `unreal.Actor` instances with `get_actor_label()` and `get_actor_location()` methods.

## Outputs
- Console output: `target <actor_name> <x,y,z>`.
- Updates Unreal viewport camera position and rotation via `live.ues.set_level_viewport_camera_info()`.

## Key functions
- `get_actor_label()`: Retrieves actor name for label matching.
- `get_actor_location()`: Fetches actor's world position.
- `find_look_at_rotation()`: Computes camera rotation toward target.
- `set_level_viewport_camera_info()`: Updates Unreal viewport camera.

## Depends on
- `tools/debug/npc_live.py`: Provides `_state["actors"]` data.
- `unreal` module: Unreal Engine API for viewport control.
- `tools/unreal/SkyBridge/npc_live.py` (via `sys.path.insert`).

## Gotchas
- Hardcoded Windows path (`C:\Users\Aidan\...`) in `sys.path.insert` may cause failures on non-Windows systems.
- Fixed camera offsets (`y+330`, `z+140`) may require adjustment for different scene layouts.
- Falls back to first actor if "Aela" is not found in labels, risking incorrect target selection.
- Silent failure if no actors exist (no output or camera change).
- Requires active `npc_live` state data populated by the main simulation.

Source: read, not executed.
