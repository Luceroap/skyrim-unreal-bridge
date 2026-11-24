## Purpose
Reloads the `npc_live` module while preserving spawned NPC state (actors, meshes, rest poses) to maintain live character behavior during hot-reload operations without disrupting ongoing gameplay.

## How it is run
Command line: `python area2/reload_npc_keep.py`. Called by `area2/cap_walkers.py` (per COORDINATION.md reference).

## Inputs
None (relies on existing `npc_live._state` in runtime module).

## Outputs
Console message showing retained actor count and `_walk_record` existence, e.g., `npc_live reloaded, state kept: 5 actors; has _walk_record: True`.

## Key functions
reload_npc_module
preserve_state_after_reload

## Depends on
`npc_live.py` (imports `sys.modules["npc_live"]`).

## Gotchas
- Requires `npc_live` module to be pre-imported (fails if not loaded).
- Preserves only `_state` structure; may not maintain other module internals.
- Explicitly resets `_state` after reload to prevent drift.
- Does not handle dynamic changes to `npc_live` class structure.
- Relies on module name stability (e.g., `sys.modules["npc_live"]` must exist).

Source: read, not executed.
