## Purpose
Monitors real-time prefetch queue status by reporting pending items and current batch size. Serves as a debugging tool for prefetch operations in the Skyrim-Unreal bridge.

## How it is run
Command: `python area2/probe_pf.py`. No other files reference this script (verified via `git grep probe_pf.py`), so it is executed manually for debugging.

## Inputs
The `live` module's `prefetch_todo` and `_pf_chunk` attributes (read as runtime state).

## Outputs
Console output with two integer values (e.g., `prefetch left 3 current batch 5`), showing pending queue items and batch size.

## Key functions
print statement (outputs prefetch queue status)

## Depends on
`live` module (must be initialized in runtime context)

## Gotchas
- Requires the `live` module to be defined; otherwise, script crashes with `NameError`.
- Output is printed to console only; no files or shared memory modified.
- Not used in production; strictly a debugging utility.

Source: read, not executed.
