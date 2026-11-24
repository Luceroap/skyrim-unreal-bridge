## Purpose
Recompiles a specific material asset in Unreal Engine to apply graph changes without manual reloading. Designed for debugging material graph updates during development.

## How it is run
Executed as a standalone Python script via Unreal Engine's Python interpreter. No other project files call it (confirmed by `git grep` with no results).

## Inputs
Hardcoded asset path: `/Game/Area2Tex/M_SkyWater`.

## Outputs
Prints `recompiled` to console. Updates the material's compiled state in Unreal's memory (no disk file changes).

## Key functions
load_asset
recompile_material
print

## Depends on
Unreal Engine's Python API (`unreal` module).

## Gotchas
Hardcoded asset path; requires Unreal Engine Python environment; debug-only tool (not for production use).
Source: read, not executed.
