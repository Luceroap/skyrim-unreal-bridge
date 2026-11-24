## Purpose
This service processes model conversion requests from the Unreal editor by converting Skyrim assets (from game archives or loose files) into FBX format. It monitors `area2/requests.txt` for new asset names, converts them via Blender, and writes the results to `area2/ready.txt` or `area2/failed.txt` for the editor to import.

## How it is run
Command line: `python tools\asset_service.py` (must be left running as a background process). Called by `demo.py` (via `subprocess.Popen`), `play.py` (as part of the `asset_service.py` script in a loop), and `unreal/SkyrimBridge/live_bridge.py` (the Unreal editor script that writes to `area2/requests.txt`).

## Inputs
Model names listed in `area2/requests.txt` (one per line), with `models.json` mapping asset names to NIF paths (written by the editor during session initialization).

## Outputs
- Successfully converted FBX files in `area2/export/`.
- `area2/ready.txt` listing completed model names.
- `area2/failed.txt` listing conversion failures.
- Updates to `area2/models.json` (recreated each editor session).

## Key functions
main: Main loop processing requests and orchestrating conversions.
nif_from_asset: Unused stub function for NIF path mapping (returns empty list).

## Depends on
- `mesh_index.py` (for asset path mapping via `load()`).
- `build_area.py`, `textures.py`, `textures_pbr.py` (conversion scripts).
- `blender_export.py` (for Blender FBX export via `blender.exe`).
- Hardcoded paths (`DATA = D:\SteamLibrary\...`, `ROOT = C:\Users\Aidan\...`).

## Gotchas
- Must be kept running continuously (no exit after processing requests).
- `models.json` is rewritten per editor session; service regenerates it if missing.
- `nif_from_asset` function is present but unused (returns empty list).
- Hardcoded Windows paths (e.g., `D:\SteamLibrary`) will break if paths change.
- Requires editor (`live_bridge.py`) to populate `area2/requests.txt` before processing.

Source: read, not executed.
