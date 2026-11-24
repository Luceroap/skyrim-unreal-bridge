## Purpose
This module synchronizes NPCs from Skyrim's actor stream into Unreal Engine. It imports skeletal meshes from FBX files and poses them based on real-time stream data, enabling live character animation and positioning.

## How it is run
Not run as a standalone script. Called from `live_bridge.py`'s tick function: `npc_live.tick(live)`. Invoked every editor frame during runtime. The `git grep` result confirms it is referenced in `COORDINATION.md` and called by `live_bridge`.

## Inputs
- Shared memory segment `Local\\SkyrimUnrealBridge_actors_v1` (actor stream)
- Shared memory segment `Local\\SkyrimUnrealBridge_gear_v1` (weapon stream)
- FBX files from `area2/npc/export/npc_<baseId>.fbx`
- Skeleton JSON files from `area2/npc/skin/skeleton_*.json`

## Outputs
- Unreal Engine actors (in-memory scene objects) for NPCs
- Bone pose transforms applied to skeletal mesh components
- Weapon meshes spawned for weapon-holding NPCs

## Key functions
tick
read_actors
mesh_for
rest_pose
parse_bones
_ingest
_apply_pose
read_gear
_weapon

## Depends on
live_bridge.py
area2/npc/export/*.fbx
area2/npc/skin/skeleton_*.json

## Gotchas
- Only processes NPCs within 5200.0 Skyrim units (75m) of camera
- Skips player character (actor with flags & 1)
- Limits to 12 total NPCs (6 reserved for nearest creatures)
- Weapon assets may not appear immediately if not cached
- Creature NPCs take priority over human NPCs

Source: read, not executed.
