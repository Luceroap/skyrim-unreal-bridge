## Purpose
This script controls night mode effects in the Skyrim-Unreal bridge project by adjusting lighting parameters based on the state stored in `night_mode.txt`. It triggers a screenshot request when activated and resets settings when deactivated.

## How it is run
Executed via command line (e.g., `python area2/night_test.py`). No other files in the project call this script, as confirmed by empty `git grep` results for `night_test.py`.

## Inputs
`area2/night_mode.txt` (must contain "on" or "off" string, read-only).

## Outputs
- Creates `area2/shot_request.txt` (empty file) when `night_mode.txt` is "on".
- Modifies `live.night_mid` scalar parameters (Night, Aurora, Intensity).
- Sets `live._night_test = True` when enabled.
- Resets `live._sky_key` to `None` when disabled.

## Key functions
Read night_mode.txt state
Set night lighting parameters
Generate shot_request.txt
Reset sky key on disable
Adjust intensity for off mode

## Depends on
`live.py` (for `night_mid` and `_night_test`), `area2/night_mode.txt`.

## Gotchas
Hard-coded Windows absolute paths (C:\Users\Aidan...).
Non-"on" `night_mode.txt` content defaults to off behavior.
Overwrites `shot_request.txt` without backup.
No error handling for missing `night_mode.txt`.
Uses `set_scalar_parameter_value` without validation.

Source: read, not executed.
