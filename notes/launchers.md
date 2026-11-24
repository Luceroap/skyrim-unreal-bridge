# Daily Launchers for SkyrimUnrealBridge

## Play.bat
- **How started**: Double-click or command line
- **What it starts**: `play.py` (launches Skyrim + Unreal editor)
- **Requires**: None (automatically starts Skyrim if not running, starts Unreal editor if not running)
- **Writes**: Console status messages (e.g., "starting Skyrim", "Unreal editor is live", "READY")

## Stop.bat
- **How started**: Double-click or command line
- **What it starts**: `play.py` with `--stop`
- **Requires**: Skyrim (`SkyrimSE.exe`) and Unreal editor (`UnrealEditor.exe`) must be running
- **Writes**: "closing the editor, then Skyrim" followed by "done" upon completion

## Import_Assets_Offline.bat
- **How started**: Double-click or command line
- **What it starts**: `play.py --stop` then `offline_import.py`
- **Requires**: None (closes Skyrim/Unreal first before starting import)
- **Writes**: "Closes Skyrim + the Unreal editor first, then imports every converted model. About 2.5 hours; safe to stop and run again."

## Codex_Local.bat
- **How started**: Double-click or command line
- **What it starts**: Codex agent via local Ollama model (`qwen3:30b-a3b-64k`)
- **Requires**: Skyrim and Unreal editor **closed** (needs ~18 GB GPU/system memory)
- **Writes**: Codex agent actions with workspace-write access (edits files inside this project)

## play.py
- **How started**: Called by `Play.bat` or `Stop.bat`
- **What it starts**: 
  - Background services: `asset_service.py`, `tamriel_terrain.py --serve`
  - Skyrim (auto-loads latest save) if not running
  - Unreal editor (`SkyBridge.uproject` at 1600x900 resolution)
- **Requires**: None (automatically checks running states)
- **Writes**: 
  - Console logs (e.g., "Skyrim is in the world", "Unreal editor is live")
  - `SkyrimUnrealBridge.sky` file for weather settings (`weather SkyrimClearTU`)
  - Editor logs in `unreal/Saved/Logs/SkyBridge*.log`
