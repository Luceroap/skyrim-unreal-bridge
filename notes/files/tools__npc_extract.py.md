## Purpose
This script extracts character skeleton and base body NIF files (and optionally additional NIFs) from Skyrim's Data directory (including loose files and BSA archives) and places them in the specified area directory under `npc/nif`. It handles face data by searching for baked head data (face, hair, eyes, brows, beard) and face tint based on a face ID.

## How it is run
Command line: `python -I npc_extract.py <data_dir> <area_dir> [extra nif paths ...]`  
Example: `python -I npc_extract.py C:\Skyrim\Data C:\Skyrim\Areas\Area01 meshes\armor\iron\f\cuirass_0.nif`  
Files that call it: `tools/npc_build.py` (lines 25, 50), `tools/npc_build_creature.py` (line 25).

## Inputs
- `data_dir`: Path to Skyrim's Data directory (contains loose files and BSA archives).
- `area_dir`: Path to the area directory (output goes to `area_dir/npc/nif`).
- Optional extra NIF paths (relative to `data_dir`), such as `meshes\armor\iron\f\cuirass_0.nif` or `face:12345678`.

## Outputs
- Extracted NIF files written to `area_dir/npc/nif` (preserving directory structure relative to `meshes`).
- For each extracted file, prints the relative path (from `data_dir`), file size, and source (loose or BSA archive) to stdout.
- Output path for `meshes\actors\character\skeleton.nif` becomes `npc/nif/actors/character/skeleton.nif`.

## Key functions
- Process face: Handles extraction of baked face data (face, hair, eyes, brows, beard) and face tint for a given face ID.
- Extract NIF: Locates and writes NIF files from loose files or BSA archives to the output directory.
- Sort archives: Sorts BSA archives to process mod archives before vanilla (to respect mod overrides).

## Depends on
- `bsa.py` (for reading BSA archives)
- `glob`, `os`, `sys` (standard libraries)

## Gotchas
- Face ID in `face:<hex>` must be 8 digits (zero-padded, e.g., `face:00001234`).
- Script uses backslashes in paths and expects input NIF paths to use backslashes.
- Mod BSA archives are processed before vanilla ones to apply mod overrides.
- Output path removes the `meshes` prefix (e.g., `meshes\actors` becomes `actors`).
- Missing files are skipped and printed to stdout (no error exit).

Source: read, not executed.
