## Purpose
Patches the live bridge to remove the `start()` call in `live_bridge.py`, enabling interior city prefetching and updating the live bridge's internal state for proper handling of Skyrim interior environments.

## How it is run
Executed as a standalone Python script via `python area2/fix_interior.py`. No other files call it (grep found no references to `fix_interior.py` in the project).

## Inputs
- `unreal/SkyBridge/live_bridge.py` (read-only access to patch the file content)

## Outputs
- Console output showing interior counts (e.g., `interiors 15 prefetch todo 5 interior now None`)
- Modified `live` object state (interiors, prefetch_todo, `_interior`)

## Key functions
- Patch Live class methods from live_bridge
- Prefetch cities via `live.prefetch_cities()`
- Print interior statistics
- Execute patched live_bridge code
- Update `live` object with patched attributes

## Depends on
- `live_bridge.py` (read directly for patching)

## Gotchas
- Hardcoded string replacement `\nstart()\n` may break if `live_bridge.py` changes format
- Requires `live` object to be initialized before execution
- No error handling if `live_bridge.py` lacks the target string
- Modifies code in-memory only (no file writes)

Source: read, not executed.
