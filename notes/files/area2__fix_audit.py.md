## Purpose
This script corrects slot assignments for specific Skyrim meshes (e.g., `commonchair02`, `wrtrelliscomplete01destroyed`) in Unreal Engine levels. It modifies live bridge runtime behavior to ensure proper material slot handling during level editing.

## How it is run
Run as a standalone Python script via `python fix_audit.py`. No other project files call this script (confirmed by empty `git grep` results).

## Inputs
Active Unreal editor session with levels containing actors under `SkyBridge` folders; static mesh components with names containing `commonchair02` or `wrtrelliscomplete01destroyed`.

## Outputs
Console output listing fixed mesh names and their material assignments; modifies live bridge runtime state via `live_bridge.py` (no file writes).

## Key functions
fix_slots
get_all_level_actors
get_components_by_class
get_name
get_material
cache cleanup

## Depends on
ue_assets
unreal.EditorLevelLibrary
unreal.StaticMeshComponent

## Gotchas
Hardcoded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py`
Processes only meshes with exact name substrings (`commonchair02`, `wrtrelliscomplete01destroyed`)
Skips actors outside `SkyBridge` folder paths
Removes cache entries with falsy values
Requires Unreal editor to be open with relevant levels loaded

Source: read, not executed.
