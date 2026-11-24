## Purpose
Builds FBX files for every named NPC currently loaded in Skyrim (via the actor stream) that lacks an FBX. Handles both humanoid NPCs (using `npc_build.py`) and non-humanoid creatures (using `npc_build_creature.py`), including texture overrides for armor.

## How it is run
Command line: `python -I npc_batch.py [max]` (requires Skyrim running with bridge plugin). Called by:
- `tools/npc_autobuild.py` (with `--autobuild` and limit=3)
- Mentioned in `COORDINATION.md` (lines 158, 166, 355, 369, 372)

## Inputs
- Memory mapping `Local\\SkyrimUnrealBridge_actors_v1` (actor data)
- Memory mapping `Local\\SkyrimUnrealBridge_gear_v1` (armor data)
- `area2/npc/tried.txt` (previously processed actors)
- Command-line flags: `--force`, `--autobuild`, `--only=...`, numeric limit

## Outputs
- `area2/npc/tried.txt` (appends processed actor base IDs)
- `area2/npc/swaps_<base_id>.json` (texture overrides for gear)
- `area2/npc/npc_<base_id>.fbx` (generated FBXs via `npc_build.py`/`npc_build_creature.py`)

## Key functions
- actor_stream_reader
- gear_data_parser
- tried_file_updater
- texture_override_writer
- npc_build_invoker
- creature_build_invoker

## Depends on
- `tools/npc_build.py`
- `tools/npc_build_creature.py`
- Skyrim bridge plugin (memory maps)

## Gotchas
- Skips player's head (flags & 1)
- Skips actors in `tried.txt` (unless `--force`)
- Default limit: 6 actors per run
- Uses `area2/npc` for all output files
- Excludes generated actors (guards, form IDs 0xFFxxxxxx)

Source: read, not executed.
