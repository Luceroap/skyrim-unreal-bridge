## Purpose
This script patches the `live_bridge.py` module to enable city prefetching functionality. It replaces a specific string in the live bridge code and injects additional methods for managing prefetched city data.

## How it is run
Run via `python area2/fix_prefetch.py` as a standalone script. No other project files reference this file (confirmed by empty `git grep` results).

## Inputs
- `C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\live_bridge.py` (read-only)

## Outputs
- Modifies `live` module state (e.g., `live._prefetched`, `live.prefetch_cities()`, `live.prefetch_step()`)
- Prints debug output: `prefetch todo X chunk Y`

## Key functions
prefetch_cities
prefetch_step
set_interior
update_sky
weather_setup

## Depends on
unreal\SkyBridge\live_bridge.py
live module

## Gotchas
- No other project files reference this script
- Hard-coded Windows path used in file read
- Modified live module state is shared memory
- Print statements are visible in console logs
- Requires `live_bridge.py` to contain specific string to replace

Source: read, not executed.
