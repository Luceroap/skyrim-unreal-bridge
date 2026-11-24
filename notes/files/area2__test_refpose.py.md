## Purpose
Modifies the pose application pipeline for the NPC "Carlotta" by temporarily skipping her entry during pose processing. Applies reference bone transforms to component-space for accurate skeletal pose alignment in Skyrim-Unreal integration.

## How it is run
Not executed directly; integrated into the main workflow via the `npc_live` module. No other files call `test_refpose.py` based on `git grep` results showing no matches.

## Inputs
- Actor named "Carlotta" in `npc_live._state["actors"]`
- Unreal Engine skeleton component `c` (retrieved from `e["comp"]`)

## Outputs
- Prints `set` followed by boolean result of `unreal.SkyBridgeViewLibrary.apply_pose()`
- Prints `hand` followed by socket transform coordinates (translation, scale3d) for "NPC-L-Hand-_LHnd_"

## Key functions
`_skip` - Temporarily bypasses pose application for Carlotta
`apply_pose` - Applies reference bone transforms to component space
`get_ref_pose_transform` - Retrieves bone reference poses
`get_socket_transform` - Fetches socket transformation data

## Depends on
`npc_live.py` (modifies `_apply_pose` method)
`unreal` module (for `MathLibrary.compose_transforms`, `RelativeTransformSpace`)

## Gotchas
- Fails if no actor named "Carlotta" exists in `npc_live` state
- Socket name "NPC-L-Hand-_LHnd_" may mismatch actual skeleton name
- Modifies live `_apply_pose` method behavior affecting other actors
- Relies on `c.get_num_bones()` returning correct bone count
- Hardcoded bone name parsing for component-space transforms

Source: read, not executed.
