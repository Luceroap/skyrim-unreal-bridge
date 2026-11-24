## Purpose
Analyzes bone transformation data for the NPC named "Aela" in the Skyrim-to-Unreal bridge, specifically printing scale and rotation values for bones matching predefined patterns.

## How it is run
Command line: `python area2/probe_rot.py`. No other files call it (git grep returned no results).

## Inputs
Runtime actor data from `npc_live` module (specifically the actor labeled "Aela" in `e["actor"].get_actor_label()`).

## Outputs
Console output formatted as:
`[index] [bone name] scale (x y z) rot (x y z w) ref (q1 q2 q3)`

## Key functions
- Get actor data via npc_live module
- Iterate bone indices from component
- Skip bones without filter keywords
- Retrieve bone transforms
- Print formatted transform data

## Depends on
npc_live.py (via `sys.modules["npc_live"]`), unreal.py (via `unreal.BoneSpaces.COMPONENT_SPACE`)

## Gotchas
- Hardcoded NPC name "Aela" may fail if NPC label changes
- Only analyzes bones containing specific substrings (Root, Pelvis, etc.)
- Bone name filters use substring matching (may miss exact matches)
- Skips bones with no rest rotation data (`rq`/`rt`)

Source: read, not executed.
