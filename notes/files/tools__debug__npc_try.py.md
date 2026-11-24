## Purpose
Debugs NPC state synchronization between Skyrim and Unreal by simulating multiple tick cycles, printing mesh/actor states, and validating streamed actor data through the npc_live module.

## How it is run
Command line: `python tools/debug/npc_try.py`. No other files call it (no results found from `git grep "npc_try\.py"` in project files).

## Inputs
The `live` variable (required but not defined in this file, must be present in caller's scope).

## Outputs
Console output showing:
- Mesh names (e.g., `meshes ['mesh1', 'mesh2']`)
- Actor data (e.g., `actors [('actor1', 'Actor Label')]`)
- Failed counts (`failed 0`)
- Stream actor details (name, base address hex, bone count)

## Key functions
tick
read_actors
reload

## Depends on
unreal/SkyBridge/npc_live.py

## Gotchas
Hardcoded 6-loop simulation (may not reflect actual use case)
Requires external `live` variable in scope
Overwrites `npc_live._state["last"]` per iteration

Source: read, not executed.
