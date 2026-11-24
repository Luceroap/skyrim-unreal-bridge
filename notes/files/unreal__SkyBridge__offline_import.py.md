## Purpose
Automates headless import of pre-converted models into Unreal Engine, skipping existing assets to avoid redundant imports during gameplay. Resumable via `area2/ready.txt` tracking, ensuring only new models are processed.

## How it is run
Command line: `python tools/offline_import.py [options]`, called by `Import_Assets_Offline.bat` and `tools/offline_import.py`. Uses `UnrealEditor-Cmd -run=pythonscript` for headless execution without a window or Skyrim running.

## Inputs
- `area2/ready.txt` (list of model names)
- FBX files in `area2/export/` (e.g., `area2/export/model.fbx`)
- Environment variables: `OFFLINE_LIMIT` (max models), `OFFLINE_MINUTES` (time budget)

## Outputs
- Log file: `area2/offline_import.log`
- Imported assets in `/Game/Area2/` (FBX, textures, materials)
- NPC assets in `/Game/Npc/` (processed via `npc_live.mesh_for`)

## Key functions
ue_assets.import_model (main model importer)  
npc_live.mesh_for (NPC mesh processor)  
say (progress logging helper)  

## Depends on
ue_assets.py  
npc_live.py  

## Gotchas
- Skips models with spaces in filenames (`" " not in n`)  
- Requires corresponding `.fbx` file to exist in `export/`  
- NPC import skips non-8-character base IDs (e.g., `npc_male.fbx` excluded)  
- Uses `OFFLINE_LIMIT` and `OFFLINE_MINUTES` for control  
- Resumes by skipping already imported models (via `eal.does_asset_exist`)  

Source: read, not executed.
