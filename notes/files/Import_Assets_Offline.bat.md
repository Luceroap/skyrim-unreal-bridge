## Purpose
This batch file stops Skyrim and the Unreal editor before importing all converted 3D models into Unreal. It takes approximately 2.5 hours to complete and can be safely interrupted and restarted.

## How it is run
Command line: `Import_Assets_Offline.bat [arguments]`. Called by `tools/make_local_queue.py` (referenced in its "launchers" list).

## Inputs
Command-line arguments passed to `offline_import.py` (via `%*`), such as specific asset paths or import flags.

## Outputs
Converted models written to Unreal Engine's project asset directory (exact path unknown from file context).

## Key functions
Stop Skyrim/Unreal editor
Import converted models offline

## Depends on
play.py
offline_import.py

## Gotchas
- Hardcoded user paths (C:\Users\Aidan\...) may fail if project directory moves
- Requires Skyrim and Unreal editor to be closed before execution
- Safe to interrupt and resume during execution
- Approximately 2.5 hours runtime
- Pauses with "Press any key to continue" after completion

Source: read, not executed.
