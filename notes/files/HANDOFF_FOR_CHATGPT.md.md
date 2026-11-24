## Purpose
This document provides instructions for optimizing the Skyrim-to-Unreal Engine bridge, focusing on reducing memory growth and CPU/GPU costs while maintaining core functionality (camera, time, weather, objects, rendering). It specifies hard rules for development and references critical project documentation.

## How it is run
Executed via `Play.bat` or `python play.py` for live sessions, and `python tools\offline_import.py` for headless imports. Called by `AGENTS.md` (line 3) and `tools/make_local_queue.py` (line 338).

## Inputs
Skyrim SE 1.6.1170 game path (`D:\SteamLibrary\steamapps\common\Skyrim Special Edition`), SKSE 2.2.6, project directory (`C:\Users\Aidan\SkyrimUnrealBridge`).

## Outputs
Memory usage (GB), frames per second (FPS), import count per minute; Git commit messages for changes.

## Key functions
Cap memory growth layer
Reduce CPU/GPU cost
Report performance metrics
Enforce single UnrealEditor.exe
Backup Skyrim files

## Depends on
README.md
COORDINATION.md
HANDOFF_FOR_CURSOR.md

## Gotchas
- Only one `UnrealEditor.exe` may run (check via `tasklist | find "UnrealEditor"`)
- Backup Skyrim files to `C:\Users\Aidan\SkyrimBackups` before editing
- Git commits must be local (no remote pushes)
- Do not minimize Skyrim (causes Community Shaders crashes)
- Plugin DLL must be built via `cmake --build build --config Release` before copying

Source: read, not executed.
