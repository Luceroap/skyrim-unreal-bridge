## Purpose
Automates starting the Skyrim asset converter, terrain service, Skyrim game, and Unreal editor with the live bridge script. Configures the remaster view optionally to render Skyrim scenes through Unreal's viewport.

## How it is run
Command line: `python demo.py` or via `Launch_Demo.bat`. Called by `start_bridge.py` (via `COORDINATION.md`), desktop shortcut "Skyrim Unreal Demo", and superseded by `play.py` (as noted in `HANDOFF_FOR_CURSOR.md`).

## Inputs
Command-line argument `--no-remaster` skips remaster view configuration. No other inputs are explicitly handled.

## Outputs
Writes logs to `unreal/SkyBridge/Saved/Logs/SkyBridge_*.log` (e.g., `SkyBridge_2.log`). Starts processes: `asset_service.py`, `tamriel_terrain.py`, `skyrimse.exe`, `UnrealEditor.exe`.

## Key functions
procs - Lists all running processes  
running - Checks if process text appears in command line  
editor_log - Finds newest SkyBridge log with active bridge  

## Depends on
Imports: subprocess, sys, os, re, time. Calls: `tools/asset_service.py`, `tools/tamriel_terrain.py`, `start_bridge.py`.

## Gotchas
- Checks for existing UnrealEditor.exe and skips restart to avoid RAM exhaustion (two editors caused 0.1 GB RAM usage).  
- Waits up to 300 seconds for live bridge log entry matching `[SkyBridgeLive] alive: [1-9]\d* actors`.  
- Skips Skyrim start if `skyrimse.exe` is detected.  
- `-no-remaster` flag prevents `start_bridge.py --remaster` execution.  
- Existing UnrealEditor.exe processes prevent duplicate launches (user must check `tasklist | find UnrealEditor`).

Source: read, not executed.
