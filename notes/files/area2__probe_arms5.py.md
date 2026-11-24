## Purpose
Probes the component state of the NPC "Aela" to verify tick management and LOD model properties within the Skyrim game state. Monitors component methods related to refresh, update, and pose operations.

## How it is run
Executed directly via `python area2/probe_arms5.py`. No other files reference this script (grep found no caller references).

## Inputs
None specified; relies entirely on active game state via the `npc_live` module.

## Outputs
Console output listing component methods matching keywords (e.g., "tick", "lod"), current tick enable status, and forced LOD model value.

## Key functions
Locate Aela NPC actor  
Enumerate component method keywords  
Query component tick status  
Check component LOD model  

## Depends on
`npc_live` module (assumed to be `area2/npc_live.py`)

## Gotchas
- Script fails with `StopIteration` if "Aela" NPC is not present in active game data  
- Assumes component supports `get_editor_property` (checked via `hasattr`)  
- No error handling for missing NPC actor in code  

Source: read, not executed.
