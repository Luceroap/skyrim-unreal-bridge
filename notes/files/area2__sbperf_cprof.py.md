## Purpose
Profiles the live.tick_body function over 40 frames to collect CPU performance data. Outputs top functions and timing statistics to area2/sbperf_cprof.txt for performance analysis.

## How it is run
Imported directly into game code (no command-line arguments). Other files calling it cannot be determined from missing git grep output.

## Inputs
Delta time (dt) passed to the wrapped live.tick_body function during each frame.

## Outputs
area2/sbperf_cprof.txt containing profiling statistics, including frame timing and top functions sorted by cumulative time. Console output: "cprofile armed".

## Key functions
body (wrapper for tick_body)
enable (cProfile)
disable (cProfile)
sort_stats (pstats)
print_stats (pstats)

## Depends on
sys, time, cProfile, pstats, io, live module

## Gotchas
Hardcoded Windows path (C:\Users\Aidan\...\sbperf_cprof.txt)
Profiles exactly 40 frames before writing
Original live.tick_body function is deleted post-profiling
Uses global module storage (sys.modules.setdefault)
Writes to non-portable file path during execution

Source: read, not executed.
