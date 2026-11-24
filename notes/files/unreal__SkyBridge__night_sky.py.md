## Purpose
Manages celestial objects (moons, planets, and aurora) for the in-game night sky, appearing only during nighttime with dynamic phase lighting and aurora effects. Objects are positioned inside a 1000 km star dome and follow camera movement.

## How it is run
Not directly executed; called via `apply(live, night=True, aurora=True)` from other Unreal Engine Python scripts. No other files directly reference `night_sky.py` in the project (grep result shows no matches).

## Inputs
- `live`: Unreal engine context object (requires `sky_dome` and `night_mid` properties)
- `night`: Boolean (default `True`; enables/disables celestial objects)
- `aurora`: Boolean (default `True`; toggles aurora effects)

## Outputs
- Creates/updates Unreal material at `/Game/NightSky/M_Celestial`
- Spawns actors (`StaticMeshActor`) attached to sky dome
- Modifies material parameters (`Aurora`, `Intensity`) via `night_mid` property
- Returns status string (e.g., `"moons/planets on, aurora on"`)

## Key functions
build: Creates celestial material shader
apply: Activates/deactivates night sky elements
remove: Deletes all celestial actors
_spawn: Positions and configures celestial objects

## Depends on
math, unreal (Unreal Engine Python API)

## Gotchas
- Requires `live.sky_dome` for proper actor attachment (defaults to origin if missing)
- Aurora control via `live.night_mid` silently fails if parameter missing
- Material path `/Game/NightSky/M_Celestial` may conflict with manually placed assets
- Fixed object placement inside 1000 km dome (no dynamic scaling)
- `craters` parameter in `BODIES` determines surface texture (1=cratered, 0=flat)

Source: read, not executed.
