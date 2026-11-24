## Purpose
This script serves as a diagnostic tool to monitor real-time NPC data synchronization between Skyrim and Unreal Engine. It measures performance metrics like actor read times, pose calculation latency, and stream update rates to validate the bridge's data flow consistency.

## How it is run
Command line: `python area2/probe_npc.py`. Other files calling it: unsure (grep output not provided).

## Inputs
Live NPC data via `npc_live._state` (e.g., `st["actors"]` with actor ID mappings, flags, and positions).

## Outputs
Console logs including:
- NPC count and labels (`npcs: [count] [labels]`)
- `read_actors` timing (`read_actors X.X ms`)
- Per-NPC pose calculation times (`pose per npc ms: [X.X]`)
- Stream update count in 1 second (`stream updates in 1 s: X`)
- Actor speeds (`  [name] speed X u/s`)
- Frame delta time (`frame dt (live): X.X`)

## Key functions
read_actors
_pose
stream_update_check
actor_speed_measurement
frame_dt_display

## Depends on
npc_live.py (via `sys.modules["npc_live"]`)
live_bridge.py (imported as `lb`)

## Gotchas
- Requires `npc_live` module to be loaded; missing module causes script failure.
- Uses `ctypes` to access raw memory (`ctypes.string_at`), risking crashes on invalid pointers.
- Fixed `time.sleep(0.002)` may miss high-frequency stream data.
- Sequence number checks (`s & 1`) assume even-numbered streams are valid.

Source: read, not executed.
