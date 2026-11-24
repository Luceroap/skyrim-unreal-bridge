## Purpose
Prints worn gear data (armor models and weapons) from Skyrim's plugin via memory-mapped shared memory. Processes up to 12 actors per run, showing armor paths and weapon configurations.

## How it is run
Command line: `python tools/read_gear.py` (Windows). Referenced in COORDINATION.md as part of the "WORN GEAR" system, triggered by plugin integration.

## Inputs
Memory-mapped file named `Local\\SkyrimUnrealBridge_gear_v1` (created by Skyrim plugin). Requires plugin to be running.

## Outputs
Console output with:
- Actor ID, base address, flags, gear count (first 4 paths shown)
- Face ID, weapon flags, weapon paths (first 2 weapons shown)
- Magic/version/sequence/tick headers

## Key functions
OpenFileMappingW
MapViewOfFile
struct.unpack
actor_data_processing
path_decoding
weapon_data_print

## Depends on
ctypes, BridgeShared.h (structure definitions in C++ plugin)

## Gotchas
- Only processes first 12 actors (min(nA, 12))
- Gear paths limited to first 4 in output (paths[:4])
- Paths decoded with 'latin1' encoding
- No version/magic number validation
- Hardcoded constants MAXG=24 and PLEN=112

Source: read, not executed.
