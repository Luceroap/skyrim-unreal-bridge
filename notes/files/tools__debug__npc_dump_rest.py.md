## Purpose
Dumps NPC rest data from the current game state to a JSON file for debugging. Processes rest0 data from the first active NPC into a structured format.

## How it is run
Run as `python tools/debug/npc_dump_rest.py`. No other project files call it (grep found no references).

## Inputs
Current game state via `npc_live._state["actors"]`.

## Outputs
Writes to `C:\Users\Aidan\SkyrimUnrealBridge\area2\npc\rest0_dump.json` (JSON file containing rest0 data and actor label).

## Key functions
- rest0 data processing
- JSON serialization
- Actor label extraction
- First actor selection
- Output file write

## Depends on
npc_live, unreal

## Gotchas
- Hardcoded Windows path in output location
- Crashes if no NPCs exist in `npc_live._state`
- Assumes `area2/npc` directory exists

Source: read, not executed.
