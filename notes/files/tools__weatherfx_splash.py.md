## Purpose
This script rebuilds the M_RainSplash material in Unreal Engine using the weather_fx module. It dynamically updates material properties and validates the configuration through editor property checks.

## How it is run
Run command: `python tools/ue_run.py tools/weatherfx_splash.py 120` (rebuilds only M_RainSplash). No other files call this script directly (confirmed via `git grep` showing only self-reference).

## Inputs
Hardcoded `rebuild=True` flag in script. Relies on current state of `weather_fx` module definitions.

## Outputs
Prints material domain, blend mode, and expression count to console (e.g., `"MATERIALDOMAIN_SURFACE", "BLENDMODE_ALPHA", 24`).

## Key functions
weather_fx.splash_material  
unreal.MaterialEditingLibrary.get_num_material_expressions  

## Depends on
weather_fx.py, unreal module  

## Gotchas
- Requires Unreal Editor to be running (unreal module is unavailable outside editor).
- 120 command-line argument is ignored by script (passed to ue_run.py only).
- Hardcoded `rebuild=True` (requires script edit to disable rebuild).
- Material property checks output to console (no persistent logs).
- Relies on `weather_fx` module reload via `importlib.reload()`.

Source: read, not executed.
