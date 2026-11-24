## Purpose
This script analyzes Skyrim ESM files to count placed references (e.g., objects or actors) in a specified worldspace based on persistence type (persistent vs. temporary cell children). It filters results by model name substrings and optionally by location.

## How it is run
Command: `python -I tools/esm_persistence.py <esm> <worldspace_edid> <model_substring> [cx cy radius]`. Called by `HANDOFF_FOR_CURSOR.md` (line 137) as part of diagnostics.

## Inputs
- ESM file path (`<esm>`)
- Worldspace EDID (`<worldspace_edid>`, case-insensitive)
- Model substring (`<model_substring>`, case-insensitive)
- Optional: center coordinates (`cx cy`) and radius (`radius`)

## Outputs
Printed to stdout: reference counts by group (e.g., persistent, temporary), followed by top 25 models per group with counts.

## Key functions
walk - Traverses ESM file structure to identify worldspaces and references  
subs - Parses sub-headers in compressed data chunks  
model_count - Aggregates reference counts by persistence group and model

## Depends on
Standard libraries (collections, math, struct, sys, zlib); no other project files.

## Gotchas
- Model substring matching is case-insensitive (converted to lowercase).  
- Default radius of 1e9 covers entire worldspace when not specified.  
- Compressed data chunks use zlib.decompress (checked via flags & 0x40000).  
- Worldspace EDID comparison is case-insensitive (converted to lowercase).  
- Radius calculation uses Euclidean distance (math.hypot).  

Source: read, not executed.
