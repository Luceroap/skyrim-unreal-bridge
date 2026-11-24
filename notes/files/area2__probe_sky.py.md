## Purpose
Outputs current sky parameters (elevation, weather types) and night/aurora settings for debugging purposes. Logs interior state if present.

## How it is run
Manually executed via `python area2/probe_sky.py`. No other files in the project call it, as confirmed by `git grep` (no results).

## Inputs
- `live._sky_key` (sky key tuple)
- `live._interior` (optional, from `getattr(live, "_interior", None)`)
- `live.night_mid` (night-time settings object)

## Outputs
Console output showing:
- "sky key (elev, fam, wet, snow, rain): [value] interior [value]"
- "night [value] aurora [value]" (or `None` if `live.night_mid` missing)

## Key functions
get_scalar_parameter_value
getattr

## Depends on
None (no imports; relies entirely on `live` object context)

## Gotchas
- Not integrated into automated workflow (no callers found via `git grep`)
- Outputs to console only (no log file or persistent storage)
- Fails silently if `live` object or attributes are missing
- Assumes `live.night_mid` has `get_scalar_parameter_value` method
- No error handling for missing `live` attributes

Source: read, not executed.
