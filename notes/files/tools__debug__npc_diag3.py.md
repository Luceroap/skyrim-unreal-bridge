## Purpose
This script compares bone positions between Skyrim actors and their corresponding Unreal Engine (UE) actors to identify discrepancies in NPC rigging. It converts Skyrim coordinate data to UE space using a fixed scaling factor and calculates positional errors for specific bones.

## How it is run
Run directly as `python tools/debug/npc_diag3.py` from the project root. No other files call it (confirmed via empty `git grep` output for "npc_diag3.py" across project files).

## Inputs
- Data from `npc_live.read_actors()` (list of Skyrim actor data)
- `npc_live._state["actors"]` (processed actor state cache)

## Outputs
Console output showing actor labels and bone position errors (e.g., "ActorName world-position error (cm) of bones vs Skyrim: [('NPC L Hand', 1.2), ...]").

## Key functions
- Iterate over first 4 actors in `npc_live._state["actors"]`
- Convert Skyrim bone positions using scaling factor U
- Calculate Euclidean distance between expected and actual UE bone locations
- Format output with bone names and error values

## Depends on
- `npc_live.py` (imports `read_actors()`, `_state`)
- `unreal` module (for bone location queries)
- Python standard libraries (`sys`, `math`)

## Gotchas
- Hardcoded scaling factor U = 1.4287
- Only processes first 4 actors (`[:4]`)
- Relies on specific bone naming formats like "NPC L Hand [LHnd]"
- Uses `npc_live._state` directly (not public API)
- Bone name extraction logic uses `[...]` pattern matching

Source: read, not executed.
