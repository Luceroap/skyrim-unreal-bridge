## Purpose
Launches Skyrim via SKSE, waits for data from the SKSE plugin, opens Unreal Editor, and optionally creates a transparent overlay of Unreal over Skyrim. The bridge allows Skyrim to be viewed through Unreal's viewport while Skyrim maintains focus.

## How it is run
Command line: `python C:\Users\Aidan\SkyrimUnrealBridge\start_bridge.py [--no-overlay] [--overlay-only] [--opacity 130]`. Called by demo.py (lines 32, 60, 61), play.py (lines 118, 149), tools/auto_build.py (line 73), tools/editor_watchdog.py (line 241), and referenced in README.md.

## Inputs
Command-line arguments (e.g., `--remaster`, `--opacity`), Skyrim's shared memory (`Local\\SkyrimUnrealBridge_v1`), Skyrim config files (SkyrimPrefs.ini, SSEDisplayTweaks.ini, CommunityShaders settings), SKSE plugin DLL.

## Outputs
Shared memory (`Local\\SkyrimUnrealBridge_v1`), `EXEC_REQ`/`EXEC_OUT` files for Unreal communication, `EXEC_LOCK` lock file, modified Skyrim config files (applied on next launch), remaster view configuration.

## Key functions
stream_frame
overlay
remaster
ue_exec
skyrim_profile
install_plugin
side_by_side

## Depends on
`remaster_watch.py`, `exec_request.py` (in `area2`), SKSE plugin (SkyrimUnrealBridge.dll), Skyrim (borderless/windowed mode), Unreal Editor.

## Gotchas
- Skyrim must be running in borderless/windowed mode.
- Remaster view requires the SkyBridgeViewLibrary C++ module.
- Config changes to Skyrim (e.g., remaster profile) apply only on next launch.
- Plugin installation requires Skyrim to be closed.
- `--remaster` mode sets Skyrim to 20 FPS minimum (via SSEDisplayTweaks.ini).

Source: read, not executed.
