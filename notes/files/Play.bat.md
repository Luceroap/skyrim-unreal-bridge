## Purpose
This batch file launches the Skyrim-Unreal Engine bridge by executing the `play.py` script, initiating Skyrim (loading the latest save automatically) and starting the Unreal Editor in parallel for a live-view integration.

## How it is run
Executed directly as `Play.bat` or via the desktop shortcut "Play Skyrim (Unreal)". Called by `tools/make_local_queue.py`, referenced in `AGENT_BRIEFING.md` (line 31), `COORDINATION.md` (line 363), and `HANDOFF_FOR_CHATGPT.md` (line 9).

## Inputs
Command-line arguments passed to `play.py` (e.g., `--stop`).

## Outputs
None - Play.bat delegates all output handling to `play.py`; no files, folders, or shared memory are written by the batch file itself.

## Key functions
Launch play.py with arguments

## Depends on
play.py

## Gotchas
- Must not have Skyrim or UnrealEditor running before executing Play.bat (avoids duplicate processes).
- Play.bat automatically terminates existing UnrealEditor processes upon launch.
- The `--stop` argument in command line closes both Skyrim and Unreal Editor.
- Python 3.12 is required at the hardcoded path `C:\Users\Aidan\AppData\Local\Programs\Python\Python312\python.exe`.
- Manual restarting of UnrealEditor is prohibited while Play.bat is active.

Source: read, not executed.
