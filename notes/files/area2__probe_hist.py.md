## Purpose
Traces high-speed actor movement samples by recording timestamps and position data when speed exceeds 25. Automatically computes and prints statistical summaries of movement patterns upon disabling the trace.

## How it is run
Not executed via command line; triggered automatically during NPC live module initialization via import. No other project files reference it (confirmed via `git grep`).

## Inputs
Game state from `npc_live._state`, specifically entries containing `speed > 25` and non-empty `hist` key.

## Outputs
- Stores timestamp/position pairs in `st["htrace"]` (dictionary in `_state`)
- Prints statistical analysis to stdout when trace is disabled (samples, identical points, time intervals, movement distances)

## Key functions
ing: Collects high-speed movement samples  
stats_report: Computes time/position statistics  
print_summary: Outputs analysis results

## Depends on
`npc_live` module (via `sys.modules["npc_live"]`), `sys`, `time`, `math` standard libraries

## Gotchas
none noticed  
Source: read, not executed.
