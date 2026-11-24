## Purpose
Profiles the `tick_body` function over a 30-second window, identifying frames where execution exceeds 40ms, and logs performance metrics to `area2/sbperf_long.txt`. Provides cumulative statistics on frame timing, spike occurrences, and top-consuming functions.

## How it is run
Run via `python area2/sbperf_long.py` from the project root. No other files in the project call `sbperf_long.py` (confirmed via `git grep` search).

## Inputs
- Global variable `DUR` (default: 30 seconds).
- `live.tick_body` function from the `live` module.

## Outputs
- `area2/sbperf_long.txt`: Contains cumulative frame timing stats, spike details (>40ms), and top-consuming function profiles.

## Key functions
body - Wraps `tick_body` for profiling, tracks frame durations, logs spikes.
write_summary - Outputs cumulative stats to `sbperf_long.txt` after 30s window.
spike_handler - Identifies and formats frames exceeding 40ms threshold.

## Depends on
- `live.tick_body` (from `live.py` module).
- Standard libraries: `sys`, `time`, `cProfile`, `pstats`, `io`.

## Gotchas
- DUR defaults to 30 seconds if not defined externally.
- Hardcoded Windows path (`C:\Users\Aidan\...`) in output filename.
- Modifies `live.tick_body` in-place during runtime.
- Profiled window duration is fixed by `DUR` (no command-line override).
- Spikes log only top 4 longest frames in `sbperf_long.txt`.

Source: read, not executed.
