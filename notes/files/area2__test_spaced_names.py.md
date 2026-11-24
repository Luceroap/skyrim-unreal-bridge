## Purpose
Tests that models with spaces in filenames are converted to whitespace-free asset names (e.g., `clutter/dining set/basictankard01.nif` → `clutter_dining_set_basictankard01`). Verifies the request gate (blocks space-named models until `spaced_names_ok.txt` exists) and prefetch behavior.

## How it is run
Command: `python area2/test_spaced_names.py`. Called by `README.md` (line 255) and referenced in `COORDINATION.md` (line 248) as part of testing.

## Inputs
- Temporary directory (`tmp`) containing:
  - `requests.txt` (track pending requests)
  - `spaced_names_ok.txt` (flag to enable space-named models)
  - `models.json` (stored asset mappings)
  - `interiors_test.json` (test cell data with space-named models)
  - `dungeon_models.txt` (test dungeon model references)

## Outputs
- Writes to `tmp/requests.txt` (list of pending assets).
- Creates/deletes `tmp/spaced_names_ok.txt` (triggers request gate).
- Writes to `tmp/models.json` (asset → path mappings).
- Confirms via assertions (no file outputs beyond temp files).

## Key functions
`asset_name` - Converts paths to whitespace-free names.
`request` - Handles asset request queue with gate.
`prefetch_cities` - Processes model prefetching with space-name filter.

## Depends on
- `unreal/SkyBridge/live_bridge.py` (mocked via `sys.modules`).
- `area2/spaced_names_ok.txt` (required flag file).
- `models.json` (stored mappings during testing).

## Gotchas
- Requires `spaced_names_ok.txt` to be created to proceed beyond initial request.
- Requests for space-named models are blocked for 30 seconds (`Live._sp_t`).
- Prefetch skips space-named models until `spaced_names_ok.txt` exists.
- Space-named models remain in `dungeon_models.txt` until flag is set.
- `asset_name` preserves existing underscores (e.g., `old style_name` → `old_style_name`).

Source: read, not executed.
