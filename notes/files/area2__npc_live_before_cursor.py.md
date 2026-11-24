## Purpose
This file handles real-time integration of Skyrim NPCs into the Unreal Engine scene. It imports skeletal meshes from FBX files and positions them using data streamed from Skyrim's actor system, maintaining the correct pose and orientation while handling NPC animations and equipment.

## How it is run
Called from live_bridge's tick: `npc_live.tick(live)`. Not intended for direct command line execution. The git grep output shows it's referenced in COORDINATION.md.

## Inputs
- Shared memory actors stream: "Local\\SkyrimUnrealBridge_actors_v1"
- Shared memory gear stream: "Local\\SkyrimUnrealBridge_gear_v1"
- FBX files: area2/npc/export/npc_<baseId>.fbx
- Rest pose JSON: area2/npc/skin/skeleton_<sex>.json
- Camera position (for distance filtering)
- Skyrim actor data (base ID, position, bone poses)

## Outputs
- Unreal Engine NPCs with skeletal meshes
- Dynamic weapon meshes when weapons are drawn
- Position and pose updates within 5200 Skyrim units (75m) of camera
- NPC actors managed in Unreal scene (SkyBridge/NPCs folder)

## Key functions
stream_seq - Checks actors stream sequence number
read_actors - Reads all actors from shared memory
rest_pose - Gets bone rest pose for sex
mesh_for - Imports/loads NPC skeletal mesh
spawn - Creates NPC actor in scene
ensure_rest - Sets up bone reference poses
plan - Precomputes bone pose math
pose - Applies pose to NPC
read_gear - Reads gear from shared memory
weapon - Places weapon mesh

## Depends on
- live_bridge (calls it from tick)
- tools/npc_build.py (creates FBX files)
- area2/npc/export/ (FBX files)
- area2/npc/skin/ (rest pose JSON)
- Unreal Engine API (unreal module)
- ctypes (for memory mapping)

## Gotchas
- Only processes NPCs within 5200 Skyrim units (~75m) of camera
- Max 12 NPCs processed per tick (MAX_NPCS = 12)
- Requires specific coordinate conversion (1.4287 cm per Skyrim unit)
- Only handles NPCs with base IDs in the export directory
- Uses specific memory mapped file naming conventions

Source: read, not executed.
