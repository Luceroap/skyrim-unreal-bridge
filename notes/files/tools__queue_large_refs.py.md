## Purpose
Queues large reference models (walls, towers, castles) from a Skyrim worldspace for asset processing ahead of time. Processes Skyrim.esm to identify and map model paths for specified worldspaces.

## How it is run
Command: `python -I queue_large_refs.py [worldspace_edid]` (default: `whiterunworld`). Called by `HANDOFF_FOR_CURSOR.md`.

## Inputs
- `Skyrim.esm` (ESM file from Skyrim Special Edition)
- Worldspace EDID (e.g., `whiterunworld`, default)
- `area2/models.json` (existing model mappings)
- `area2/ready.txt` (pre-processed model names)
- `area2/failed.txt` (failed model names)

## Outputs
- `area2/models.json` (updated mapping of model names to .nif paths)
- `area2/requests.txt` (appended new model names for asset service)
- Updates `area2/ready.txt`/`area2/failed.txt` via `have` set

## Key functions
subs (data parsing)
walk (ESM structure traversal)
model filtering (space check, .nif appending)
model mapping (path normalization)
request queueing (append to requests.txt)

## Depends on
`area2/` directory structure (models.json, ready.txt, failed.txt)
`Skyrim.esm` file
`json`, `os`, `struct`, `sys`, `zlib` modules

## Gotchas
- Skips model names containing spaces
- Uses cp1252 encoding for model names
- Appends new models to requests.txt without deduplication
- Automatically adds .nif extension to models missing it
- Replaces backslashes with forward slashes in paths

Source: read, not executed.
