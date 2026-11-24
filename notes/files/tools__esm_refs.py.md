## Purpose
Finds placed references (REFR) in Skyrim.esm that use specific NIF meshes (by path tail). Outputs reference positions, rotations, and scale for matching meshes to enable accurate placement in Unreal Engine.

## How it is run
Command: `python -I tools/esm_refs.py Skyrim.esm out.json wrhouse02.nif ...`  
Called by: `README.md` (via "Whiterun mesh export" section) and `unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.cpp` (comment line 51).

## Inputs
- `Skyrim.esm`: Skyrim's main ESM file (binary)
- `out.json`: Output path for JSON results
- NIF path tails (e.g., `wrhouse02.nif`), converted to lowercase for case-insensitive matching

## Outputs
- `out.json`: JSON array of references with format:
  ```json
  [{"nif": "wrhouse02.nif", "pos": [x,y,z], "rot": [rx,ry,rz], "scale": s}]
  ```
- Command-line print: `len(stat_nif) STATs matched, len(res) placed refs`

## Key functions
sub_records: Iterates over subrecord headers and bodies  
walk: Recursively processes ESM data structure  
process_references: Filters and formats matched references  

## Depends on
None (only standard libraries: `struct`, `sys`, `zlib`, `json`)

## Gotchas
- Case-insensitive NIF matching (all path tails lowercased)  
- Skips deleted references (flags & 0x20)  
- Output `nif` field contains lowercase filename tail including extension (e.g., `wrhouse02.nif`)  
- Handles compressed STAT records via zlib (flags & 0x40000)  
- Does not output full NIF paths, only lowercase path tails  

Source: read, not executed.
