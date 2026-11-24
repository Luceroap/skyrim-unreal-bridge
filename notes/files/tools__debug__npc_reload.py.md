## Purpose
This script destroys all NPCs with labels starting with "NPC_" in the current Unreal Editor level and reloads the `npc_live` module to reset its state. The `live_bridge` system then uses the updated module on its next tick to respawn NPCs.

## How it is run
Executed directly within the Unreal Editor's Python environment (e.g., via the Editor's script console). No other files in the project call `npc_reload.py`, as confirmed by `git grep` (no matches found).

## Inputs
Current Unreal Editor level containing actors with labels starting with "NPC_" (e.g., "NPC_Alice", "NPC_Goblin").

## Outputs
- Destroys all matching actors in the level.
- Prints `npc_live reloaded` to the Unreal console.
- Updates `npc_live` module state for `live_bridge` to use on next tick.

## Key functions
get_all_level_actors
destroy_actor
importlib.reload

## Depends on
npc_live.py (module)
unreal Python API

## Gotchas
- Destroys all actors with labels starting with "NPC_", including non-NPCs if mislabeled.
- Requires an active Unreal Editor session to execute.
- Reloading `npc_live` causes temporary NPC disappearance until `live_bridge` respawns them.
- Must be run from within Unreal's Python environment (not via external command line).
- No command-line arguments are accepted; script execution context is fixed.

Source: read, not executed.
