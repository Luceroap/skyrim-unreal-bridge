## Purpose
Generates a CSV file (water.csv) mapping exterior cell coordinates (gx, gy) to water heights (xclw) from a Skyrim ESM file. Processes cells within a specified radius around a point, only for worldspaces explicitly listed in the input.

## How it is run
Command: `python -I esm_water.py <esm> <out.csv> <worldspaces> <cx> <cy> <radius>`. Called by `unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.cpp` line 117.

## Inputs
- ESM game data file (e.g., `Morrowind.esm`)
- Output CSV path (e.g., `area2/water.csv`)
- Comma-separated worldspaces (e.g., `skyrim,morrowind`)
- Center X coordinate (`cx`)
- Center Y coordinate (`cy`)
- Search radius (`rad`)

## Outputs
- `out.csv` with rows `gx,gy,height` (sorted by cell coordinates)
- Console output showing count of cells processed and first 8 entries (e.g., `[(gx, gy), height]`)

## Key functions
- `subs`: Parses ESM chunk headers
- `walk`: Recursively traverses ESM groups/records
- `main logic`: Filters cells by worldspace and proximity
- `xclw processing`: Handles water height values
- `output generation`: Writes CSV with sorted cells

## Depends on
- `unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.cpp` (caller)
- Python modules: `struct`, `sys`, `zlib`, `math`

## Gotchas
- Worldspaces list is case-insensitive (converted to lowercase)
- Child worldspaces require explicit inclusion; no automatic parent fallback
- Uses zlib decompression when flags & 0x40000
- Water heights outside range (-1e7 < xclw < 1e7) are skipped
- Output CSV is sorted by cell coordinates

Source: read, not executed.
