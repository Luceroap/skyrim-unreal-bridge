## Purpose
This script samples the actor stream from Skyrim for a specified duration to analyze per-NPC limb movement and check if the `npc_live._is_bind` flag is set. It visualizes whether limbs are moving relative to their rest pose and tracks binding status.

## How it is run
Command line: `python area2/probe_stream_limbs.py [seconds]` (default duration: 3.0 seconds).  
Called by `README.md` (line 324) and `COORDINATION.md` (line 110).

## Inputs
- Command-line duration argument (e.g., `5.0` for 5 seconds).  
- Real-time actor data from Skyrim via `npc_live` module (via shared memory).

## Outputs
Console output with formatted lines per NPC:  
`%08x %-22s n%3d bind %3d  armChange %5.1f  calfChange %5.1f  moved %6.1f  dist %5.0f viewAngle %5.1f`  
Includes NPC ID, name, sample count, bind count, limb angle changes, movement distance, and view angle relative to camera.

## Key functions
read_actors()  
rest_pose()  
qmul()  
qrot()  
qconj()  
_is_bind()  
skel_key()

## Depends on
npc_live.py  
sys  
time  
math  
ctypes  
struct

## Gotchas
- Uses mocked Unreal module via `sys.modules["unreal"] = types.SimpleNamespace(log=print)`.  
- Relies on specific shared memory segment `Local\\SkyrimUnrealBridge_v1`.  
- Windows-specific API calls (`OpenFileMappingW`, `MapViewOfFile`).  
- Requires Unreal bridge to be running for input data.  
- Fails if shared memory segment is missing or inaccessible.

Source: read, not executed.
