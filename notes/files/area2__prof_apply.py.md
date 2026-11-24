## Purpose
Applies poses to all visible NPCs in the game state using the `_apply_pose` function. Measures and reports performance metrics for the operation.

## How it is run
Executed via `python area2/prof_apply.py` command line. Called indirectly by main application logic as referenced in COORDINATION.md line 99.

## Inputs
NPC state data from `npc_live._state["actors"]` filtered for entries with `e.get("shown")` truthy.

## Outputs
Console output formatted as: `X poses in Y ms (Z ms each)` showing total poses, elapsed time, and average time per pose.

## Key functions
`_apply_pose` - Applies pose data to NPC actor.

## Depends on
`npc_live` module (accessed via `sys.modules["npc_live"]`).

## Gotchas
- Only processes NPCs explicitly marked as "shown" in the game state.
- Causes a violation in python311.dll during execution (noted in COORDINATION.md line 99).
- Relies on internal `_apply_pose` method which may be subject to future changes.

Source: read, not executed.
