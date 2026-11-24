## Purpose
Checks which models from Skyrim's live world stream are missing or in an inconsistent state in Unreal Engine. Categorizes each model by its conversion status (e.g., missing, failed, requested) and counts reference occurrences.

## How it is run
Command: `python tools\stream_coverage.py [filter]`. Called from `HANDOFF_FOR_CURSOR.md` as a diagnostic tool.

## Inputs
- Memory-mapped data from Skyrim's `Local\\SkyrimUnrealBridge_world_v1`
- `area2/ready.txt`, `area2/failed.txt`, `area2/requests.txt` (text files listing converted/failed/requested models)
- Unreal Engine model files in `unreal/SkyBridge/Content/Area2/*.uasset`

## Outputs
- Console output listing missing models with status (e.g., "FAILED to convert", "never requested")
- Summary line: `refs by status: {dict} total refs X models Y`

## Key functions
memory_mapping_access
model_name_processing
status_categorization
reference_counting
filter_application
output_printing

## Depends on
- `area2/ready.txt`
- `area2/failed.txt`
- `area2/requests.txt`
- Unreal Engine `Area2` model files (`*.uasset` in `Content/Area2`)
- Memory-mapped shared data `Local\\SkyrimUnrealBridge_world_v1`

## Gotchas
- Fails immediately if memory map `Local\\SkyrimUnrealBridge_world_v1` is unavailable
- Skips models with spaces in filenames (marked as "SKIPPED (space in name)")
- Uses `latin1` encoding for model names (may fail on non-ASCII names)
- Requires `area2/ready.txt`, `failed.txt`, `requests.txt` to exist
- Filter argument matches case-insensitively

Source: read, not executed.
