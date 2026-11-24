## Purpose
Measures and compares angular positions of Skyrim character arm bones to their Unreal Engine equivalents for pose validation. Outputs comparative data for debugging animation synchronization between engines.

## How it is run
Not directly executable; triggered during NPC pose processing via `npc_live` module. No external callers found via `git grep` for `probe_arms.py`.

## Inputs
Character pose data from `npc_live._state["actors"]`, specifically actor states containing `pose` with `bones`, `rq`, `rp` arrays and rest pose data.

## Outputs
Command-line output formatted as:
`[ActorLabel] L: skyrim [angle] unreal [angle] rest [angle] R: ... bind=[bool]`

## Key functions
ang() - Computes angle between 3D vectors using dot product.
nl.rest_pose() - Retrieves rest pose data for character.
nl._is_bind() - Checks if pose data is bound to skeleton.
get_socket_location() - Retrieves Unreal bone socket positions.

## Depends on
`npc_live` (imports via `sys.modules["npc_live"]`), `math`, `sys`.

## Gotchas
- Uses hardcoded Skyrim bone name patterns like "NPC L UpperArm [LUar]".
- Skips arms if both upper/forearm bones are missing from pose data.
- Outputs angles rounded to 1 decimal place.
- Rest pose angles (`r0`) are `None` if bone missing in rest data.
- Relies on `npc_live`'s `_is_bind` method for binding status.

Source: read, not executed.
