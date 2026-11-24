## Purpose
This SKSE plugin captures real-time game state (player position, world objects, actor poses, and gear) into shared memory blocks for synchronization with Unreal Engine. It handles data streaming via memory mappings, including world scans (objects, lights), actor skeletons, and worn equipment, with configurable update rates.

## How it is run
No direct command line; loaded as a SKSE plugin at Skyrim startup. Other files calling it: `shared/BridgeShared.h` (included), `skse/pluginmain.cpp` (SKSE plugin entry point), and Skyrim's engine via SKSE task interface (`SKSE::GetTaskInterface()->AddTask`).

## Inputs
- Game state: Player character (`RE::PlayerCharacter`), cells (`RE::TESObjectCELL`), weather (`RE::Sky`), and active references.
- Flag files: `Data/SKSE/Plugins/SkyrimUnrealBridge.autoload` (auto-load latest save), `Data/SKSE/Plugins/SkyrimUnrealBridge.dump` (trigger refs dump), `Data/SKSE/Plugins/SkyrimUnrealBridge.sky` (set hour/weather).

## Outputs
- Shared memory blocks: `_world_v1` (world objects/lights), `_actors_v1` (actor poses), `_gear_v1` (worn gear).
- Log files: `SkyrimUnrealBridge_refs.tsv` (world references), `SkyrimUnrealBridge_lights.tsv` (active lights), `SkyrimUnrealBridge_centers.txt` (dump positions).

## Key functions
Sample - Player state capture.
ScanWorld - World object/light scan.
ScanActors - Actor skeleton pose stream.
ScanGear - Worn armor and gear capture.
AutoLoadLatestSave - Load most recent save on main menu.
ApplySkyCommands - Process `SkyrimUnrealBridge.sky` file.
DumpRefs - Dump references to TSV.
UiFlags - Compute UI flags (menus, combat).
Stat - Get actor value statistics.
CopyStr - Safe string copy.
RotFromAngles - Convert Euler angles to rotation matrix.
CollectLightsImpl - Gather active lights.
BoneNameIndex - Track bone names for actors.
FillActorImpl - Populate actor pose data.
GuardedCall - SEH-protected function call.

## Depends on
- `shared/BridgeShared.h` (shared data structures, memory mappings).
- SKSE SDK (`SKSE::GetTaskInterface`, `RE::PlayerCharacter`).
- Skyrim engine (`RE::Sky`, `RE::TES`, `RE::UI`).

## Gotchas
- Skips world models containing "marker" (e.g., crafting station helpers).
- Uses SEH (`__try`/`__except`) for crash recovery in reference scans.
- DumpRefs() only triggers after player moves >2500 units since last dump.
- `SkyrimUnrealBridge.sky` commands (e.g., `weather SkyrimClear`) are consumed after execution.
- AutoLoadLatestSave() runs in a separate thread to avoid blocking data streaming.

Source: read, not executed.
