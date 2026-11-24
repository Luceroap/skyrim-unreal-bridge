## Purpose
Converts Skyrim reference dumps (TSV files) into a JSON format consumed by `build_area.py` to generate Unreal Engine area data. Merges multiple dumps while de-duplicating entries by reference ID.

## How it is run
Command: `python -I truth_to_area.py <refs.tsv> <out.json>`.  
Invoked by `build_area.py` (via `README.md` instructions) to merge references from different in-game locations (e.g., `dump1.tsv`, `dump2.tsv`) into a unified JSON output.

## Inputs
- One or more TSV files containing Skyrim reference data (e.g., `dump1.tsv`, `dump2.tsv`).
- Output JSON filename (e.g., `out.json`).

## Outputs
- JSON file with processed data structure:  
  `{"nif": "path/to/model.nif", "pos": [x, y, z], "rot": [rx, ry, rz], "scale": float}`
- Console output: `len(res) refs, len(cnt) unique models` followed by top 8 most common model paths.

## Key functions
de_duplication  
path_filtering  
coordinate_parsing  
multi_tsv_merging  
json_output  

## Depends on
`build_area.py` (caller), `README.md` (workflow description), `SkyrimUnrealBridge_refs.tsv` (input source files).

## Gotchas
- Skips entries where `f[11] == "1"` (likely a flag for inactive entries).
- Uses Latin-1 encoding for TSV reading.
- Excludes paths matching `EXCLUDE` terms (e.g., `lod`, `marker`).
- Requires TSV entries to have ≥13 columns (skips invalid lines).
- Path checks are case-insensitive (converts to lowercase).

Source: read, not executed.
