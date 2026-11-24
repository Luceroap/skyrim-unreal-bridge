## Purpose
Optimizes Skyrim's performance for the Unreal bridge by disabling rendering features like shadows, grass, and water effects. The script rewrites SkyrimPrefs.ini to reduce GPU load while Unreal handles visual rendering.

## How it is run
Command-line: `python tools/skyrim_lightweight.py` (applies settings, creates backup) or `python tools/skyrim_lightweight.py --undo` (restores backup). No other project files call it (grep shows only itself in comments).

## Inputs
SkyrimPrefs.ini at `C:\Users\Aidan\OneDrive\Documents\My Games\Skyrim Special Edition\SkyrimPrefs.ini`.

## Outputs
Modified `SkyrimPrefs.ini` file and backup `C:\Users\Aidan\SkyrimBackups\SkyrimPrefs.pre-lightweight.ini`.

## Key functions
running - Checks if Skyrim process is active.
set_keys - Updates config values in SkyrimPrefs.ini.

## Depends on
Standard Python modules (os, re, shutil, subprocess, sys, time), SkyrimPrefs.ini path.

## Gotchas
- Skyrim must be closed before running (script exits if active).
- Backup path is hardcoded to `C:\Users\Aidan\...` (user-specific).
- `--undo` requires the backup file to exist.
- Modifies specific settings: `fShadowDistance=0.0000`, `iTexMipMapSkip=3`, etc.
- Backup created only if it does not exist (via `os.makedirs`).

Source: read, not executed.
