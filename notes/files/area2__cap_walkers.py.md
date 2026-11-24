## Purpose
Captures side-view close-ups of up to three walking NPCs at 0.5-second intervals using Unreal Engine's rendering system. Saves two frames per NPC as PNG files and generates a position report.

## How it is run
Invoked automatically by `area2/reload_npc_keep.py` during live hot-reload sessions (via `COORDINATION.md` reference). Not a standalone executable; triggered when NPC state updates.

## Inputs
Live NPC state data from `npc_live` module (accessible via `nl._state["actors"]`), including bone counts, speed values (`e.get("speed", 0)`), and positions.

## Outputs
- `area2/walkers_<k>_<i>.png` (two frames per NPC, `k=0`/`1`, `i=0`-`2`)
- `area2/walkers_report.txt` (lines with bone positions, frozen state, and walkloop data)

## Key functions
_cb: Handles frame capture intervals and logs positions.
spawn_actor_from_class: Spawns scene capture actors.
export_render_target: Saves rendered images to disk.
get_socket_location: Retrieves bone coordinates.
destroy_actor: Cleans up capture actors.

## Depends on
`npc_live.py` (accesses `nl._state["actors"]`), Unreal Engine's `EditorLevelLibrary` and `RenderingLibrary`.

## Gotchas
- Hardcoded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\area2` (blocks non-Windows use).
- Strictly limits to 3 NPCs via `[:3]` (no configuration).
- Frame capture timing is fixed (1.0s then 1.5s after start).

Source: read, not executed.
