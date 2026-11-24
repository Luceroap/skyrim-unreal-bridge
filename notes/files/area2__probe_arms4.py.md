## Purpose
This script retrieves and prints bone transforms for specific limbs of an NPC (Aela) in Unreal Engine, primarily for debugging the Skyrim-to-Unreal bridge. It verifies component-space to world-space bone transformations and socket locations.

## How it is run
Run via `python area2/probe_arms4.py` from the project root. No other project files call this script (git grep found no invocations).

## Inputs
- Current game state via `sys.modules["npc_live"]`
- NPC name "Aela" (hardcoded in actor search)
- Predefined bone names (e.g., "NPC Head [Head]")

## Outputs
Printed to stdout:
- Component world transform (translation, rotation, scale)
- Component relative transform (scale)
- Actor transform (scale, rotation)
- Bone-to-world transform and socket locations for each listed bone

## Key functions
`get_world_transform`
`get_relative_transform`
`get_bone_transform_by_name`
`get_socket_location`
`get_actor_transform`
`get_actor_rotation`
`get_actor_label`

## Depends on
`sys` module, `npc_live` module (via `sys.modules`), `unreal.BoneSpaces`

## Gotchas
- Hardcoded NPC name "Aela" may fail if actor label changes
- Hardcoded bone names (e.g., "NPC Head [Head]") depend on exact Unreal bone naming
- Uses `next(e for ...)` without error handling for missing actor
- Assumes `nl._state["actors"]` contains valid data
- Relies on Unreal bone naming conventions without validation

Source: read, not executed.
