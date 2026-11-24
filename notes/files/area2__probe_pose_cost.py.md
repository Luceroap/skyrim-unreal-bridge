## Purpose
This script benchmarks the performance of pose application operations for NPCs in the Skyrim-Unreal bridge, measuring the time cost of near and far pose transitions across multiple actors.

## How it is run
Execute directly with `python probe_pose_cost.py`. The `git grep` command found no references to `probe_pose_cost.py` in other project files, indicating it is not called as part of the main application flow.

## Inputs
Reads NPC pose data from `nl._state["actors"]` (via `npc_live` module), specifically the `shown["pose"]` and `shown["sex"]` fields for each actor.

## Outputs
Prints formatted timing results to standard output (e.g., `ActorName near 1.23 ms far 4.56 ms`), showing average time per pose application for the first six NPCs.

## Key functions
Measure near poses
Measure far poses
Format output results
Print benchmark data
Loop over actors

## Depends on
`npc_live.py` (accessed via `sys.modules["npc_live"]`), specifically its `_apply_pose` method.

## Gotchas
none noticed
Source: read, not executed.
