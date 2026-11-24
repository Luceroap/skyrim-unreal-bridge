## Purpose
This script inspects Unreal Engine texture assets in the project's `Area2Tex` folder, checking their dimensions, streaming settings, LOD groups, and related console variables. It helps verify texture configuration consistency and engine settings without modifying assets.

## How it is run
Executed directly via Python within the Unreal Editor (no command-line arguments needed). No other files in the project reference this script, as confirmed by `git grep` output.

## Inputs
Hardcoded texture names (`wrfieldgrass01`, `wrslate01`, `wrstonefloor02`), Unreal Engine runtime environment, and active project context (`/Game/Area2Tex/` paths).

## Outputs
Console output listing texture properties (dimensions, max size, LOD group, streaming settings) and values of texture-related console variables (e.g., `r.Streaming.PoolSize`, `r.MaxAnisotropy`), with `"?"` for unsupported engine versions.

## Key functions
unreal.load_asset
t.blueprint_get_size_x
t.get_editor_property
SystemLibrary.get_console_variable_float_value
hasattr check for method existence

## Depends on
Unreal Engine Python API (`unreal` module), textures at `/Game/Area2Tex/`, Unreal Editor runtime environment.

## Gotchas
- Fails silently if textures are missing (prints "no asset" for missing names).
- `r.Streaming.PoolSize` values may show `?` if engine lacks method.
- Hardcoded texture names require code changes to modify.
- Requires active Unreal Editor session with Python API enabled.
- Console variable checks skip errors via `hasattr`.

Source: read, not executed.
