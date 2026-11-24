## Purpose
This script analyzes performance data collected by the `_sbperf` module and outputs detailed metrics including frame rates, average frame times, and per-function call statistics. It is designed to be triggered at the end of a performance monitoring session to generate a summary.

## How it is run
Executed automatically by `area2/sbperf_start.py` (line 2 comment), which references it as "Read + restore with sbperf_read.py". No direct command-line invocation is required; it is called via the performance monitoring workflow.

## Inputs
- The `_sbperf` module (via `sys.modules["_sbperf"]`), containing:
  - `P.t0`: Start time of the performance session.
  - `P.frames`: List of frame timestamps.
  - `P.t`: Dictionary of function call timings.
  - `P.n`: Dictionary of function call counts.

## Outputs
- Console output showing:
  - Frame metrics (elapsed time, frames, FPS, average/frame times).
  - Per-function performance statistics (time per call, total calls).
  - "restored" message if `ARGS` contains "stop".

## Key functions
Calculate frame metrics  
Print performance summary  
Restore state on 'stop'  

## Depends on
- `sys` and `time` standard libraries.
- `_sbperf` module (preloaded by `sbperf_start.py`).
- `area2/sbperf_start.py` (calls this script).

## Gotchas
- Always restores state if `ARGS` is absent due to the default `get("ARGS", "stop")` fallback.
- Requires `_sbperf` module to be fully populated before execution.
- Output is console-only; no file writes or external storage.
- The `restore()` call in `_sbperf` is only triggered when `ARGS` contains "stop".
- The script assumes `P.frames` is non-empty; otherwise metrics are skipped.

Source: read, not executed.
