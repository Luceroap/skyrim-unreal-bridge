## Purpose
Validates bone socket locations and scales against bone transforms in the Skyrim-to-Unreal bridge, identifying discrepancies for debugging purposes. It checks alignment between socket positions and bone transforms with specific thresholds.

## How it is run
Executed directly via Python command; no other files reference `probe_render2.py` as confirmed by `git grep` results.

## Inputs
- NPC Live module state (`npc_live._state["actors"]`) containing Skyrim actor data
- Active Unreal Engine bone hierarchy via `c.get_bone_*` methods

## Outputs
- Console output showing actor location, bounds, and count of "bad" bones
- For each of up to 40 bad bones: bone index, name, location deviation (x,y,z), and scale deviation (x,y,z)

## Key functions
- get_bone_transform_by_name
- get_socket_location
- math.dist
- inverse_transform_location

## Depends on
npc_live, unreal, sys, math

## Gotchas
- Bones with index <4 are always flagged as "bad"
- Scale deviation threshold of 5% (abs(sc.x - 1) > 0.05)
- Bone socket z-position must be within [-300, 300] units
- Output limited to first 40 "bad" bones
- No external files or data sources

Source: read, not executed.
