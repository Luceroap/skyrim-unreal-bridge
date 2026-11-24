## Purpose
This module implements weather effects for snow and rain splash rings that are not covered by `live_bridge`'s rain system. It dynamically creates and updates materials, mesh actors, and parameters for snowflake fields and rain splash decals based on Skyrim's weather conditions.

## How it is run
The module is imported by `live_bridge.Live` after `update_sky` in `tick_body` (via `weather_fx.update(self, cam, dt)`). For development, it uses `install_test_tick(live)` to trigger updates from editor ticks. Not invoked via command line.

## Inputs
- `live`: `live_bridge` instance
- `cam_loc`: Camera world position vector
- `dt`: Time delta (optional, defaults to current time)
- `v`: Weather packet from bridge (structured data for weather values)

## Outputs
- Creates assets at `/Game/WeatherFX/`:
  - Materials: `M_SnowFlakes`, `M_RainSplash`, `MPC_WeatherFX`
  - Mesh: `SM_SnowFlake`
- Modifies material parameters:
  - `DriftX`, `DriftY`, `DriftZ` (wind drift)
  - `Snowfall`, `Splash` (weather intensity)
- Spawns actors: `WeatherFX_Snow` (snow field), `WeatherFX_Splash` (rain decal)

## Key functions
`log` - Logs messages to Unreal editor
`_e` - Creates material expression
`snow_material` - Builds snow material
`splash_material` - Builds splash material
`build` - Creates all assets
`_spawn` - Spawns actors
`update` - Per-frame effect updates
`clear` - Cleans up actors
`install_test_tick` - Testing hook

## Depends on
- Unreal Engine `unreal` module
- `live_bridge.Live` (for hook)
- `COORDINATION.md` (for wet foliage coordination)
- `tools/make_local_queue.py` (listed as dependency)

## Gotchas
- Snow wraps within camera box (2000x2000x1200 cm) to avoid jumps during wind changes
- Rain splashes only appear on near-horizontal surfaces (using depth derivatives)
- Wet foliage handled by `M_SkyMaster` (not in this module)
- Must call `clear()` when bridge stops to remove actors
- `update` requires `live_bridge` instance with weather data

Source: read, not executed.
