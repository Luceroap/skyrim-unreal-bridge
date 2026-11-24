## Purpose
This script analyzes the current Unreal Engine level for actors related to the SkyBridge project. It counts actors by folder path and identifies static mesh models with high duplication rates across the level.

## How it is run
Executed within Unreal Editor's Python console as `python probe_perf.py`. No other files call it, as confirmed by `git grep` results showing no references.

## Inputs
Current Unreal level loaded in the editor (no external input files).

## Outputs
Console output containing:
- Total actors count and folder distribution (e.g., `actors 42 {''/SkyBridge/Assets': 30}`)
- Models with ≥8 copies (e.g., `models with >=8 copies: 5 covering 12 actors`)
- Top 15 duplicated mesh instances (e.g., `[(('/SkyBridge/Assets', 'Mesh_001'), 12), ...]`)

## Key functions
get_all_level_actors
get_folder_path
static_mesh_component
get_name
Counter
print

## Depends on
`unreal` module (EditorLevelLibrary, StaticMeshActor), SkyBridge folder structure convention.

## Gotchas
- Only processes actors in folders starting with "SkyBridge"
- Ignores non-static mesh actors (e.g., actors without static meshes)
- Limits duplicate mesh output to top 15 entries
- Requires Unreal Editor context to execute
- Counts only static mesh actors with valid static_mesh_component

Source: read, not executed.
