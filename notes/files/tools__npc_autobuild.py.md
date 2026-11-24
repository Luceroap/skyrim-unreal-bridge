## Purpose
This script builds FBX files for new NPCs or creatures near the player every 15 seconds while Skyrim is running. It runs in the background, started by play.py after Skyrim loads, and automatically stops when Skyrim closes. Build attempts are logged to a dedicated log file.

## How it is run
Command line: `python -I tools/npc_batch.py 3 --autobuild` (with working directory set to project root).  
Other files that call it: `play.py` (line 138).

## Inputs
- Skyrim process status (checked via `tasklist`)
- Current working directory (project root: `C:\Users\Aidan\SkyrimUnrealBridge`)
- None from command line

## Outputs
- Logs to `area2/npc/autobuild.log` (format: `HH:MM:SS\n<output line>`)
- Triggers FBX builds via `npc_batch.py --autobuild`
- No direct file writes beyond the log

## Key functions
skyrim_running - Checks for SkyrimSE.exe process in tasklist output
main_loop - Runs subprocess command every 15 seconds while Skyrim is active
log_write - Appends timestamps and build output to log file

## Depends on
- `npc_batch.py` (called with arguments `3 --autobuild`)
- Standard libraries: `os`, `subprocess`, `sys`, `time`
- Project root path `C:\Users\Aidan\SkyrimUnrealBridge`

## Gotchas
- Only logs when "building" appears in `npc_batch.py` output
- Uses `creationflags=0x08000000` (hidden console window)
- Checks Skyrim process status on every loop iteration
- Builds occur for any new actor within player vicinity (not just specific types)
- Sleeps exactly 15 seconds between build attempts

Source: read, not executed.
