## Purpose
Compares the actual pose data of a character (Carlotta) against expected pose data during the Skyrim-Unreal bridge process, debugging skeletal animation alignment.

## How it is run
Run as a standalone Python script (e.g., `python probe_cmp.py`). No other files call it based on current `git grep` results.

## Inputs
- Character actor data for "Carlotta" from `npc_live` module.
- Skeleton data from Unreal Engine (`c.get_num_bones()`, bone names/transforms).
- Pose data from `e["shown"]["pose"]`.

## Outputs
- Console output showing bone names, position differences, rotation angles (in degrees), and scale factors for up to 16 bones (12 primary + 4 hand/head).
- Captures `cap["n"]` (bone names) and `cap["t"]` (transforms) during pose application.

## Key functions
Fake.apply_pose
rotation comparison calculation
bone data processing loop

## Depends on
npc_live (from `sys.modules`)
unreal (Unreal Engine API)
SkyBridgeViewLibrary (Unreal's pose application interface)

## Gotchas
- Hardcoded actor name "Carlotta" in actor search.
- Only processes 12 primary bones plus 4 hand/head bones.
- Temporarily replaces Unreal's `apply_pose` method using `try/finally`.
- Requires "Carlotta" to exist in NPC state.
- Uses absolute rotation comparison (dot product) without normalization.

Source: read, not executed.
