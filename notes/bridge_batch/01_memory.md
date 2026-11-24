# Memory pressure and cache limits

Local-model review lead; NOT independently verified or applied.

## Finding
Memory-pressure handling can fail to reduce retained assets or repeatedly allocate new objects

## Evidence
- unreal/SkyBridge/memory_governor.py:131 - for name, m in cands:

## Suggested fix
Replace `cands = cands[:MAX_UNLOAD]` with `cands = cands[:MAX_UNLOAD]` (no change needed, but ensure it's applied correctly)

## Validation needed
Check if `cands` is correctly sliced to `MAX_UNLOAD` before processing, and verify that asset unloading doesn't cause repeated allocations.
