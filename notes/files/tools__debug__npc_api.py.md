## Purpose
This script inspects Unreal Engine classes (PoseableMeshComponent and Actor) for methods related to refreshing, ticking, or updating. It is used for debugging Unreal Engine API interactions within the SkyrimUnrealBridge project.

## How it is run
Run via Unreal editor's Python console or command line. No other project files call this script (confirmed by empty `git grep` result for `npc_api.py`).

## Inputs
None (relies on Unreal Engine environment context).

## Outputs
Console output of method names containing keywords like "refresh", "tick", "update", etc., from Unreal classes.

## Key functions
Inspect class methods via dir()
Print filtered method lists

## Depends on
unreal module (Unreal Engine Python API)

## Gotchas
- Requires Unreal Engine to be running for `import unreal` to succeed
- No external inputs or arguments
- Output is printed to console only; no files or shared memory modified
- Confirmed no other project files reference this script via `git grep`

Source: read, not executed.
