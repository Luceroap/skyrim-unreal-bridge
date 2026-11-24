## Purpose
This module manages memory usage in the Unreal editor by unloading unused assets from specific directories and dynamically adjusting texture streaming settings to prevent memory exhaustion during Skyrim-Unreal bridge operations. It operates continuously within the live bridge's tick loop to maintain stable performance.

## How it is run
Called periodically from `live_bridge.tick` (in the live bridge module) every 10 seconds (CHECK_S). The `tools/make_local_queue.py` script includes this file in its module list but does not directly execute it.

## Inputs
- `live` object (contains `mesh_cache`, `_flags`, and bridge state)
- System memory statistics (via `memory_gb()`)
- Current memory free thresholds (LEVEL_FREE_GB)
- Current level ID (from `live` object)

## Outputs
- Writes `area2/memory_status.json` (memory statistics and status)
- Logs to Unreal editor with prefix `[SkyBridgeLive] memory:`
- Adjusts Unreal engine console variables: `r.Streaming.PoolSize`, `r.Streaming.MipBias`, `r.Streaming.HiddenPrimitiveScale`, `r.Streaming.LimitPoolSizeToVRAM`, `r.VRS.Enable`, `r.VRS.ContrastAdaptiveShading`
- Unloads unused assets (via `unreal.EditorLoadingAndSavingUtils.unload_packages`)

## Key functions
memory_gb: Returns system memory statistics in GB
log: Logs with SkyBridgeLive prefix
_cvars: Executes Unreal console commands
_textures: Caches texture paths per material instance
_in_use: Collects currently referenced assets
sweep: Unloads unused packages
_collect: Builds asset unload list
tick: Main entry point (called periodically)

## Depends on
- Unreal engine (via `unreal` module)
- Python standard libraries (ctypes, json, os, time)
- No other project files (imports only standard modules)

## Gotchas
- Only unloads assets from /Game/Area2/ and /Game/Tamriel/ (other assets remain loaded)
- Skips operation if `live._flags` contains "nomemgov"
- Unloads at most 60 packages per sweep (MAX_UNLOAD) to avoid rendering stalls
- Writes memory status to `area2/memory_status.json` (fixed location)
- Adjusts texture pool based on 4 memory threshold levels (0-3)

Source: read, not executed.
