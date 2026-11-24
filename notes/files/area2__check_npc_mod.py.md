## Purpose
This script checks the live state of NPCs in the Skyrim to Unreal bridge, verifying key attributes and printing actor and walk loop statistics for debugging purposes.

## How it is run
Command line: `python area2/check_npc_mod.py`. No other files call this script, as confirmed by `git grep` showing no references.

## Inputs
The current state of the `npc_live` module (`nl._state`), including actor data and walk loop configurations.

## Outputs
Console output showing:
- Presence of `_ref_scales` and `_walk_pose` attributes
- Number of actors (`len(nl._state["actors"])`)
- Walk loop durations formatted as `{"key": rounded_duration, ...}`

## Key functions
- Check _ref_scales
- Check _walk_pose
- Print actor count
- Print walk loop durations

## Depends on
`npc_live` module (must be loaded via `sys.modules`)

## Gotchas
none noticed

Source: read, not executed.
