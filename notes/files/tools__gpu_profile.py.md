## Purpose
This script captures GPU frame profiling data from the Unreal Editor's log, analyzing rendering passes that exceed a specified time threshold and depth limit. It outputs a human-readable summary of expensive GPU operations to help identify performance bottlenecks in the rendering pipeline.

## How it is run
Executed directly via `python tools/gpu_profile.py [min_ms=0.25] [max_depth=6]` from the command line. No other files in the project call this script (verified via `git grep` showing no references to `gpu_profile.py` in other files).

## Inputs
- Command-line arguments: `min_ms` (default 0.25), `max_depth` (default 6)
- Unreal log file: `C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\Saved\Logs\SkyBridge.log`

## Outputs
- Console output listing GPU pass names, depth, and duration (e.g., `  0.321 ms   Render Target`), truncated to 90 characters for pass names
- Writes to Unreal console via `ProfileGPU` command (no persistent output file)

## Key functions
main() – Coordinates profiling execution
ue_exec() – Executes Unreal console command
ROW – Regex pattern for parsing log lines
print() – Outputs formatted GPU pass data

## Depends on
start_bridge.py (for ue_exec function), os, re, sys, time

## Gotchas
- Hardcoded absolute log path (C:\Users\Aidan\...)
- Fixed 6-second sleep after triggering ProfileGPU
- Output pass names truncated to 90 characters
- Default min_ms=0.25ms may filter out short passes
- Log format dependency (regex breaks if Unreal log structure changes)

Source: read, not executed.
