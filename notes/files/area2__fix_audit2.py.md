## Purpose
Fixes material assignments for specific chair meshes in Unreal levels and clears stale cache entries from the slot cache. Processes only static mesh components named "clutter_common_commonchair02" to ensure correct material overrides.

## How it is run
Executed directly via Python (e.g., `python area2/fix_audit2.py`). No other project files call it (git grep found no instances).

## Inputs
Unreal Engine project level data (via unreal.EditorLevelLibrary), materials defined in `ue_assets` module.

## Outputs
Prints material names of processed chairs, logs "chairs [count] cleared stale cache misses" to console.

## Key functions
- `get_all_level_actors`: Retrieves all level actors in the editor context.
- `get_components_by_class`: Filters mesh components by class.
- `slot_material`: Fetches material slot from `ue_assets`.
- `set_material`: Updates component material references.
- `cache cleanup`: Removes cache entries with `False` values.

## Depends on
`ue_assets` module, Unreal Engine's `unreal` library (specifically `EditorLevelLibrary`).

## Gotchas
- Requires Unreal Editor to be running (uses `EditorLevelLibrary`).
- Only processes static mesh components with exact name "clutter_common_commonchair02".
- Cache entries with `False` values are permanently removed.
- Prints material names during execution (may clutter console).
- Skips actors without matching mesh name or invalid materials.

Source: read, not executed.
