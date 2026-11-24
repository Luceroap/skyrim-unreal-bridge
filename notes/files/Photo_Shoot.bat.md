## Purpose
The Photo_Shoot.bat batch file stops the local model, launches Skyrim and Unreal Engine at showcase quality settings, and enables hotkeys (F8 for 4K, F9 for 8K, F5 for time of day, F6 for weather, F7 for release) to capture screenshots. The generated photos are saved in the `screenshots\photos` directory.

## How it is run
Executed directly as `Photo_Shoot.bat` from the command line. No other project files call it (git grep results show only documentation references in `AGENT_BRIEFING.md`).

## Inputs
None.

## Outputs
Photos saved to `screenshots\photos` (relative to project root at `C:\Users\Aidan\SkyrimUnrealBridge\screenshots\photos`).

## Key functions
- shot_session.py (with --max flag)
- photo_keys.py (handles hotkey bindings)

## Depends on
- tools\shot_session.py
- tools\photo_keys.py

## Gotchas
- Hardcoded absolute path in `cd` command (`C:\Users\Aidan\SkyrimUnrealBridge`), may fail for users with different paths.
- 'pause' command requires manual Enter keypress to close window.

Source: read, not executed.
