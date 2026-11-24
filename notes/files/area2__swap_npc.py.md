## Purpose
The script reloads the `npc_live` module to update NPC state without resetting actors. It preserves actor positions (rest0) and gear data during the module reload, ensuring NPCs maintain their current state.

## How it is run
Executed via `exec(open(...).read())` from `area2/fix_npc_mats.py` and `area2/swap_reset.py`. No direct command-line invocation.

## Inputs
None. Reads and modifies global state of `npc_live` module in memory.

## Outputs
Prints: `npc_live swapped; npcs kept: [count]` (where [count] is the number of preserved NPCs). Modifies `npc_live._state` and `npc_live._gear` in-place.

## Key functions
- Reload `npc_live` module using `importlib.reload`
- Preserve actor rest positions via `rest0q` key
- Migrate actor state to new module instance
- Update module gear data from preserved state

## Depends on
- `npc_live` module (project module)
- `importlib` (standard library)
- `sys` (standard library)

## Gotchas
- Requires `npc_live` module to have `_state` and `_gear` attributes
- Skips actors with pre-existing "rest0q" entry
- Print count reflects `npc_live._state["actors"]` length post-swap
- Module state modification is non-reversible without restart

Source: read, not executed.
