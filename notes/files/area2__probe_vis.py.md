## Purpose
Debugging script for visualizing Skyrim NPC actor states in the Unreal bridge. Outputs visibility, location, and bounding box data for the first five NPCs to the console during development.

## How it is run
Executed directly via command line (e.g., `python area2/probe_vis.py`). No other files call it, as confirmed by empty `git grep` results.

## Inputs
Runtime NPC data via `npc_live._state["actors"]` (internal project state).

## Outputs
Console output with actor labels, visibility status, location coordinates, scale, bounding box values, head position, and mesh names.

## Key functions
get_actor_bounds
is_visible
is_hidden_ed
get_actor_location
get_actor_scale3d
get_socket_location
get_skinned_asset
get_name
get_actor_label

## Depends on
npc_live.py (imports via `sys.modules["npc_live"]`)

## Gotchas
Only processes first 5 actors (index `[:5]`); hard-coded bone name "NPC Head [Head]" may become invalid if game data changes.

Source: read, not executed.
