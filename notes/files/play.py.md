## Purpose
A one-click launcher that starts Skyrim (loading the latest save) and the Unreal editor in parallel, ensuring the Unreal view is positioned over Skyrim and Skyrim retains keyboard focus. It manages dependency processes, handles weather settings, and cleans up stale background tasks.

## How it is run
Command line: `python play.py` (starts both applications), `python play.py --stop` (closes both cleanly). Called by `Play.bat`, `Stop.bat`, and `tools/shot_session.py` (via `subprocess.run([sys.executable, "play.py"])`).

## Inputs
Command-line arguments: `--stop` (closes), `--keep-weather` (preserves weather), `--no-autobuild` (skips character/creature building). Requires SkyrimSE.exe and UnrealEditor.exe to be installed at configured paths.

## Outputs
- Logs to `unreal/SkyBridge/Saved/Logs` (e.g., `SkyBridge.log`).
- Shared memory segment `SkyrimUnrealBridge_actors_v1` (used by Skyrim/Unreal bridge).
- Modifies `SKSE/Plugins/SkyrimUnrealBridge.sky` (weather/texture settings).
- Creates process dependencies (e.g., `asset_service.py`, `npc_autobuild.py`).

## Key functions
say - Timestamped console messages.
running - Checks if process is running via `tasklist`.
kill - Terminates processes via `taskkill`.
kill_watchers - Stops lingering Python scripts.
start_services - Launches background converters.
free_gb - Checks available RAM.
skyrim_in_world - Verifies Skyrim is loaded.
editor_live - Confirms Unreal editor is ready.
focus_skyrim - Gives Skyrim keyboard focus.
stop - Cleansly shuts down processes.
main - Orchestrates full startup sequence.

## Depends on
`start_bridge.py` (for Skyrim startup), `asset_service.py` (3D model conversion), `tamriel_terrain.py` (terrain chunks), `npc_autobuild.py` (NPC model builder), SKSE plugins directory (`SKSE/Plugins`).

## Gotchas
- Requires ≥8GB free RAM (warning if below).
- `--keep-weather` prevents weather reset during launch.
- Automatically kills duplicate UnrealEditor.exe processes.
- Must run from project root (uses `os.path.dirname(__file__)`).
- Skyrim must be started via `play.py` (not manually) to avoid conflicts.

Source: read, not executed.
