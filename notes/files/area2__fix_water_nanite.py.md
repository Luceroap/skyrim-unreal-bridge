## Purpose
Disables Nanite rendering for water materials named "M_SkyWater" on static mesh components in Unreal Engine levels. Resolves visual artifacts when Nanite is enabled for water assets.

## How it is run
Executed as a standalone Unreal Editor Python script. No other project files call it (confirmed by empty `git grep` results for "fix_water_nanite.py").

## Inputs
None (reads level data via Unreal API).

## Outputs
Prints count of modified water components to console (e.g., "water components switched off Nanite: 12").

## Key functions
water_slots
process_level_actors

## Depends on
None (relies solely on Unreal Engine Python API).

## Gotchas
- Only applies to StaticMeshActor components (ignores other actor types).
- Material name must be exactly "M_SkyWater" (case-sensitive).
- Modifies in-memory editor properties without persisting to disk.
- Runs once per level session (requires manual re-execution after level changes).
- Uses `disallow_nanite` editor property (Unreal API requirement).

Source: read, not executed.
