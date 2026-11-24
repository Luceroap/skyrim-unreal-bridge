## Purpose
This PowerShell script automates the rebuild process for the SkyrimUnrealBridge project by stopping running Unreal Editor instances, executing Python-based asset preparation scripts, exporting terrain with Blender, and importing terrain data into Unreal Engine. It ensures a clean workflow from game data to Unreal project assets.

## How it is run
Command line: `powershell -ExecutionPolicy Bypass -File C:\Users\Aidan\SkyrimUnrealBridge\rebuild_all.ps1`  
No files explicitly call it (git grep for "rebuild_all.ps1" returned no results in project files).

## Inputs
- Skyrim Special Edition game data directory: `D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data`
- Project root: `C:\Users\Aidan\SkyrimUnrealBridge`
- Environment variable `FORCE` (temporary during Blender step)
- Pre-existing project files (e.g., `tools\auto_build.py`, `unreal\SkyBridge\import_terrain3.py`)

## Outputs
- Log files: `rebuild1.log` (auto_build.py), `rebuild2.log` (esm_land_tex.py), `rebuild3.log` (blender), `rebuild4.log` (import_terrain3.py), `rebuild5.log` (fix_slots.py)
- Completion marker: `rebuild_done.txt` containing "done"
- Generated terrain data in `area2` directory (from esm_land_tex.py)

## Key functions
Stop UnrealEditor
Run auto_build.py
Process ESM terrain textures
Export terrain via Blender
Import terrain into Unreal
Fix slot assignments
Mark completion

## Depends on
- `tools\auto_build.py`
- `tools\esm_land_tex.py`
- `tools\blender_export.py`
- `unreal\SkyBridge\import_terrain3.py`
- `unreal\SkyBridge\fix_slots.py`
- Blender executable at `D:\blender.exe`
- Unreal Editor command-line at `D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe`

## Gotchas
- Hard-coded paths for Blender and Unreal Engine (`D:\blender.exe`, `D:\UE_5.8\...`) will fail if installed elsewhere
- Forcibly terminates any running UnrealEditor processes (`Stop-Process -Force`)
- Overwrites log files (`>` operator) instead of appending
- Relies on environment variable `FORCE` set only during Blender execution
- Uses `-nullrhi` for Unreal commands, skipping graphical interface

Source: read, not executed.
