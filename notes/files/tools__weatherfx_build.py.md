## Purpose
This script builds and recompiles Unreal Engine materials for the WeatherFX asset collection located at `/Game/WeatherFX`. It validates material compilation status and reports errors via console output.

## How it is run
Command line: `python tools/ue_run.py tools/weatherfx_build.py 120`  
No other files call it (confirmed by `git grep` only finding the command line comment in `weatherfx_build.py`).

## Inputs
- Unmodified material assets in Unreal Engine's `/Game/WeatherFX` directory (hardcoded path).  
- `rebuild=True` parameter triggers full recompilation of snow and splash materials.

## Outputs
- Console output listing:  
  - Material paths (e.g., `Material'/Game/WeatherFX/Snow'`)  
  - Node counts (`nodes X`)  
  - Compilation errors (`errors [list]`)

## Key functions
- `weather_fx.build(rebuild=True)`
- `unreal.MaterialEditingLibrary.get_material_compile_errors`
- `unreal.MaterialEditingLibrary.get_num_material_expressions`

## Depends on
- `weather_fx.py` (imported module)
- Unreal Engine's `unreal` Python API (requires editor runtime)

## Gotchas
- Must run within Unreal Editor's Python environment (not standalone Python).
- The `120` command-line argument is unused by this script (passed to `ue_run.py`).
- Errors are reported only via console (no file output).
- `rebuild=True` recompiles both materials (snow/splash) instead of incremental updates.
- Assets are hardcoded to `/Game/WeatherFX` (no configurable path).

Source: read, not executed.
