## Purpose
Removes duplicate actors and city entities from game data by comparing model, position, and rotation within specific tolerances. Ensures only unique entities persist in the runtime structures.

## How it is run
Executed directly as a Python script (e.g., `python fix_dup.py`). `git grep` for `fix_dup.py` yielded no results, indicating no other project files call it.

## Inputs
- `live.actors` (dictionary of actor data)
- `live.city` (city entity data)
- `live_bridge.py` (source file content, modified before execution)

## Outputs
- Console output: `removed stream twins X city twins Y`
- Modified `live.actors` and `live.city` structures (duplicates removed)
- No file writes or external I/O

## Key functions
L.near (position comparison)
Rotation tolerance check
City meta duplicate check
Actor removal logic
Stream twin count output

## Depends on
live_bridge.py
live module (actors/city structures)

## Gotchas
Hardcoded position tolerance of 3.0
Hardcoded rotation tolerance of 0.01
Replaces "\nstart()\n" with "\n" in live_bridge.py
Hardcoded Windows absolute path in script
Script executes modified live_bridge.py content via exec

Source: read, not executed.
