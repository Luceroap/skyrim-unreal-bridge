# Tuning Constants

| name                | value                     | file:line                                          | what it controls                                                                 |
|---------------------|---------------------------|----------------------------------------------------|----------------------------------------------------------------------------------|
| MAX_NPCS            | 12                        | area2/npc_live_before_cursor.py:16                 | maximum number of NPCs                                                           |
| RADIUS              | 5200.0                    | area2/npc_live_before_cursor.py:17                 | Skyrim units from camera (~75 m)                                                 |
| UPDATE_HZ           | 15.0                      | area2/npc_live_before_cursor.py:18                 | stream update frequency (Hz)                                                     |
| FLIP                | (1.0, -1.0, 1.0)          | area2/npc_live_before_cursor.py:19                 | unsure                                                                           |
| POSES_PER_FRAME     | 5                         | area2/npc_live_before_cursor_frozen.py:19         | limb updates per editor frame (~0.5-1 ms each)                                   |
| UPDATE_HZ           | 60.0                      | area2/npc_live_before_cursor_frozen.py:20         | stream polls; stream ~30 Hz, motion interpolated every frame                     |
| DETACH              | 0x08000208                | demo.py:7                                          | process creation flags (DETACHED_PROCESS, NEW_PROCESS_GROUP, NO_WINDOW)           |
| DETACH              | 0x01000208                | play.py:14                                         | process creation flags (DETACHED_PROCESS, NEW_PROCESS_GROUP, BREAKAWAY_FROM_JOB) |
| HIDDEN              | 0x08000000                | start_bridge.py:13                                 | unsure                                                                           |
| SCALE               | 0.014287                  | tools/blender_export.py:7                          | Skyrim unit to meter scale factor                                                |
| TILE_UNITS          | 512.0                     | tools/esm_land_tex.py:14                           | landscape texture repeat size (Skyrim units)                                     |
| TEX_UNITS           | 512.0                     | tools/land_textures.py:42                          | landscape texture repeat size (Skyrim units)                                     |
| LAYER_MAX           | 2048                      | tools/land_textures.py:43                          | extracted LTEX PNGs capped size (pixels)                                         |
| BLEND_DEPTH         | 0.3                       | tools/land_textures.py:44                          | height-blend band weight units                                                   |
| TILE                | 4                         | tools/land_textures.py:45                          | cells per FBX tile side                                                          |
| NEAR_L8             | 110000.0                  | tools/lod_terrain.py:18                            | level-16 tiles centre distance threshold for level-8 tiles use                   |
| SINK                | 60.0                      | tools/lod_terrain.py:19                            | unsure                                                                           |
| TIMEOUT             | 1500                      | tools/run_local_queue.py:14                        | task timeout in seconds                                                          |
| CAP                 | 55000                     | tools/run_local_queue.py:69                        | character limit per task (pasted material)                                       |
| HDR                 | 32                        | tools/stream_coverage.py:8                         | packet header size                                                               |
| TILE_UNITS          | 512.0                     | tools/tamriel_terrain.py:37                        | landscape texture repeat size (Skyrim units)                                     |
| SKIRT               | 96.0                      | tools/tamriel_terrain.py:38                        | unsure                                                                           |
| STEP                | 128.0                     | tools/water_flow.py:13                             | unsure                                                                           |
| SIG                 | 3.0                       | tools/water_flow.py:49                             | river bend width factor (squares)                                                |
| MIE_DEFAULT         | 0.003996                  | unreal/SkyBridge/atmosphere.py:19                  | SkyAtmosphereComponent Mie scattering scale                                      |
| RADIUS              | 5600.0                    | unreal/SkyBridge/grass_live.py:16                  | Skyrim units radius (~80 m)                                                      |
| NEAR_SHADOW         | 1500.0                    | unreal/SkyBridge/grass_live.py:17                  | tiles closer than this cast shadows (~21 m)                                      |
| CULL                | (6500, 8200)              | unreal/SkyBridge/grass_live.py:18                  | per-instance fade start/end (cm)                                                 |
| REBUILDS_PER_CALL   | 6                         | unreal/SkyBridge/grass_live.py:19                  | rebuilds per render call                                                         |
| WS_OFFSET           | 236                       | unreal/SkyBridge/grass_live.py:23                  | unsure                                                                           |
| SINK                | 10.0                      | unreal/SkyBridge/land_terrain_live.py:23           | terrain sinking depth below old terrain (Skyrim units)                           |
| NL                  | 16                        | unreal/SkyBridge/land_terrain_live.py:24           | unsure                                                                           |
| MAT_VERSION         | 1                         | unreal/SkyBridge/land_terrain_live.py:25           | material version number                                                          |
| MAX_SPAWN_PER_TICK  | 30                        | unreal/SkyBridge/live_bridge.py:16                 | max NPC spawns per game tick                                                     |
| WORLD_RADIUS        | 14000.0                   | unreal/SkyBridge/live_bridge.py:17                 | world radius (must match plugin)                                                 |
| SEA_LEVEL           | -14000.0                  | unreal/SkyBridge/live_bridge.py:19                 | sea level (cm), planet surface for atmosphere/clouds                              |
| LEVEL_FREE_GB       | (8.0, 4.0, 2.0)           | unreal/SkyBridge/memory_governor.py:17             | free memory thresholds per level (GB)                                            |
| POOL_MB             | (3000, 2400, 1800, 1200)  | unreal/SkyBridge/memory_governor.py:18             | memory pool size per level (MB)                                                  |
| MIP_BIAS            | (0.0, 0.0, 0.5, 1.0)      | unreal/SkyBridge/memory_governor.py:19             | mipmap bias per level                                                            |
| CHECK_S             | 10.0                      | unreal/SkyBridge/memory_governor.py:20             | memory check interval (seconds)                                                  |
| SWEEP_S             | (120.0, 60.0, 25.0, 20.0) | unreal/SkyBridge/memory_governor.py:21             | memory sweep intervals (seconds)                                                 |
| IDLE_S              | (300.0, 120.0, 45.0, 20.0) | unreal/SkyBridge/memory_governor.py:22             | idle intervals between sweeps (seconds)                                          |
| MAX_UNLOAD          | 60                        | unreal/SkyBridge/memory_governor.py:23             | maximum packages unloaded per sweep                                              |
| CREATURE_SLOTS      | 6                         | unreal/SkyBridge/npc_live.py:17                    | NPCs slots reserved for nearest creatures                                        |
| POSE_BUDGET         | (0.002, 0.008, 0.08)      | unreal/SkyBridge/npc_live.py:19                    | limb update time budget (seconds)                                                |
| RAIN_SCALE          | (0.007, 0.007, 0.35)      | unreal/SkyBridge/remaster_materials.py:402         | rain streak instance scale (x/y/z)                                               |
| CHUNK_UNITS         | 16384                     | unreal/SkyBridge/tamriel_live.py:22                | chunk size in Skyrim units (4 × 4096)                                            |
| MAX_OUTSTANDING     | 40                        | unreal/SkyBridge/tamriel_live.py:24                | models requested from asset service simultaneously                               |
| SNOW_COUNT          | 14000                     | unreal/SkyBridge/weather_fx.py:25                  | snowflakes per cubic metre                                                       |
| SNOW_SCALE          | (0.035, 0.035, 1.0)       | unreal/SkyBridge/weather_fx.py:26                  | snowflake size (x/y/z, 3.5 cm flakes)                                            |
