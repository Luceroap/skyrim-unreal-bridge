## Purpose
Adjusts Unreal Editor settings to maximum quality for showcase screenshots, enabling ray-traced Lumen lighting, high-resolution Nanite, dense global illumination, and reflection tracing. Reverts settings to everyday quality when the `--off` flag is provided.

## How it is run
Command: `python tools/max_quality.py` (applies max settings) or `python tools/max_quality.py --off` (reverts to everyday settings). Called by `tools/perf_profile.py` (with `--off`) and `tools/shot_session.py` (without `--off`).

## Inputs
Command line flag `--off` (optional; triggers everyday settings).

## Outputs
Modifies live Unreal editor settings via console commands (no disk files or shared memory written). Prints confirmation: `applied <count>`.

## Key functions
ue_exec: Runs Unreal console commands via bridge.
MAX string: Contains all max quality console variables.
off logic: Switches between max and everyday settings.

## Depends on
start_bridge.py (imports ue_exec for console command execution).

## Gotchas
- Settings are session-only (revert on editor restart).
- `--off` uses predefined everyday settings, not project defaults.
- `shot_session.py` runs `max_quality.py` without `--off` on startup.
- Requires running Unreal editor with bridge connection.
- `r.ScreenPercentage 200` doubles resolution (high GPU usage).

Source: read, not executed.
