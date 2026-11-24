## Purpose
This script probes the current state of rain-related assets and materials within an Unreal Engine level. It verifies the existence of specific assets, checks material parameter configurations, and inspects scene capture actors to confirm the presence of rain effects.

## How it is run
Standalone execution via Unreal editor Python environment. No command-line arguments required. No other files in the project reference or call this script (confirmed by empty `git grep` output).

## Inputs
Current Unreal editor state (level actors, assets, material configurations). Requires `live` object to be defined in context.

## Outputs
Console output logs showing:
- Asset existence checks (`MPC_RainOcc`, `M_RainDrops`)
- Material vector parameters (`vector params`)
- Custom material node descriptions (`custom nodes`)
- Scene capture actor labels (`captures`)

## Key functions
does_asset_exist
get_all_level_actors
load_asset
get_vector_parameter_names
get_material_expressions

## Depends on
unreal.EditorAssetLibrary
unreal.EditorLevelLibrary
unreal.MaterialEditingLibrary

## Gotchas
- The 'live' object must be defined in the script's execution context
- Material expressions check relies on Unreal version supporting `get_material_expressions` (handled via `hasattr`)
- No explicit error handling for missing Unreal editor context
- Asset paths are hard-coded (`/Game/Area2Tex/`)

Source: read, not executed.
