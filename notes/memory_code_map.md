# Memory Management Overview

**memory_governor.py:23**  
What it does: Maximum packages unloaded per memory sweep.  
What triggers it: Memory governor tick (from `live_bridge.py:1114-1115`).  
What it limits: `MAX_UNLOAD` (60) packages per unload sweep to avoid rendering pauses.

**memory_governor.py:4**  
What it does: Memory levels (0-3) adjust texture pool size and mip bias.  
What triggers it: System RAM free space thresholds (e.g., 8GB+ free = level 0).  
What it limits: Texture pool size (higher levels shrink pool) and mip bias (lower mips).

**memory_governor.py:106**  
What it does: Explicit garbage collection call.  
What triggers it: Memory governor tick (from `memory_governor.py:106`).  
What it limits: No direct limit; triggers full GC pass.

**live_bridge.py:16**  
What it does: Maximum actors spawned per tick.  
What triggers it: Main editor tick (`live_bridge.py:626-630`).  
What it limits: `MAX_SPAWN_PER_TICK` (30) actor spawns per tick.

**live_bridge.py:23**  
What it does: Engine memory limits (models, refs, lights).  
What triggers it: Engine initialization (hardcoded in code).  
What it limits: `MAX_MODELS` (4096), `MAX_REFS` (16384), `MAX_LIGHTS` (512).

**live_bridge.py:516**  
What it does: Prefetch import task budget (3 per tick).  
What triggers it: Background prefetch step (`live_bridge.py:683-686`).  
What it limits: 3 import tasks per tick for background asset conversion.

**live_bridge.py:656**  
What it does: Spawning budget for actor generation.  
What triggers it: `city_some` function (`live_bridge.py:656-669`).  
What it limits: Remaining budget after initial `MAX_SPAWN_PER_TICK` usage.

**offline_import.py:4**  
What it does: Time and model count limits.  
What triggers it: Environment variables (`OFFLINE_LIMIT`, `OFFLINE_MINUTES`).  
What it limits: Model processing count (`OFFLINE_LIMIT`) and time (`OFFLINE_MINUTES`).

**offline_import.py:16**  
What it does: Time budget calculation.  
What triggers it: Start of import loop (`offline_import.py:16-32`).  
What it limits: Time spent per import session (`OFFLINE_MINUTES` * 60 seconds).

**grass_live.py:185**  
What it does: Rebuild budget for terrain.  
What triggers it: Main loop (`grass_live.py:187-212`).  
What it limits: `REBUILDS_PER_CALL` (per function call) terrain rebuilds.

**npc_live.py:16**  
What it does: Maximum NPCs allowed.  
What triggers it: NPC spawning logic (`npc_live.py:760`).  
What it limits: `MAX_NPCS` (12) total NPCs active.

**tamriel_live.py:24**  
What it does: Maximum concurrent asset requests.  
What triggers it: Asset service request loop (`tamriel_live.py:244`).  
What it limits: `MAX_OUTSTANDING` (40) models requested at once.

**memory_governor.py:129**  
What it does: Cuts candidate packages to `MAX_UNLOAD`.  
What triggers it: Memory governor tick (`memory_governor.py:129`).  
What it limits: Number of packages processed per unload sweep (60).

**offline_import.py:42**  
What it does: Garbage collection call.  
What triggers it: Time-based checkpoint (`offline_import.py:42`).  
What it limits: No limit; triggers GC during import.

**weather_fx.py:72**  
What it does: Garbage collection call.  
What triggers it: Weather effect loop (`weather_fx.py:72`).  
What it limits: No limit; triggers GC during weather processing.

**memory_status.json**  
*Not present in provided code.*

# Things that create actors or import assets without any cap

**fire_fx.py:108**  
`spawn_actor_from_class` for each light meeting `MIN_I <= i <= MAX_I` range.  
No budget check; processes all lights within range (unbounded).

**weather_fx.py:328**  
`spawn_actor_from_class` for decal effects (e.g., rain splashes).  
No budget check; no explicit cap on actor count per frame.
