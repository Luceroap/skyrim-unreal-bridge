## Purpose
Processes Skyrim ESM files to extract placed references (e.g., doors, furniture) within a user-specified radius of a point, filtering by a substring in their model paths. Outputs a JSON file listing NIF paths, positions, rotations, and scales for each matching reference.

## How it is run
Command: `python -I esm_area.py <esm> <out.json> <substring> <cx> <cy> <radius> [WS]`. Called by `build_area.py`, `textures.py`, and `blender_export.py` as part of the area processing pipeline.

## Inputs
ESM file path, output JSON file, model substring filter, center X/Y coordinates (cx, cy), radius (ESM units), optional world name (WS).

## Outputs
JSON file (e.g., `whiterun/area.json`) containing arrays of objects with keys `nif`, `pos`, `rot`, `scale`. Example: 155 unique NIFs, 417 placements as per README.

## Key functions
subs - Decomposes ESM sub-chunks  
walk - Processes ESM structure recursively  
Main logic - Filters and formats results

## Depends on
None (relies solely on standard Python libraries).

## Gotchas
- Radius in 100-unit ESM coordinates (e.g., 6500 = 65 meters)  
- Model paths converted to lowercase with forward slashes  
- Includes 12 base types (e.g., TREE, FLOR), not just 5 in docstring  
- Skips references with 'hidden' flag (flags & 0x20)  
- Positions rounded to 1 decimal for uniqueness  

Source: read, not executed.
