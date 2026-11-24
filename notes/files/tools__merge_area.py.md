## Purpose
Merges runtime truth (player-encountered objects with mods/transformations) with Skyrim's base ESM references for Whiterun area, prioritizing live data within COVER radius of dump centers and filling gaps with ESM references.

## How it is run
Command: `python -I merge_area.py <out.json> <refs_all.tsv> <centers.txt> <area_esm.json> [cover=6000]`  
Called by `tools/auto_build.py` (line 32).

## Inputs
- `out.json`: Output JSON file path
- `refs_all.tsv`: Runtime truth dump (TSV)
- `centers.txt`: Dump center coordinates (one per line, space-separated floats)
- `area_esm.json`: Base ESM references JSON
- `cover=6000` (optional): Radius for live data coverage (default 6000.0)

## Outputs
- `out.json`: Merged JSON array of objects with `nif`, `pos`, `rot`, `scale`
- Console: `merged: <live> live refs + <esm> game-file refs (outside <centers> covered spots) = <total>`
- Console: `unique models: <count>`

## Key functions
`parse_centers`: Reads centers from centers.txt into coordinate list  
`process_truth`: Filters TSV into valid model references using INCLUDE/EXCLUDE rules  
`merge_esm`: Adds ESM references not overlapping live data within 40 units  
`write_output`: Serializes merged data to out.json

## Depends on
`tools/auto_build.py`

## Gotchas
- Hard-coded INCLUDE paths require models to start with specific prefixes (e.g. "architecture/")
- Hard-coded EXCLUDE patterns skip models containing "lod", "marker", etc.
- ESM references are skipped if within 40 units of a live reference for same model
- TSV requires ≥13 fields and skips lines with 12th field "1" or duplicate models
- TSV is processed with `latin1` encoding

Source: read, not executed.
