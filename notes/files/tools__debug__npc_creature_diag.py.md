## Purpose
Debugging tool for inspecting the runtime state of NPC and creature actors within the Skyrim-Unreal bridge integration. Displays critical runtime properties including spawn status, skeletal data, and spatial coordinates for verification.

## How it is run
Run directly as a Python script: `python tools/debug/npc_creature_diag.py`. No other project files reference or call this script (confirmed by empty `git grep` results).

## Inputs
- Actor state data stored in `npc_live._state["actors"]` (populated by main bridge integration logic)

## Outputs
Console output listing actor details in the format:
```
spawned: [count]
  [actor_label] ready=[bool] bones=[count] scale=[float] loc=[x,y,z]
```

## Key functions
get_actor_label
get_actor_scale3d
get_actor_location
e.get("ready")
len(e.get("names", ()))

## Depends on
npc_live.py
unreal module

## Gotchas
- No other project files call this script (empty `git grep` result)
- Relies on internal `npc_live._state` structure (not public API)
- Expects all actors to have `actor` object with required methods

Source: read, not executed.
