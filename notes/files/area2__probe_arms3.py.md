## Purpose
This script inspects the left arm bone hierarchy and animation state of a specific NPC (Aela) in Skyrim's animation system. It verifies bone positions and relationships within the current animation plan.

## How it is run
Executed directly via command line (e.g., `python area2/probe_arms3.py`). No other files in the project call this script (confirmed by empty `git grep` results for `probe_arms3.py`).

## Inputs
- NPC animation state via `nl._state["actors"]` (specifically actor labeled "Aela")
- Bone names hardcoded in script (e.g., "NPC L Clavicle [LClv]")

## Outputs
Console output showing:
- Bone names and their presence in animation plan/stream
- Parent bones
- Bone transform translations (x/y/z coordinates rounded to 1 decimal)
- Socket locations for bones
- Sorted list of arm-related bone names in the animation plan

## Key functions
`get_bone_transform_by_name` - Retrieves bone position in component space  
`get_parent_bone` - Gets parent bone of target bone  
`get_socket_location` - Fetches socket position  
`ue_bone` - Converts bone name to Unreal engine bone reference  
`next` - Finds first matching actor with "Aela" in label  

## Depends on
`area2/npc_live.py` (imports `nl.sys.modules["npc_live"]`)  
`unreal.py` (uses `unreal.BoneSpaces.COMPONENT_SPACE`)  

## Gotchas
- Hardcoded to Aela's animation (fails if actor not present)
- Relies on specific Skyrim bone naming convention
- Bone name format matches Skyrim's "NPC L Clavicle [LClv]" style
- No callers found in project (standalone debug tool)
- Requires Unreal Engine bone space API

Source: read, not executed.
