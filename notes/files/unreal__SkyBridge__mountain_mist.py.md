## Purpose
This script implements soft atmospheric depth effects in Unreal Engine using two layers of fog (haze and a cloud band) to simplify distant geometry without visible edges. It dynamically adjusts haze opacity and cloud band position based on scene parameters while tinting the effect to match ambient light.

## How it is run
Called via `apply(live, strength=1.0)` or `off(live)` from other project code (referenced in AGENT_BRIEFING.md line 53). No command-line invocation; integrated into Unreal's runtime via Python API.

## Inputs
- `live`: Current Unreal scene context object
- `strength`: Float (default 1.0; 0=none, 1=default, 2=moody)
- `cam_z`: Optional camera Z height (cm); defaults to `live.cam_sky[2]` or 0 if missing

## Outputs
- Modifies `ExponentialHeightFog` properties (`start_distance`, `fog_max_opacity`, `second_fog_data`) in the live scene
- Returns status strings (e.g., "haze + cloud band on (strength 1.0)")

## Key functions
_fog - Get fog component from live context
apply - Enable atmospheric effect with parameters
off - Disable effect and reset fog properties

## Depends on
unreal module, `ExponentialHeightFogData` class

## Gotchas
- Cloud band layer fails if `second_fog_data` property is unavailable (e.g., missing in Unreal version)
- BAND_CENTER_ABOVE_PLAYER hard-coded to 12000.0 cm
- cam_z defaults to 0 if `live.cam_sky` is missing
- fog_max_opacity capped at 0.92 (even at strength=2)
- Cloud band density scales linearly (0.0028 * strength)

Source: read, not executed.
