## Purpose
Generates a memory usage summary for the currently open Unreal Editor level by counting actor types and listing loaded meshes in the Area2 folder. Outputs actor distribution and asset counts to the console.

## How it is run
Executed as a standalone Python script within the Unreal Editor's Python environment (e.g., via editor's script console or `unreal_python.exe`). No other project files call this script (confirmed by `git grep` with no results).

## Inputs
The currently open level in the Unreal Editor (no command-line arguments or external inputs).

## Outputs
Console output showing:
- Actor count and top 8 actor types (`print("actors", len(acts), c.most_common(8))`)
- Number of loaded meshes in `/Game/Area2` (`print("loaded meshes:", len(unreal.EditorAssetLibrary.list_assets("/Game/Area2", recursive=False)))`)

## Key functions
get_editor_world  
execute_console_command  
get_all_level_actors  
Counter  
list_assets  

## Depends on
`unreal` (Unreal Engine Python API), `collections.Counter`

## Gotchas
- Requires Unreal Editor to be open (uses `EditorLevelLibrary`).
- Hardcoded asset path `/Game/Area2` must match project structure.
- `memreport -full` command runs but output is not captured; only actor/mesh counts are printed.
- Not integrated into build or runtime systems (no file dependencies found via `git grep`).
- Only prints summary data; full memory report is not processed.

Source: read, not executed.
