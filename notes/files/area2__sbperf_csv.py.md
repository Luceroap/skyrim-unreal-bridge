## Purpose
Starts CSV-based performance profiling in Unreal Engine for a specified number of frames. Generates profiling data for frame times and related metrics during runtime.

## How it is run
Command: Executed within Unreal Engine's Python environment (e.g., via editor scripts). Callers: No files found that import or call `sbperf_csv.py` via the provided `git grep` search.

## Inputs
`FRAMES` (integer, default 300) from global environment, controlling the number of frames to profile.

## Outputs
CSV profiling data written by Unreal Engine's `csvprofile` command (exact path not specified in code).

## Key functions
execute_console_command
print

## Depends on
unreal (Unreal Engine Python API)

## Gotchas
- FRAMES defaults to 300 if not defined in the environment.
- Requires Unreal Engine to be running (fails if executed outside Engine context).
- Output CSV file location is not configured in this script.

Source: read, not executed.
