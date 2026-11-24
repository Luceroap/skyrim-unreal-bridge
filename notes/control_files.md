# Control Files and Flags

| name | where it is checked (file:line) | accepted values | effect |
|------|--------------------------------|-----------------|--------|
| debug_flags.txt | unreal/SkyBridge/live_bridge.py:1025 | Flags listed in file (e.g., "notamriel") | Turns off distant layer (requires editor restart) |
| addons.txt | unreal/SkyBridge/live_bridge.py:970 | Non-comment lines in file | Loads add-on modules (each line defines spawn/update/clear) |
| no_autostart.txt | unreal/SkyBridge/Content/Python/init_unreal.py:5 | File existence | Prevents autostart of the bridge |
| prefetch_on.txt | unreal/SkyBridge/live_bridge.py:683 | File existence | Enables asset prefetching (~100 assets/min) |
| shot_request.txt | unreal/SkyBridge/live_bridge.py:1036 | File existence | Triggers screenshot capture |
| exec_request.py | unreal/SkyBridge/live_bridge.py:1044 | File existence | Executes Python script (exec hook) |
| os.environ.FORCE | tools/blender_export.py:11, tools/grass_blender.py:35, land_terrain.py:49 | Presence (e.g., "1") | Skips file existence checks (force overwrite) |
| os.environ.OFFLINE_LIMIT | unreal/SkyBridge/offline_import.py:15 | Integer | Sets limit for offline processing |
| os.environ.OFFLINE_MINUTES | unreal/SkyBridge/offline_import.py:16 | Float (minutes) | Sets time budget for offline processing |
| os.environ.OFFLINE_NPCS | unreal/SkyBridge/offline_import.py:49 | "0" disables | Enables NPC processing in offline mode |
| os.environ.SKY_LOD_WATER | unreal/SkyBridge/remaster_materials.py:809 | Presence | Enables LOD water for remastering |
| os.environ.SKY_LOD_TERRAIN | unreal/SkyBridge/remaster_materials.py:838 | Presence | Enables LOD terrain for remastering |
| os.environ.SKY_CONVERT_MATERIALS | unreal/SkyBridge/remaster_materials.py:845 | Presence | Triggers material conversion |
| --no-remaster | play.py:58 | Flag presence | Skips remastering process |
| --stop | play.py:104 | Flag presence | Stops bridge execution |
| --no-autobuild | play.py:134 | Flag presence | Prevents building characters/creatures |
| --keep-weather | play.py:140 | Flag presence | Preserves weather settings during rebuild |
| --dungeons | distant_world.py:373 | Flag presence | Dumps dungeon data |
| --world | distant_world.py:376 | Argument (e.g., "whiterunworld") | Dumps specific world data |
| --interiors | distant_world.py:379 | Flag presence | Dumps interior world data |
| --water | distant_world.py:382 | Flag presence | Dumps water data |
| --stats | distant_world.py:440, grass_placement.py:613, tamriel_world.py:195 | Flag presence | Enables statistics output |
| --vanilla | grass_placement.py:602 | Flag presence | Uses vanilla grass overrides (disables mods) |
| --no-queue | grass_placement.py:419 | Flag presence | Disables queued processing |
| --preview | grass_placement.py:621 | Flag presence | Enables preview mode for terrain |
| --models | grass_placement.py:618 | Flag presence | Processes geometry models |
| --blender | land_terrain.py:99 | Flag presence | Triggers Blender export for terrain |
| --blender-obj | land_terrain.py:99 | Flag presence | Triggers Blender export for objects |
| --no-tex | land_terrain.py:374 | Flag presence | Skips texture processing |
| --lod | land_terrain.py:460 | Flag presence | Enables Level of Detail (LOD) processing |
| --no-fbx | land_terrain.py:462, land_textures.py:662 | Flag presence | Skips FBX export |
| --quiet | land_terrain.py:465 | Flag presence | Reduces output verbosity |
| --old-thumbs | land_textures.py:598 | Flag presence | Uses old thumbnail generation |
| --force | land_textures.py:604 | Flag presence | Forces texture processing |
| --no-bake | land_textures.py:641 | Flag presence | Skips texture baking |
| --no-lod | land_textures.py:660 | Flag presence | Skips LOD processing |
| --no-restart-ue | tools/auto_build.py:29 | Flag presence | Prevents UE restart after build |
| --only= | npc_batch.py:65 | Value (e.g., "guard") | Processes specific NPC types |
| --autobuild | npc_batch.py:40 | Flag presence | Enables automatic NPC rebuilding |
| --dump | npc_hair_tint.py:54 | Flag presence | Dumps hair tint configuration data |
| --limit | offline_import.py:35 | Integer | Sets processing limit |
| --minutes | offline_import.py:35 | Float | Sets time budget for offline |
| --even-if-skyrim | offline_import.py:31 | Flag presence | Runs even if Skyrim is active |
| --no-shutdown | shutdown_after_import.py:48 | Flag presence | Prevents automatic shutdown after import |
| --undo | skyrim_lightweight.py:50 | Flag presence | Undoes previous import operation |
| --restore | skyrim_plugins.py:20 | Flag presence | Restores plugin configuration |
| --land | tamriel_terrain.py:421 | Flag presence | Dumps land terrain data |
| --low | tamriel_terrain.py:423 | Flag presence | Uses low-detail terrain |
| --chunk | tamriel_terrain.py:427 | Two numbers (x,y) | Processes specific terrain chunk |
| --serve | tamriel_terrain.py:432 | Flag presence | Enables terrain serving mode |
