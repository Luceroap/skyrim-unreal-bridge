## Purpose
Analyzes NPC movement plans in the Skyrim game bridge by inspecting actor data. Provides debugging output for plan structure and minor node counts.

## How it is run
Run as `python area2/probe_plan.py` directly. No other files in the project reference it (confirmed via `git grep` with no results).

## Inputs
Game state stored in `nl._state["actors"]`, specifically the first actor with a "plan" entry.

## Outputs
Console output showing:
- Number of plan bones (`len(e["plan"])`)
- Count of minor plan nodes (`sum(1 for p in e["plan"] if p[4])`)
- Alphabetically sorted list of plan entry prefixes (`sorted(p[0] for p in e["plan"])`)

## Key functions
- Accessing `nl._state["actors"]` for actor data
- Counting minor plan nodes via `sum(1 for p in e["plan"] if p[4])`
- Sorting plan prefixes with `sorted(p[0] for p in e["plan"])`
- Extracting first actor with `plan` key via `next(e for e in ... if e.get("plan"))`

## Depends on
- `area2/npc_live.py` (accessed via `sys.modules["npc_live"]`)

## Gotchas
- Raises `StopIteration` if no actor has a "plan" entry
- Relies on plan entries having at least 5 elements (index 4 exists)
- Assumes plan entries follow structure where `p[4]` indicates minor nodes
- Output format depends on internal game state structure
- No error handling for missing plan data

Source: read, not executed.
