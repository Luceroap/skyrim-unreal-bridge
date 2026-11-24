## Purpose
This script inspects actor animation states in Skyrim's runtime, checking readiness, positioning, and bone structures related to arms, clavicles, and spines for debugging purposes.

## How it is run
Executed directly via command line (e.g., `python area2/probe_arms2.py`). The `git grep` command shows no other files call it.

## Inputs
- Game state data from `npc_live._state` (actor dictionary values).
- Hardcoded NPC name "Aela" for target actor lookup.

## Outputs
- Debug output to stdout: actor labels, readiness status, history length, time since posing, distance, and animation plan entries.
- Filtered bone names (e.g., "Arm", "Clav", "Spine") from character mesh.

## Key functions
Actor readiness check  
Bone name filtering  
Mesh bone count verification  
Target NPC identification  
Bone name listing

## Depends on
- `npc_live` module (via `sys.modules["npc_live"]`).

## Gotchas
- Hardcoded NPC name "Aela" may fail if NPC name changes.  
- Bone filtering uses partial string match ("Arm" in bone name), which may miss non-standard naming.  
- No callers found via `git grep`, indicating manual execution only.  
- Relies on specific `npc_live` internal structure.  
- Time calculations assume `posed_t` field exists (defaults to 0 if missing).  

Source: read, not executed.
