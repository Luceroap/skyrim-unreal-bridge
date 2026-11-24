## Purpose
This file patches the live bridge to integrate rain effects by modifying rain occurrence spawning and updating logic. It reloads rain materials and injects patched functions into the bridge's live module.

## How it is run
Command line: `python area2/patch_rain_occ.py` (executed manually during bridge setup). No other files call it, as confirmed by empty `git grep` results.

## Inputs
- `live_bridge.py` (read and patched via `exec`)
- `remaster_materials` module (reloaded via `importlib.reload`)

## Outputs
Console messages: "material [name]", "capture [live.rain_occ]", "rain now [value]". Modifies `live` object attributes (`rain_occ_spawn`, `rain_occ_update`, etc.).

## Key functions
rain_drops_material
rain_occ_spawn
rain_occ_update
update_sky
water_slots

## Depends on
remaster_materials.py
unreal/SkyBridge/live_bridge.py
live module (from bridge context)

## Gotchas
Hardcoded absolute path to live_bridge.py may break if directory structure changes.
Requires live_bridge.py to end with "start()" (assertion fails otherwise).
rain_occ_spawn is conditionally called only when live.rain_field is truthy.
Relies on remaster_materials.rain_drops_material() being callable with rebuild=True.

Source: read, not executed.
