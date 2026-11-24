## Purpose
Imports NPCs from Skyrim as skeletal meshes in Unreal Engine and animates them based on the actor stream. It imports FBX files from `area2/npc/export/npc_<baseId>.fbx` on demand, creates PoseableMeshComponent actors, and poses bones based on Skyrim's actor data streamed through `Local\\SkyrimUnrealBridge_actors_v1`. Called from `live_bridge.tick()`.

## How it is run
Executed via `live_bridge.tick(live)` from `unreal/SkyBridge/live_bridge.py` (line 1102) as part of the editor tick process. Runs every editor frame (at most 60 times per second).

## Inputs
- Memory-mapped actor stream: `Local\\SkyrimUnrealBridge_actors_v1`
- Memory-mapped gear stream: `Local\\SkyrimUnrealBridge_gear_v1`
- FBX files: `area2/npc/export/npc_<baseId>.fbx`
- Skeleton JSON: `area2/npc/skin/skeleton_<key>.json`
- Textures: `area2/npc/tex/` and `area2/tex/`
- Camera position: `v[10:13]` (line 1070 in `tick()`)

## Outputs
- Spawned NPC actors as `PoseableMeshComponent` (up to 12 within 5200 Skyrim units (~75m) of camera)
- Imported FBX meshes at `/Game/Npc/` path
- Animated NPC positions and bone poses
- Weapon meshes via gear stream

## Key functions
stream_seq - Actor stream sequence check (line 208)
read_actors - Reads actor stream data (line 214)
skel_key - Determines skeleton key (line 331)
rest_pose - Loads skeleton rest pose (line 337)
mesh_for - Imports FBX mesh (line 389)
_spawn - Spawns NPC actor (line 534)
_ingest - Processes new stream data (line 767)
_smooth - Smooths movement between samples (line 826)
_apply_pose - Applies bone pose (line 865)
tick - Main frame processing (line 1024)

## Depends on
`ctypes`, `json`, `os`, `re`, `shutil`, `struct`, `time` (standard libraries)
`unreal` (Unreal Engine API)
`ue_assets` (unreal/SkyBridge/ue_assets.py)
`remaster_materials` (unreal/SkyBridge/remaster_materials.py)
`live_bridge` (unreal/SkyBridge/live_bridge.py)

## Gotchas
- Skeleton-less mesh causes editor crash (BoneContainer.cpp:165) - guarded against (lines 430-432)
- Parsing every actor's bones costs ~3 ms per frame (line 326)
- Creatures (dragons, wolves) get priority over humans (lines 987-990)
- Only 1 FBX import per editor frame (lines 992-993)
- "NPC" root bone is not required for creatures (line 766)

Source: read, not executed.
