## Purpose
Disables unnecessary SKSE plugins (physics/visual-only) by moving their DLLs to `_disabled_for_bridge`, reducing CPU/GPU overhead during bridge operation. Does not delete files; tracks disabled plugins via `moved.json`.

## How it is run
Command line: `python tools/skyrim_plugins.py` (disables plugins) or `python tools/skyrim_plugins.py --restore` (restores plugins). Called from `COORDINATION.md` (line 284) and `README.md` (line 293).

## Inputs
- SKSE plugin directory path (`D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data\SKSE\Plugins`).
- List of plugins to disable (`DISABLE` variable).
- Current presence of plugins in the SKSE Plugins folder.
- Whether Skyrim is running (checked via `tasklist`).

## Outputs
- Moves DLLs from `SKSE\Plugins` to `SKSE\Plugins\_disabled_for_bridge`.
- Updates `SKSE\Plugins\_disabled_for_bridge\moved.json` with sorted list of disabled plugin names.
- Prints status messages ("disabled" or "restored").

## Key functions
sys.exit
os.makedirs
shutil.move
json.load
json.dump
subprocess.run
print
sorted
set
open

## Depends on
Imports: `json`, `os`, `shutil`, `subprocess`, `sys`. Referenced in `COORDINATION.md` and `README.md`.

## Gotchas
- Skyrim must be closed (DLLs locked while running).
- Hardcoded SKSE plugin path (`D:\SteamLibrary\...`).
- `DISABLE` list explicitly excludes `hdtSMP64`, `SMP-NPC`, and `cbp`.
- `--restore` clears `moved.json` entirely.
- Files are moved, never deleted.

Source: read, not executed.
