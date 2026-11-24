## Purpose
Debugging tool for analyzing NPC bone scale and transform data in the Skyrim-Unreal bridge. Outputs pose timing and socket scale values for specific anatomical points.

## How it is run
Executed directly as a Python script (e.g., `python probe_scale.py`). No other project files reference it (grep results show no callers).

## Inputs
- `npc_live` module state with an NPC named "Carlotta" in `_state["actors"]`.

## Outputs
- Prints time since posing, "rest0v" presence check, number of scales, and socket transform data (scale, location, reference scale) for bone sockets.

## Key functions
- `c.get_socket_transform` retrieves socket transforms.
- `e.get` accesses event data.
- `time.time()` measures time elapsed.

## Depends on
- `npc_live.py` (via sys.modules["npc_live"]).
- Python standard libraries `sys`, `time`.

## Gotchas
- Hardcoded to "Carlotta" NPC; fails if missing.
- Assumes specific socket names exist ("NPC", "NPC-Pelvis-...", etc.).
- Uses `next(e for ...)` which crashes if Carlotta not present.
Source: read, not executed.
