## Purpose
This script creates a persistent index of all mesh assets (from BSA archives and loose files) to map asset names to NIF paths. It ensures model references remain valid even when the dynamic `area2/models.json` file is overwritten by editors.

## How it is run
Command line: `python tools/mesh_index.py` (outputs to `area2/mesh_index.json`). No other files call this script (confirmed via `git grep` showing only the docstring reference).

## Inputs
- Skyrim's Data directory: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data` (contains `.bsa` archives and `meshes/` loose files).

## Outputs
- `area2/mesh_index.json` (JSON file mapping asset names to normalized NIF paths).

## Key functions
- `key`: Converts relative path to lowercase asset name with slashes replaced by underscores.
- `build`: Gathers all mesh paths from BSA archives and loose files (loose files override BSA).
- `load`: Reads index from file or generates it via `build()`.

## Depends on
- `bsa.py` (for BSA archive handling)
- Skyrim Data directory structure at `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`

## Gotchas
- Loose files override BSA entries due to processing order (loose files processed after BSA).
- Broken BSA archives are silently skipped during processing.
- Asset names are case-normalized to lowercase with `/` replaced by `_`.

Source: read, not executed.
