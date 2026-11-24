## Purpose
Stability session profiler that instruments per-tick functions in the `live` module to measure execution time. Records call durations and counts for analysis, with data readable via `sbperf_read.py`.

## How it is run
Executed via the project's main application startup (command line: `python area2/sbperf_start.py`), outputting "profiling on". No other files call it directly in the provided context; explicit callers would require `git grep` results (not provided in input).

## Inputs
No external inputs; relies on pre-existing `live` module functions (e.g., `tick_body`, `read_world`) and the `atmosphere` module's `flicker` method.

## Outputs
Writes to global module state: `P.t` (total time per function), `P.n` (call counts), `P.frames` (per-frame timing). Outputs "profiling on" to console.

## Key functions
- wrap: Instruments a method to track execution time
- body: Replaces `live.tick_body` with timing measurements
- restore: Reverts all instrumented functions (called by `sbperf_read.py`)

## Depends on
`sys`, `time`, `atmosphere`, `live` (module), and dynamic access to `sys.modules` (e.g., `npc_live`, `tamriel_live`).

## Gotchas
- Profiler modifications persist until `sbperf_read.py` restores original functions
- Skips wrapping missing functions (e.g., `read_world` if absent in `live`)
- Modifies `live` module in-place, affecting runtime behavior during profiling
- Requires explicit pairing with `sbperf_read.py` for clean teardown
- Uses global namespace (`P`) which could conflict with other modules

Source: read, not executed.
