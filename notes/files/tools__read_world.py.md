## Purpose
This script reads the shared memory segment created by the Skyrim Unreal Bridge plugin to display live world data. It parses the memory structure to report version, sequence numbers, model references, and object positions.

## How it is run
Command line: `python tools/read_world.py`. Called by `tools/read_bridge.py` as shown in the handoff note.

## Inputs
Shared memory segment named `Local\\SkyrimUnrealBridge_world_v1` (requires plugin to be loaded).

## Outputs
Console output containing:
- Magic number, version, sequence, tick, reference counts, model/light counts, and status bits
- Model names (up to 8)
- Reference data (position, scale, flags for up to 3 models)

## Key functions
Open mem mapping
Parse header
Print refs
Print models
View memory

## Depends on
ctypes, ctypes.wintypes

## Gotchas
- Requires Skyrim Unreal Bridge plugin to be active (fails if memory mapping not found)
- Uses exact shared memory name "Local\\SkyrimUnrealBridge_world_v1"
- Relies on fixed memory offsets (32, 4096*128)
- Windows-only due to kernel32 API usage
- Uses little-endian structure parsing ("<8I")

Source: read, not executed.
