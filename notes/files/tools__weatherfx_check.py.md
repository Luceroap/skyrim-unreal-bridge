## Purpose
Compiles specific WeatherFX materials in Unreal Engine and lists their expression classes. Outputs expression counts and types to the console.

## How it is run
Executed within Unreal Engine's Python environment (via the editor). No other project files call it (git grep returned no results).

## Inputs
Hardcoded asset paths: `/Game/WeatherFX/M_SnowFlakes` and `/Game/WeatherFX/M_RainSplash`.

## Outputs
Console output showing each material path, expression count, and dictionary of expression type counts (e.g., `"/Game/WeatherFX/M_SnowFlakes 10 {'MaterialFunctionCall': 5, ...}"`).

## Key functions
recompile_material
load_asset
get_num_material_expressions
get_editor_property

## Depends on
unreal module, collections (standard library)

## Gotchas
Only processes two predefined material paths (M_SnowFlakes, M_RainSplash). If asset paths change, script fails. Uses fallback for editor-only expressions but may miss edge cases. Requires Unreal editor session.

Source: read, not executed.
