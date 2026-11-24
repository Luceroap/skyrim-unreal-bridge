## Purpose
This script counts water components (using the M_SkyWater material) and identifies which of these allow Nanite rendering (disallow_nanite property not enabled) in the current Unreal level. It helps verify Nanite compatibility for water assets during development.

## How it is run
Executed directly via `python area2/probe_water_nanite.py`. No other project files call it (empty `git grep` result for "probe_water_nanite.py").

## Inputs
Current Unreal editor level's actors and their material properties (via `unreal.EditorLevelLibrary`).

## Outputs
Console output in the format: `water components <count> still nanite <count>` (e.g., `water components 12 still nanite 5`).

## Key functions
get_all_level_actors  
get_materials  
get_name  
get_editor_property  

## Depends on
unreal (EditorLevelLibrary, StaticMeshActor)

## Gotchas
- Breaks after first M_SkyWater material per actor (only checks first match)  
- Requires Unreal editor session (EditorLevelLibrary is editor-specific)  
- Counts components with `disallow_nanite` = False as Nanite-compatible  
- Does not handle multiple M_SkyWater materials on a single actor  

Source: read, not executed.
