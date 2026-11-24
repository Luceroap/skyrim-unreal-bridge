## Purpose
This section initializes shared memory mappings for Skyrim-to-Unreal data exchange. It sets up four distinct memory-mapped files for gear, actors, world data, and a communication packet, each with magic numbers and version 1 headers for data integrity.

## How it is run
The `SKSEPluginLoad` function is called by SKSE at runtime when Skyrim starts (no command line needed). It is registered as the plugin entry point. Other files calling into this code: `AGENT_BRIEFING.md` references the plugin, and `SKSE` framework triggers `SKSEPluginLoad` without user intervention.

## Inputs
No command-line inputs. Uses constants from `SkyBridge` namespace defined in `shared/BridgeShared.h`:
- `kGearSize`, `kActorsSize`, `kWorldSize` (memory sizes)
- `kGearName`, `kActorsName`, `kWorldName` (shared memory object names)
- `kMappingName` (packet shared memory name)

## Outputs
Creates system-wide memory-mapped files with these paths:
- `Local\SkyrimUnrealBridge_v1` (gear data)
- `_world_v1` (world data)
- `_actors_v1` (actors data, 96 actors × 320 bones)
- `_gear_v1` (gear data)
- `SkybridgeMapping` (packet structure, size `sizeof(SkyBridge::Packet)`)
Initializes headers with `kMagic` and `kVersion` (fixed version 1).

## Key functions
OpenGearMapping: Sets up gear memory mapping and header
OpenActorsMapping: Sets up actors memory mapping and header
OpenWorldMapping: Sets up world memory mapping and header
OpenMapping: Coordinates all mappings and sets up packet
SKSEPluginLoad: Plugin entry point; registers data-loaded listener

## Depends on
`shared/BridgeShared.h` (defines `SkyBridge` constants and types)
SKSE API (uses `SKSE::log`, `SKSE::GetMessagingInterface`)

## Gotchas
- Memory blocks are zero-initialized via `std::memset` before header writes
- All mappings use `PAGE_READWRITE` access flags
- `OpenMapping` calls `OpenWorldMapping`/`OpenActorsMapping`/`OpenGearMapping` in sequence
- Packet magic version is `SkyBridge::kVersion` (fixed)
- `PumpThread` starts after SKSE `kDataLoaded` event

Source: read, not executed.
