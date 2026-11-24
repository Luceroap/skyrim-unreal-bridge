## Purpose
This project bridges Skyrim Special Edition (using an SKSE plugin) with Unreal Engine 5.8, streaming real-time game data (player position, camera, weather, etc.) via Windows shared memory to an Unreal project that renders the game world with enhanced visuals, including photorealistic lighting, weather effects, and accurate terrain/mesh representation.

## How it is run
Command line: `python C:\Users\Aidan\SkyrimUnrealBridge\start_bridge.py` (full bridge) or `start_bridge.py --overlay-only` (overlay mode). `start_bridge.py` calls `tools/read_bridge.py` to print live values and launches Unreal via `UnrealEditor.exe`. The `start_bridge.ps1` PowerShell script (older equivalent) automates Skyrim launch with SKSE and Unreal starting. Other files calling it: `start_bridge.py`, `start_bridge.ps1`, `tools/overlay.ps1`, `remaster_watch.py`, `live_bridge.py`.

## Inputs
- Skyrim plugin (CommonLibSSE-NG) streams data to Windows shared memory (`Local\SkyrimUnrealBridge_v1`)
- `SkyrimUnrealBridge_refs.tsv` (game-loaded references dump)
- Skyrim's game data (positions, weather, cell, worldspace, camera, FOV, time)
- Mesh data (NIFs via `bsa.py`, OBJ via `nif2obj.py`)

## Outputs
- Unreal viewport mirroring Skyrim's camera (with adjustments in `SkyrimCameraActor.cpp`)
- `SkyrimUnrealBridge_refs.tsv` (loaded references)
- Generated meshes/textures: `whiterun/export/`, `area/`, `area2/`
- `area/placements.csv` (Unreal's placement data)
- Debug outputs (`exec_out.txt`, `area2/tex/alpha_masked_extra.txt`)

## Key functions
start_bridge.py
read_bridge.py
live_bridge.py
remaster_watch.py
import_area.py
overlay.ps1
auto_build.py
distant_world.py
apply_textures.py
remaster_materials.py

## Depends on
- SKSE plugin (CommonLibSSE-NG) in `Data\SKSE\Plugins`
- Unreal project `unreal/SkyBridge`
- `tools/` utilities (`bsa.py`, `nif2obj.py`, `textures.py`)
- `shared/BridgeShared.h` (shared memory structure)
- Skyrim SE 1.6.1170 + SKSE 2.2.6

## Gotchas
- Smart App Control blocks freshly built unsigned DLLs (requires testing with `python -I -c "import ctypes,sys; ctypes.WinDLL(sys.argv[1])"`)
- Unreal requires .NET Framework SDK registration (stub key in registry)
- Skyrim crashes on exit with this mod list (unrelated to bridge)
- `start_bridge.py` runs Skyrim with low-res profile (disables Community Shaders)
- `distant_world.py` dumps references to `area2/world_*.json`

Source: read, not executed.
