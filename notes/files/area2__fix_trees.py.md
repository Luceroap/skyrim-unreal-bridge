## Purpose
Adjusts the cull distances of tree instances in the Unreal Engine scene that were incorrectly set to 160000 units, extending their visibility further to 300000 units for improved visual performance. This script processes instances using Unreal Engine's Python API.

## How it is run
Executed directly as a Python script (e.g., `python area2/fix_trees.py`). No other project files call it, as confirmed by `git grep` yielding no results.

## Inputs
- Current Unreal scene state via `live.distant_actors` (dynamic object collection from the scene).
- Unchanged `unreal` module API (no explicit command-line arguments).

## Outputs
- Prints `trees extended <count>` (e.g., `trees extended 5`) showing the number of trees modified.
- Executes Unreal Engine console command `ProfileGPU` for profiling.

## Key functions
- `get_components_by_class` (retrieve mesh components)
- `get_editor_property` (check cull distance)
- `set_cull_distances` (update cull values)
- `execute_console_command` (run Profiling command)

## Depends on
- Unreal Engine Python API (`unreal` module).
- `live` object defined in the Unreal runtime environment (not a project file).

## Gotchas
- Only modifies components with `instance_end_cull_distance` exactly equal to 160000.
- Sets start cull distance to 0 (trees remain visible at all distances from the camera).
- Requires `live.distant_actors` to exist; otherwise processes no trees.
- Hardcoded values (160000 → 300000) may conflict with other project configurations.
- Relies on Unreal Engine's console being available for `ProfileGPU` execution.

Source: read, not executed.
