## Purpose
Dynamically updates the running Unreal Editor's live_bridge with current atmosphere.py and live_bridge.py content without restarting the editor. Applies atmosphere quality settings and sky/lighting updates to the active scene.

## How it is run
Executed via `python area2/hot_atmos.py` command line; no other files in the project call it (confirmed by empty `git grep` result).

## Inputs
- `hot_tier.txt` (reads tier quality setting if file exists)
- `live_bridge.py` (expected to contain `start()` function)
- Current Unreal Editor scene state (via `live` object)

## Outputs
- Console output showing quality tier, GPU detection, night mid value, light count, and base lights
- Modified live atmosphere component (`live.atmosphere`)
- Updated lighting configurations (`live.light_base`, `live.light_actors`)

## Key functions
apply_quality
detect_gpu
sweep_captures
reload(atmosphere)
exec(live_bridge.py)
get_all_level_actors
get_component_by_class
update_sky
tick_body
apply_lights

## Depends on
atmosphere.py
live_bridge.py
live object (from live_bridge module)

## Gotchas
Hardcoded absolute paths (C:\Users\Aidan\SkyrimUnrealBridge)
Relies on `live_bridge.py` containing `start()` function
Modifies global `live` state without user confirmation
Assumes `live_bridge.py` structure matches expected format
Requires `live` object to be initialized before execution

Source: read, not executed.
