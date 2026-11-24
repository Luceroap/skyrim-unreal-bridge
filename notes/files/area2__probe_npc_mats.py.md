## Purpose
This script inspects material assignments for specific NPC actors (Carlotta and Jenassa) in the Skyrim-Unreal bridge project. It outputs material slot names and associated properties from Unreal Engine's material system for debugging purposes.

## How it is run
Command: `python area2/probe_npc_mats.py`. No other project files reference or call this script, as confirmed by `git grep` results (no matches found).

## Inputs
Runtime state from `npc_live` module's `_state["actors"]` dictionary, containing actor data with labels matching "Carlotta" or "Jenassa".

## Outputs
Console output formatted as:
```
== [actor label] [mesh name]
   [material slot name] -> [material name] [info]
```

## Key functions
get_actor_label
get_skinned_asset
get_editor_property
get_name
get_material_instance_texture_parameter_value

## Depends on
area2/npc_live.py (via `sys.modules["npc_live"]`)

## Gotchas
- Only processes actors with labels containing "Carlotta" or "Jenassa"
- Requires the `npc_live` module to be loaded in the runtime context
- Outputs material properties directly from Unreal Engine's internal API

Source: read, not executed.
