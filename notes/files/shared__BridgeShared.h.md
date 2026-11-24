## Purpose
Defines shared-memory layouts for data exchange between a SKSE plugin (writer) and Unreal Engine (reader). Specifies four memory mappings (camera packet v3, world objects, actor poses, gear) with versioned fields to enable backward compatibility.

## How it is run
Built via `cmake --build build --config Release` for SKSE plugin (included in `plugin/src/main.cpp`). Unreal reads memory via Python scripts: `unreal/SkyBridge/live_bridge.py`, `unreal/SkyBridge/npc_live.py`, and `tools/read_gear.py`.

## Inputs
Runtime data from Skyrim (player position, camera, world objects, actor poses, gear) written by SKSE plugin to shared memory mappings.

## Outputs
Memory segments:  
- `Local\\SkyrimUnrealBridge_v1` (camera packet v3)  
- `Local\\SkyrimUnrealBridge_world_v1` (world objects)  
- `Local\\SkyrimUnrealBridge_actors_v1` (actor poses)  
- `Local\\SkyrimUnrealBridge_gear_v1` (worn gear)

## Key functions
Packet
WorldHeader
ActorHeader
GearHeader

## Depends on
cstdint
plugin/src/main.cpp
unreal/SkyBridge/npc_live.py

## Gotchas
- Version 3 fields are appended; older readers ignore them (e.g., v2 writer leaves version 3 fields zero)
- Structs use #pragma pack(4); incorrect padding causes data corruption
- World stream limits: `kMaxModels=4096`, `kMaxRefs=16384`
- Gear stream caps actors at `kMaxGear=24`
- Unreal scripts must match `kVersion=3` for full data access

Source: read, not executed.
