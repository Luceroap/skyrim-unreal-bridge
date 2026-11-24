## Purpose
This script queries and prints fog-related editor properties of the Unreal Engine asset `M_NightSky` in the project's Area2 environment. It provides debug information about fog settings, sky dome component bounds, and location for debugging or validation purposes.

## How it is run
Command line execution (e.g., `python area2/probe_fog.py`). No other project files call it (confirmed by empty `git grep` output for `probe_fog.py` references).

## Inputs
- Unreal asset path: `/Game/Area2Tex/M_NightSky`
- Live context object `live.sky_dome` (assumed to exist in runtime state)

## Outputs
- Printed list of tuples containing fog-related property names and values (e.g., `('apply_fogging', True)`).
- Printed sky dome component bounds sphere radius (if available) and actor location.

## Key functions
- Load Unreal asset `/Game/Area2Tex/M_NightSky`
- Iterate over fog properties to fetch editor values
- Handle missing properties via exception catching
- Access sky dome static mesh bounds
- Print runtime debugging data

## Depends on
- `unreal` (Unreal Engine Python API)
- `live` module (assumed global context containing `sky_dome`)

## Gotchas
- Hardcoded asset path `/Game/Area2Tex/M_NightSky` will break if asset is renamed/moved.
- Relies on `live.sky_dome` being present; crashes if absent.
- Only checks specific predefined properties; misses other fog settings.
- Prints "ERR" for missing properties without context.
- Does not handle invalid `sky_dome` bounds access (may print `None`).

Source: read, not executed.
