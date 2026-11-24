## Purpose
A script to toggle CPU profiling for NPC live updates within the Skyrim-Unreal bridge. It modifies the NPC live module's tick function to enable or disable profiling and outputs profiling statistics when disabled.

## How it is run
Command line: `python area2/prof_npc2.py`. No other files reference this script (confirmed via `git grep`).

## Inputs
None. Operates purely by modifying the runtime state of the `npc_live` module.

## Outputs
Prints profiling statistics to console when stopped (truncated to 4000 characters), and alters the `npc_live.tick` function behavior during runtime.

## Key functions
timed - Wraps NPC tick with profiling.
start/stop toggle - Handles enabling/disabling profiler.

## Depends on
npc_live.py (via `sys.modules["npc_live"]`).

## Gotchas
- Running the script again stops profiling and prints truncated stats.
- Profiling statistics are truncated to 4000 characters.
- Requires `npc_live` module to be already loaded.
- No other files call this script.

Source: read, not executed.
