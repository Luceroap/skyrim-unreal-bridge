## Purpose
This file instruments the NPC tick processing in the `npc_live` module to profile performance metrics, including timing statistics and per-actor data during runtime.

## How it is run
Executed as part of the `npc_live` module's initialization (via import). No external caller files were found in the project via `git grep` for `prof_npc.py`, indicating it is triggered internally by the `npc_live` module.

## Inputs
Existing state in `npc_live._state` (checks for presence of the `prof` key).

## Outputs
Console logs displaying profiling statistics (time per frame, call rate) and per-actor metrics (distance, stream delta, history length).

## Key functions
timed: Wraps original NPC tick with timing instrumentation.

## Depends on
npc_live module (accesses `nl._state`), sys, time.

## Gotchas
- Profiling toggles on/off with each import (starts on first import, prints stats and stops on subsequent imports).
- Prints verbose actor metrics (distance, dt, history count) for up to 12 actors on stop.
- Requires `npc_live._state` to store profiling state; fails if not present.
- Output includes wall-time-adjusted metrics (e.g., "0.5 ms per second of wall time").
- Actor metrics are truncated to first 12 entries in the actors dictionary.

Source: read, not executed.
