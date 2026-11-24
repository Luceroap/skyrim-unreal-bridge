## Purpose
Documents lines 350-380 of COORDINATION.md (part 2 of 2), covering NPC integration mechanics in Unreal Engine (npc_live.py). Describes spawn logic, bone pose handling, texture dependencies, and critical memory management considerations observed during runtime.

## How it is run
Command line: `play.py` (via Play.bat or desktop shortcut "Play Skyrim (Unreal)"). This kills duplicate editors, starts Skyrim and Unreal Editor in parallel, places Unreal over Skyrim, and gives Skyrim focus. `npc_batch.py` (with `--autobuild` flag) and `npc_autobuild.py` are launched by `play.py` to build NPC assets. `live_bridge.tick` calls `npc_live.tick(self)`.

## Inputs
- `area2/npc/export/npc_<baseId>.fbx` (FBX assets imported on demand)
- `area2/npc/skin/skeleton_<key>.json` (skeleton data for `_ingest`)
- `area2/tex/alpha_masked_extra.txt` (for hair alpha masking)
- `area2/tex/multilayer_textures.txt` (for mountain/cliff textures)
- `area2/ready.txt` (assets to import via offline process)

## Outputs
- Spawns up to 12 NPCs within 75m of camera as PoseableMeshComponent actors
- Poses NPC bones using Skyrim's actor stream (divided by actor scale)
- Uses `area2/tex/alpha_masked_extra.txt` for hair alpha masking
- Creates runtime texture mappings via `remaster_materials.configure`
- Generates `area2/npc/tried.txt` (NPC build attempts)

## Key functions
- tick (called by live_bridge.tick)
- ue_bone (handles bone name translation)
- _ensure_rest (reads rest pose before skeleton exists)
- _ingest (imports skeleton + scale)
- _apply_pose (divides bone offsets by actor scale)
- _smooth (sets actor scale3d)
- _read_and_spawn (spawns actors with bone data)
- CREATURE_SLOTS (limits creature spawning to 6 nearest non-humanoids)

## Depends on
- `live_bridge.py` (calls npc_live.tick)
- `area2/npc/export/` (source FBX directory)
- `area2/npc/skin/` (skeleton JSON directory)
- `area2/tex/` (texture configuration files)
- `npc_batch.py` (builds FBX assets for NPCs)

## Gotchas
- Editing npc_live.py requires explicit permission via Requests (not allowed otherwise)
- Unreal renames FBX bones (spaces → '-', brackets → '_') handled by ue_bone
- Rest pose must be read *before* skeleton exists (fixed by _ensure_rest)
- Only one UnrealEditor.exe instance allowed (multiple instances cause memory crash)
- Live city/dungeon prefetch (prefetch_cities) consumes 53GB memory; offline import required

Source: read, not executed.
