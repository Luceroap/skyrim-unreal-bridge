## Purpose
This script patches `live_bridge.py` to remove the `start()` call and adjusts interior cell data handling. It reconfigures the interior loading mechanism and logs interior cell counts after prefetching city data.

## How it is run
Command: `python area2/fix_interior2.py`  
No other files in the project call this script, as confirmed by `git grep` returning no results.

## Inputs
- `live_bridge.py` (read to apply code patch)

## Outputs
- Printed stats to stdout: `interior cells <count> refs <count> prefetch todo <count>`
- Modified in-memory behavior of `live_bridge.py`'s `load_interiors` method

## Key functions
- replace_start_call
- patch_load_interiors
- cleanup_interior_keys
- prefetch_cities

## Depends on
- `live_bridge.py` (required for patching)

## Gotchas
- The string `\nstart()\n` must exactly match `live_bridge.py`'s content; otherwise, the patch fails silently.
- The script modifies code in-memory only; `live_bridge.py` remains unaltered on disk.
- The `prefetch_cities()` call is executed after removing `interiors` and `interior_of` keys from `live`.

Source: read, not executed.
