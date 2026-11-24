## Purpose
This script diagnoses NPC animation states by comparing bone rotations against their rest poses. It measures angular deviations in degrees for limbs to identify potential animation issues.

## How it is run
Command: `python tools/debug/npc_diag2.py`  
Other files: None (git grep shows no caller references).

## Inputs
- `npc_live._state["actors"]` (current NPC actor data)
- `npc_live.read_actors()` (retrieves actor list)

## Outputs
- Console output listing each NPC actor's label, readiness status, bone count, and maximum rotation angle deviation from rest pose.

## Key functions
- ue_bone: Retrieves Unreal bone name from string
- mul: Multiplies matrices
- quat_to_mat: Converts quaternion to 3x3 matrix
- tr: Transposes matrix

## Depends on
- tools/debug/npc_live.py (imports `_state` and bone access utilities)

## Gotchas
- Hardcoded Windows path in sys.path.insert (C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge)
- Requires Unreal Engine runtime (uses `unreal` module)
- Outputs only to console with no file logging
- Relies on `npc_live._state` being populated before execution
- Uses fixed bone name strings (e.g., "NPC L UpperArm [LUar]") for checks

Source: read, not executed.
