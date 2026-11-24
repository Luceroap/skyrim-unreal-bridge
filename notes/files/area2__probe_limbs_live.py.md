## Purpose
Processes NPC limb pose data by calculating bone angles and timing information for real-time animation adjustments in the Skyrim-Unreal bridge.

## How it is run
Executed as a standalone script; no other project files reference it (grep for "probe_limbs_live.py" returned no matches).

## Inputs
State data from npc_live module (nl._state), including actor bone transforms, sequences, and animation states.

## Outputs
Console logs detailing actor names, distances, readiness, animation plans, pose histories, and calculated bone angles.

## Key functions
ang (angle calculation between two bones)

## Depends on
npc_live.py

## Gotchas
- Skips actors with fewer than 60 bones (line 7)
- Handles angle calculation exceptions by setting r=-1 (lines 13-14)
- Uses time.time() for pose timestamp comparisons (lines 6, 20)
- Outputs formatted console logs with pose metrics (line 19)

Source: read, not executed.
