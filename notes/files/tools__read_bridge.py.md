## Purpose
Prints live values from the SkyrimUnrealBridge shared memory structure to the console, providing real-time player position, camera data, weather, and scene information while Skyrim is running with the plugin loaded.

## How it is run
Command: `python tools\read_bridge.py`  
Callers: Referenced in `README.md` line 32 and `HANDOFF_FOR_CURSOR.md` line 166 (alongside `read_world.py`).

## Inputs
Shared memory mapping named `Local\\SkyrimUnrealBridge_v1` (provided by Skyrim plugin; requires Skyrim to be running with plugin loaded).

## Outputs
Console output formatted as:  
`frame={v[3]} player={v[4]:.0f},{v[5]:.0f},{v[6]:.0f} cam={v[10]:.0f},{v[11]:.0f},{v[12]:.0f} fov={v[22]:.0f} hour={v[23]:.2f} weather={s(v[27])}({v[25]:08X}) cell={s(v[28])} ws={s(v[29])}`

## Key functions
OpenFileMapping
MapViewOfFile
StructUnpack
PrintLiveData
Sleep

## Depends on
- `ctypes`, `struct`, `time` modules
- `shared/BridgeShared.h` (C struct layout matching FMT)

## Gotchas
- Requires Skyrim to be running with the bridge plugin loaded (exits if mapping not found)
- Hardcoded shared memory name `Local\\SkyrimUnrealBridge_v1` must match plugin
- Struct format string `FMT` must exactly match `BridgeShared.h` definition
- Sleeps 0.5 seconds between readings (non-realtime for rapid updates)
- String decoding uses null-terminated buffer handling

Source: read, not executed.
