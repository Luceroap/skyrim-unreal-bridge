## Purpose
Waits for the offline asset import process to complete, closes all related application processes (Unreal Editor, Skyrim, Blender), and initiates a 2-minute PC shutdown countdown.

## How it is run
Command: `python tools/shutdown_after_import.py [--no-shutdown] [--max-hours 4]`. No other project files call this script; the only reference is in its own docstring (confirmed via `git grep`).

## Inputs
Command-line arguments: `--no-shutdown` (prevents shutdown), `--max-hours` (max wait time for import in hours, default 4.0).

## Outputs
Writes log entries to `area2/shutdown_after_import.log`. Reads `area2/offline_import.log` for import status. Triggers system shutdown after 120 seconds (cancelable via `shutdown /a`).

## Key functions
say - Logs timestamped messages.
import_running - Checks for import-related processes.
last_line - Fetches last line of offline import log.

## Depends on
None (uses standard libraries only).

## Gotchas
- Waits max 4 hours (default) for import to complete before proceeding.
- Requires import process to contain "offline_import" in command line or match "UnrealEditor-Cmd.exe" name.
- Hardcoded 120-second delay after import completion before process termination.
- Shutdown can be canceled with `shutdown /a` during 120-second countdown.
- Default max-hours (4) may be too short for large asset imports.

Source: read, not executed.
