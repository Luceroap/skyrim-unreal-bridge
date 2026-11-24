## Purpose
Generates a dynamic night sky material for the Unreal Engine bridge, replacing the default sky dome with a scalable sphere using a precomputed texture. Integrates the material into the active sky rendering system.

## How it is run
Command: `python fix_night.py`  
No other files call it (confirmed via `git grep` with no results).

## Inputs
- Content of `unreal/SkyBridge/live_bridge.py` (read from absolute Windows path)
- `remaster_materials` module's `night_sky_material` function

## Outputs
- Modifies `live.night_mid` (dynamic material instance) and `live.sky_dome` (Unreal actor)
- Creates `SkyBridge/Weather/NightSky` actor with scaled sphere (2e6 units)

## Key functions
night_sky_material (from remaster_materials)  
create_dynamic_material_instance  
spawn (Unreal actor)  
set_static_mesh  
set_actor_scale3d

## Depends on
area2/remaster_materials.py  
unreal/SkyBridge/live_bridge.py

## Gotchas
- Hardcoded absolute Windows path `C:\Users\Aidan\...`
- Relies on exact `"\nstart()\n"` string in `live_bridge.py`
- Uses fixed scale factor `2.0e6` for the sphere
- Directly modifies global `live` module attributes
- Replaces `start()` invocation without fallback handling

Source: read, not executed.
