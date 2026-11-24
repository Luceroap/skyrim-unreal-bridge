## Purpose
Monitors active memory usage in the Skyrim-Unreal bridge by reporting in-use meshes, materials, textures, and cached asset statistics. Aids debugging memory consumption during development.

## How it is run
Command line: `python memgov_dry.py` (executed directly). No other files call it (empty results from `git grep` search for `memgov_dry.py`).

## Inputs
- Current `memory_governor` state via `mg._in_use()`
- `live.mesh_cache` data structure (assumed to be globally initialized)

## Outputs
Console output showing:
- In-use mesh/material/texture counts
- Cached vs. unused mesh counts (e.g., "cached meshes 100, unused now 15")
- Total memory usage in gigabytes (`mg.memory_gb()`)

## Key functions
Print resource usage counts
Filter unused cached meshes
Report memory usage
Check in-use resources

## Depends on
- `memory_governor.py` (via `import memory_governor as mg`)
- `live` module (for `live.mesh_cache`)

## Gotchas
- Uses private method `_in_use()` (underscore prefix)
- Relies on `live.mesh_cache` without validation
- Reloading `memory_governor` via `importlib.reload(mg)`
- Filename suffix `_dry.py` indicates debugging purpose
- No error handling for missing `live` or `mg` modules

Source: read, not executed.
