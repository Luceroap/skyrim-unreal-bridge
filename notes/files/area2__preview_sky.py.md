## Purpose
This script reads the `area2/preview.txt` file to dynamically set in-editor sky time and weather overrides, or revert to Skyrim's default when `preview.txt` contains `off`.

## How it is run
Executed as a standalone Python script (`python preview_sky.py` in `area2/`). No other project files reference it (confirmed by `git grep` search for `preview_sky.py` showing no results).

## Inputs
- `area2/preview.txt` containing either:
  - `off` (to revert to Skyrim's default)
  - `<hour> <weather name>` (e.g., `12.5 SkyrimClear`)

## Outputs
- Modifies `live._sky_override` (a global tuple or `None`)
- Prints `override <value>` to console
- No file/folder writes (only memory changes)

## Key functions
- Read preview.txt contents
- Parse hour/weather from preview.txt
- Set live._sky_override
- Default to 'SkyrimClear' for weather
- Handle 'off' mode

## Depends on
- `live` module (not a file import; assumed to be defined externally)

## Gotchas
- Hardcoded Windows path (`C:\Users\Aidan\...`) will fail on other OS or users
- Missing weather name defaults to `'SkyrimClear'` instead of erroring
- Assumes `live` module is available at runtime
- No error handling for non-numeric hours
- Uses `float(a[0])` without validation

Source: read, not executed.
