## Purpose
Imports all FBX files from the directory `C:\Users\Aidan\SkyrimUnrealBridge\whiterun\export` into Unreal Engine's content browser under `/Game/WhiterunMeshes`. Automatically replaces existing assets with the same name and saves them after import.

## How it is run
Run via command line: `UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script=unreal/SkyBridge/import_whiterun.py`. Called explicitly by the `README.md` file (line 57) as the method to import Whiterun FBX assets.

## Inputs
- Source directory: `C:\Users\Aidan\SkyrimUnrealBridge\whiterun\export\*`.fbx
- `unreal` Python API (provided by Unreal Engine runtime)

## Outputs
- Imported assets written to Unreal Engine content path: `/Game/WhiterunMeshes/`
- Console logs: `IMPORTED <filename> -> [list of imported paths]` for each file

## Key functions
- `glob.glob` Finds all FBX files in source directory
- `unreal.AssetImportTask` Configures import parameters per file
- `unreal.AssetToolsHelpers.get_asset_tools` Retrieves asset import pipeline
- `import_asset_tasks` Executes batch import operation
- `unreal.log` Outputs import status to engine console

## Depends on
- Unreal Engine Python API (`unreal` module)
- Standard libraries: `glob`, `os`
- Source directory structure (must contain .fbx files)

## Gotchas
- Hardcoded Windows path `C:\Users\Aidan\SkyrimUnrealBridge\whiterun\export`
- Requires running within Unreal Engine Python environment (not standalone Python)
- Does not create target path `/Game/WhiterunMeshes` if missing (unhandled by script)
- Uses absolute path tied to specific user (Aidan) and machine
- Imports replace existing assets without user confirmation

Source: read, not executed.
