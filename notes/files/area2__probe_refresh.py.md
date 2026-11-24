## Purpose
This script verifies bone transformation consistency and rendering settings for the character "Aela" in Skyrim by comparing rendered bone positions against set positions. It ensures animation fidelity and correct bone hierarchy synchronization during runtime.

## How it is run
Run as a direct script execution within Skyrim's Unreal Engine Python environment (no command-line arguments). No other files call it (confirmed by `git grep` finding no references to `probe_refresh.py`).

## Inputs
- In-game actor state from `npc_live._state` (specifically actor with label containing "Aela")
- Hardcoded bone name "NPC L Hand [LHnd]"
- Current component bone transform data via Unreal Engine API

## Outputs
- Console logs showing bone position comparisons (e.g., `before render (x y z) set (x y z)`)
- Modified component properties in game state (via `set_skinned_asset_and_update`, `set_forced_lod`, etc.)

## Key functions
chk
set_skinned_asset_and_update
set_forced_lod
set_component_tick_enabled
set_editor_property

## Depends on
npc_live (sys.modules["npc_live"])
unreal engine API

## Gotchas
- Hardcoded actor name "Aela" will fail if the actor is not present
- Bone name "NPC L Hand [LHnd]" is hardcoded and may not match other builds
- Modifies critical rendering properties without user confirmation
- Exceptions during operations are logged but not handled (e.g., "a", "b", "c", "d" prefixes)
- Requires `npc_live` module to be active during execution

Source: read, not executed.
