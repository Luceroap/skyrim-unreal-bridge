## Purpose
Debugging tool to test spawning NPCs beyond the default 12-nearest limit in the Skyrim-Unreal bridge, inspecting actor data for non-excluded creatures. Temporarily modifies NPC limits for testing purposes.

## How it is run
Executed directly via `python tools/debug/npc_creature_test.py` command. No other files call it (confirmed by empty `git grep` result).

## Inputs
Current Unreal game state (via `unreal` module) and `npc_live` module's internal state (e.g., `_state` dictionary).

## Outputs
Console output showing spawned actor count, location coordinates, bone counts, scale values, and pose samples for non-excluded NPCs. Resets `npc_live.MAX_NPCS` after execution.

## Key functions
_read_and_spawn
get_actor_label
get_actor_location
get_num_bones
get_actor_scale3d

## Depends on
tools/npc_live.py
tools/live_bridge.py

## Gotchas
- Temporarily sets `npc_live.MAX_NPCS` to 60 for testing, must be reset.
- Skips specific NPC names (e.g., "Aela", "Guard") in output.
- Fixed 10-iteration loop may cause noticeable delays.
- Prints detailed actor data for non-excluded NPCs, potentially cluttering logs.
- Relies on Unreal API methods (`get_actor_location`, etc.) without error handling.

Source: read, not executed.
