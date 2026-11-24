## Purpose
Collects GPU utilization and memory usage statistics per process between Skyrim and Unreal Engine on Windows. Uses Windows Performance Counters to sample GPU engine usage and memory metrics over a specified duration, providing mean, p95, and max values for reporting.

## How it is run
Command: `python tools/perf_gpu_share.py [seconds=30] [out=area2/perf/gpu_share.json]`. No other project files in `tools/` or elsewhere call this script (confirmed via `git grep` for "perf_gpu_share.py").

## Inputs
- Optional `seconds` integer (default 30) for sampling duration.
- Optional `out` path (default `area2/perf/gpu_share.json`).

## Outputs
- JSON file at specified output path (`area2/perf/gpu_share.json`).
- Console output listing:
  - GPU engine utilization (mean/p95/max per process).
  - GPU memory usage (GB per process).

## Key functions
names(): Maps process IDs to names via `tasklist`.
main(): Coordinates sampling, processing, and output.

## Depends on
Python standard libraries (`json`, `os`, `re`, `subprocess`, `sys`). No other project files.

## Gotchas
- Only runs on Windows (uses Windows Performance Counters and PowerShell).
- Skips processes with average GPU utilization below 0.5%.
- Only reports GPU memory usage above 50MB (0.05GB).
- Automatically creates output directory if missing.
- Requires PowerShell availability for counter sampling.

Source: read, not executed.
