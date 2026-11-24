## Purpose
Resets specific state variables (rest0v, refcs, rest0s) for all NPC actors by removing them from internal data structures. This facilitates synchronization between Skyrim and Unreal Engine by clearing temporary or outdated actor states.

## How it is run
Executed as a Python script (e.g., `python swap_reset.py`). No other files directly call it, as confirmed by `git grep` showing no references to `swap_reset.py` in the project.

## Inputs
- Internal state managed by the `npc_live` module (`nl._state["actors"]`), which contains actor data structures.

## Outputs
- Prints to stdout: `reset <count>` (e.g., `reset 42`), where `<count>` is the number of actors processed.
- Modifies the shared `npc_live._state` in-memory data structure (no files or external outputs).

## Key functions
- Reset actor state keys
- Print actor count
- Modify shared memory in-place
- Execute external script (swap_npc.py)
- Clear specific actor metadata

## Depends on
- `area2/swap_npc.py` (executed via `exec` at the start)
- `npc_live.py` (imported via `sys.modules["npc_live"]`)

## Gotchas
- Modifies shared memory (`nl._state["actors"]`) in-place, affecting all references to this state.
- Relies on `npc_live` module being loaded before execution.
- `swap_npc.py` is executed unconditionally at the start of this script.
- Output message format is hard-coded (`reset <count>`).
- Uses `.pop(k, None)` to safely remove keys without errors if missing.

Source: read, not executed.
