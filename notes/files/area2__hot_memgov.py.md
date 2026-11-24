## Purpose
This file dynamically patches the `tick_body` method of the live bridge module to integrate memory governance. It monitors and limits memory usage during runtime by reloading the `memory_governor` module before injecting governance logic into the bridge's core loop.

## How it is run
Command: `python area2/hot_memgov.py` (executed once at bridge startup). No other project files call this script (confirmed via `git grep` results showing zero matches).

## Inputs
- `memory_governor` module (reloaded via `importlib.reload`)
- `live_bridge.py` (read from `C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py`)

## Outputs
- Modified `live` module's `tick_body` method (overwriting the original implementation)
- Console output: `tick_body patched; governor X.X GB` (where `X.X` is current memory usage)

## Key functions
tick_body patch injection  
memory governance integration  
live_bridge.py code extraction  

## Depends on
memory_governor  
unreal/SkyBridge/live_bridge.py  

## Gotchas
- Removes `start()` function from `live_bridge.py` (line 4 of the script), potentially breaking initialization logic if `start()` was required.
- Hardcoded Windows path `C:\Users\Aidan\SkyrimUnrealBridge` may fail on other systems.
- Relies on `live_bridge.py` containing a line `start()` (exact string match).
- Memory governor memory usage (GB) printed without unit clarification.
- Uses `exec()` on modified code, increasing security/corruption risk if `live_bridge.py` changes.

Source: read, not executed.
