## Purpose
Monitors and logs actor pose transition rates and movement data over a 4-second interval for performance analysis and debugging in the Skyrim-Unreal bridge.

## How it is run
Automatically loaded via `import` in the NPC live module (not command-line). No callers found via `git grep` for `probe_pose_rate.py`.

## Inputs
- Runtime state from `npc_live._state` (actors, poses, walk data, sequence ID).
- Unreal Engine's post-tick callback system (`unreal.register_slate_post_tick_callback`).

## Outputs
- `area2/pose_rate.txt` (overwritten every 4 seconds):
  - FPS, sequence ID, walk buffer sizes, loop durations, and per-actor data (poses/s, distance, frozen status, speed, walk phase).

## Key functions
_cb - Tracks pose transitions and resets counter after 4 seconds.
register_slate_post_tick_callback - Registers the callback with Unreal.
unregister_slate_post_tick_callback - Stops the callback after 4 seconds.

## Depends on
- `npc_live` (accessed via `sys.modules["npc_live"]`).
- Unreal Engine's `unreal` module.

## Gotchas
- Callback runs for exactly 4 seconds before unregistering.
- Hard-coded Windows absolute path `C:\Users\Aidan\...` in output file.
- Output is written once per execution (not continuous logging).
- Relies on `npc_live` module being initialized (fails if missing).
- Writes only after 4 seconds of runtime (not on demand).

Source: read, not executed.
