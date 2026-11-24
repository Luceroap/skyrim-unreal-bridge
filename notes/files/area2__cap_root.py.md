## Purpose
Sets up and captures scene renders for NPCs in Unreal Engine, saving images to disk for the Skyrim-Unreal bridge. Manages scene capture actors for rendering NPC heads with configurable camera angles.

## How it is run
Command line: `python cap_root.py` (executed as a script). Other files that call it: none found via `git grep -n -I -E "cap_root\.py"`.

## Inputs
`npc_step.txt` with three space-separated lines:  
- `step[0]`: "setup", "grab", or "done"  
- `step[1]`: Comma-separated NPC labels or image prefix  
- `step[2]`: Camera X offset (e.g., "10.0")

## Outputs
PNG files in `C:\Users\Aidan\SkyrimUnrealBridge\area2\` named `<step[1]>_0.png`, `<step[1]>_1.png`, etc.  
Shared memory: `live._npc_caps` (list of captured actors).

## Key functions
setup - Configures camera and render target  
grab - Exports captured images  
done - Destroys scene capture actors  

## Depends on
`npc_live.py` (via `sys.modules["npc_live"]`)  
Unreal Engine modules (e.g., `unreal.EditorLevelLibrary`)

## Gotchas
- Hard-coded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\area2`  
- Only processes up to 3 matching NPCs (`.values()[:3]`)  
- `step[1]` must be comma-separated names for NPC matching  
- `setup` requires valid Unreal Engine actors with "NPC-Head" sockets  
- `grab` uses pre-configured `live._npc_caps`  

Source: read, not executed.
