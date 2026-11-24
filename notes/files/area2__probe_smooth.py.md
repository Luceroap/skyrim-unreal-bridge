## Purpose
This file enhances NPC movement tracking by monitoring actor speeds above 25 units, recording locations during motion, and analyzing motion patterns to detect anomalies like abrupt stops or irregular paths.

## How it is run
Executed automatically when loaded as part of the `npc_live` module; no direct command-line execution. `git grep` results show no external files calling it directly (no matches found).

## Inputs
Internal state from `st["actors"]` (actor positions, speeds), `nl.tick` (NPC update loop), and actor location data via `get_actor_location()`.

## Outputs
Console output of motion statistics (frames, step distances, jerk values), internal state modifications to `st["trace"]` during recording.

## Key functions
traced - Replaces `tick` to record locations of fast-moving actors
Motion analysis - Calculates step distances, still frames, and step variation

## Depends on
npc_live (accessed via `sys.modules["npc_live"]`), math, sys, time

## Gotchas
- Speed threshold of 25 units for triggering recording
- Requires at least 20 movement frames for analysis
- Uses actor labels for output if available; otherwise uses actor ID
- Analyzes step distances via Euclidean distance (math.hypot)
- Automatically stops and analyzes data when "trace" state is already active

Source: read, not executed.
