# Review leads after a verification pass (still from small models: YES = worth a human/strong-model look first, NO = probably a false alarm)

- **YES** | perf | plugin/src/main.cpp:900 | YES - The set is created per-frame (30Hz) as a local variable per ScanActors call, so moving to static avoids redundant allocation/deallocation.  
  lead: Redundant set creation: `std::unordered_set<RE::Actor*> seen;` | Unnecessary per-frame set allocation/deallocation (30Hz) | Move set to static and use clear()
- **YES** | perf | tools/asset_service.py:29 | YES - The code reads the entire requests.txt file every 3-second loop iteration (line 29) without tracking new entries incrementally, causing redundant disk I/O despite the file being small and append-only.  
  lead: repeated disk reads of requests.txt | reads full file every loop iteration causing redundant I/O | use file seek/tail or incremental tracking
- **YES** | perf | tools/npc_batch.py:54 | YES - The 'all' check iterates over the growing 'creatures' list (O(n) per check), leading to O(n²) total operations for n insertions, which a set would reduce to O(1) per check.  
  lead: O(n^2) 'all' check on creature list during insertion | For 1000 creatures, 10^6 checks would occur | Replace 'all' with a set for O(1) lookups
- **YES** | perf | unreal/SkyBridge/atmosphere.py:307 | YES - The function is called per frame from the main loop (live_bridge.py:1034), making the scan of all actors unnecessary each frame.  
  lead: `unreal.EditorLevelLibrary.get_all_level_actors()` called per frame | Unnecessary frame-time cost scanning all level actors (potentially thousands) | Cache held scene capture references instead of scanning actors
- **YES** | perf | unreal/SkyBridge/land_terrain_live.py:306 | YES - The 'spawn' function is called every frame (via 'tick') as shown by line 345's call in the context of the 'tick' function, causing 'material()' to rebuild per frame.  
  lead: parent = material() | Material rebuild called per spawn (invoked every frame via tick) | Full material expression graph rebuild causes heavy per-frame overhead | Build material once at startup and cache the asset
- **YES** | perf | unreal/SkyBridge/live_bridge.py:584 | YES - The code runs per frame in apply_world (called from frame loop), rebuilding a set of thousands of references each frame, matching the O(n) per frame performance issue reported.  
  lead: Building occupied set from reference data | O(n) per frame with n large (thousands of references) | Cache and update set only when reference data changes
- **YES** | perf | unreal/SkyBridge/live_bridge.py:640 | YES - The check loops over all existing actors (self.actors.values()) for each spawn request, making it O(n) per request, and with spawn requests called every tick (per `MAX_SPAWN_PER_TICK`), the total cost becomes O(n²) as actor count grows.  
  lead: O(n^2) duplicate check for spawn requests | Checks all actors per spawn request (e.g., `any(d["model"] == model and ... for d in self.actors.values())`) | Replace with spatial grid for O(1) lookups
- **YES** | perf | unreal/SkyBridge/remaster_materials.py:624 | YES - Called once per material instance during startup (as seen in git grep), leading to repeated disk reads; preloading the set at module level would avoid this.  
  lead: Repeated disk reads for texture lists | `_lines("decal_textures.txt")` is called per material instance | Preload file contents into sets at module level
- **YES** | memory | play.py:74 | YES - The code reads the entire log file into memory before taking the last 30k bytes, which is inefficient for large logs when only the tail is needed.  
  lead: Reading entire log file for last 30000 bytes | Causes high disk I/O and memory usage for large logs; full file read is unnecessary when only tail needed | `open(...).read()[-30000:]` → seek to end then read 30k bytes
- **YES** | memory | tools/asset_service.py:50 | YES - The 'done' set grows indefinitely in memory without cleanup as the service processes models continuously over time (every 3 seconds) in the infinite loop.  
  lead: unbounded 'done' set growth | 'done' set grows indefinitely without cleanup | persist to disk or prune historical entries
- **YES** | memory | tools/npc_batch.py:55 | YES - The 'creatures' list accumulates all qualifying NPCs before applying the 'limit' at line 72, causing memory usage to scale with total NPCs rather than batch size.  
  lead: Full creature list accumulated without limit application | Memory usage scales with total NPCs (not just batch size) | Apply limit during list construction
- **YES** | memory | unreal/SkyBridge/grass_live.py:117 | YES - The st["actors"] dictionary entries are never removed when actors are destroyed (e.g., via act.destroy_actor() in grass_live.py:224), causing unbounded memory growth.  
  lead: Unbounded actor growth in st["actors"] | Actors persist for all models ever loaded (never destroyed) | Destroy actors for models not in current tile set during updates
- **YES** | memory | unreal/SkyBridge/live_bridge.py:486 | YES - Mesh cache grows indefinitely without cleanup as new unique asset names are stored without eviction.  
  lead: Mesh cache unbounded growth | Mesh cache grows indefinitely as new assets are loaded without cleanup mechanism | Add cache size limit or LRU eviction
- **YES** | memory | unreal/SkyBridge/tamriel_live.py:298 | YES - self.built[key] = a is called without any mechanism to remove entries, accumulating actors as player travels.  
  lead: self.built dict never cleared | As the player travels, more actors are built and stored, causing memory to grow without bound | self.built[key] = a
- **YES** | bug | plugin/src/main.cpp:860 | YES - Exceptions are swallowed without logging, causing silent failure that could mask critical errors in a high-frequency game loop (30 Hz), violating safe exception handling practices.  
  lead: Swallowing exceptions: `__except (EXCEPTION_EXECUTE_HANDLER) { return false; }` | Critical errors hidden without logging, causing silent failure | Log exception details and return false
- **YES** | bug | shared/BridgeShared.h:92 | YES - The current kMaxActors=96 is exceeded in scenes with >96 actors (as confirmed by review finding), causing omission; increasing to 256 resolves the issue as the code runs per frame (~30 Hz) and typical Skyrim scenes can exceed 96 actors.  
  lead: kMaxActors = 96 for actor pose stream | Exceeding 96 actors causes omission, leading to missing actors in Unreal | Increase kMaxActors to 256
- **YES** | bug | tools/nif2obj.py:190 | YES - The code replaces the dot in texture names (e.g., "texture.png" → "texture_png"), causing MTL references to expect "texture_png" instead of "texture.png", breaking file lookups.  
  lead: Texture name replacement breaks file references | Replaces dots with underscores, so MTL will look for "texture_png" but the texture is "texture.png" | Remove the dot replacement in material name processing
- **YES** | bug | tools/npc_autobuild.py:5 | YES - Hard-coded path "C:\Users\Aidan\SkyrimUnrealBridge" is used directly and would break if the project is moved or username differs.  
  lead: hard-coded path | breaks if project moved or user has different username | use config file or environment variable
- **YES** | bug | tools/offline_import.py:15 | YES - Missing quotes around filter string cause tasklist to misinterpret arguments, leading to incorrect process detection.  
  lead: `tasklist /FI "IMAGENAME eq " + exe` | missing quotes breaks process detection | wrap filter in quotes: `"/FI \"IMAGENAME eq " + exe + "\""`
- **YES** | bug | tools/offline_import.py:44 | YES - The code opens "offline_import.log" in "area2" but the actual log is written to "offline_import_stdout.log" at the ROOT level as defined in line 36.  
  lead: `open(os.path.join(ROOT, "area2", "offline_import.log"))` | reads wrong log file (not `offline_import_stdout.log`) | fix file path to match log destination
- **YES** | bug | unreal/SkyBridge/grass_live.py:13 | YES - Hard-coded user-specific absolute path will break on any other machine/user, requiring relative path or config variable for portability.  
  lead: Hard-coded absolute path (AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2") | Path references user-specific directory and will break for other users/machines | Replace with relative path "area2" or config variable
- **YES** | bug | unreal/SkyBridge/memory_governor.py:68 | YES - The exception is silently swallowed (pass) instead of logged, causing cache staleness when texture retrieval fails, which aligns with the review finding.  
  lead: silently swallow exception in _textures | cache may become stale, preventing correct asset unloading | log error instead of passing
- **YES** | bug | unreal/SkyBridge/memory_governor.py:88 | YES - The code silently swallows exceptions in a critical path (per-frame asset scanning) leading to potential misidentification of used assets, which matches the review's bug report.  
  lead: silently swallow exception in _in_use | may misidentify used assets, causing incorrect unloading | log error instead of passing
- **YES** | bug | unreal/SkyBridge/remaster_materials.py:140 | YES - The `except Exception` block silently returns the material without logging or re-raising, leaving silent errors that could break material upgrades without user notification, contradicting the safe handling required for graph modifications.  
  lead: Silent exception swallowing during M_SkyMaster graph upgrade | Could leave materials in broken state without user notification | Log error and re-raise exception
- **YES** | robustness | shared/BridgeShared.h:92 | YES - The current kMaxActors=96 is exceeded in scenes with >96 actors (as confirmed by review finding), causing omission; increasing to 256 resolves the issue as the code runs per frame (~30 Hz) and typical Skyrim scenes can exceed 96 actors.  
  lead: Hard-coded max path length 96 for skeleton paths (kSkelLen) | Truncation of long skeleton paths (e.g., for custom races) may cause skeleton loading failure | Increase kSkelLen to 256
- **YES** | robustness | tools/grass_placement.py:40 | YES - Hard-coded Windows path blocks non-Windows systems and non-default installations, and the code (min_grass_size) is called once at startup to read config, making it a workflow blocker.  
  lead: Hard-coded Skyrim data path: `DATA = r"D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data"` | Tool fails on non-Windows systems or non-default installations, blocking workflow | Replace with config file or command-line argument (e.g., `--data-dir`)
- **YES** | robustness | tools/grass_placement.py:41 | YES - The hard-coded path prevents the tool from functioning if Blender is installed elsewhere, and no command-line argument or config file is provided to override it, as required by the review.  
  lead: Hard-coded Blender path: `BLENDER = r"D:\blender.exe"` | Tool fails if Blender isn't installed at hardcoded path, preventing model conversion | Replace with config file or command-line argument (e.g., `--blender-path`)
- **YES** | robustness | tools/land_terrain.py:244 | YES - Swallowing exceptions during BSA initialization hides errors that could cause missing textures in the game, making debugging impossible without logging.  
  lead: Swallowing all exceptions in BSA initialization | Hides potential errors during initialization, making debugging difficult | Replace `except Exception:` with `except Exception as e: print(e)`
- **YES** | robustness | tools/offline_import.py:9 | YES - Hard-coded path prevents use on systems with different Unreal installation paths or drive letters.  
  lead: `CMD = r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"` | hard-coded path breaks portability | use environment variables or config
- **YES** | robustness | tools/offline_import.py:37 | YES - The print statement references "area2\offline_import.log" but the actual log file path is defined in line 36 as ROOT/offline_import_stdout.log.  
  lead: `print("progress: area2\\offline_import.log")` | logs to `offline_import_stdout.log` not expected path | correct output to match actual log path
- **YES** | robustness | unreal/SkyBridge/land_terrain_live.py:19 | YES - The absolute path `C:\Users\Aidan\SkyrimUnrealBridge\area2` is hard-coded and will break if the project is moved or runs on a different machine, requiring use of Unreal's `unreal.Paths.project_content_dir()` for dynamic path resolution.  
  lead: AREA = r"C:\Users\Aidan\SkyrimUnrealBridge\area2" | Absolute path hard-coded for project location | Breaks if project moves or runs on different user/machine | Use Unreal engine path functions (e.g., unreal.Paths.project_content_dir())
- **YES** | robustness | unreal/SkyBridge/memory_governor.py:16 | YES - Hard-coded path directly depends on user-specific username and directory structure, failing for all other users' project locations.  
  lead: hard-coded absolute path C:\Users\Aidan\SkyrimUnrealBridge\area2 | breaks for users with different paths or project locations | use os.path.join with project root instead
- **YES** | robustness | unreal/SkyBridge/memory_governor.py:25 | YES - TEX_ROOT is hard-coded as "/Game/Area2Tex/" without deriving from AREA variable or config, making it vulnerable to path changes in the Unreal asset structure.  
  lead: hard-coded texture root path /Game/Area2Tex/ | breaks if texture assets are stored in different paths | derive from AREA or use config
- **YES** | cleanup | tools/distant_world.py:16 | YES - Hard-coded Windows path "D:\SteamLibrary\..." is OS-specific and will fail for non-Windows systems or custom Skyrim installations.  
  lead: Hard-coded Skyrim data path | Path "D:\SteamLibrary\steamapps\common\Skyrim Special Edition\Data" is Windows-specific and won't work on other OS or installations. | Use an environment variable (e.g., SKYRIM_DATA_PATH) or search for Skyrim's Data directory during runtime.
- **YES** | performance | unreal/SkyBridge/tamriel_live.py:320 | YES - The loop iterates over `self.built.items()` which grows as new models are added via `self.built[key] = a`, and the function is called from line 463 (a regular update path), causing visibility updates to slow progressively over time as more models are built.  
  lead: update_visibility loops over self.built (growing) | Visibility updates become slower over time as more models are built | self.built.items()
- **YES** | performance | unreal/SkyBridge/tamriel_live.py:410 | YES - Called every frame from line 364 in the game loop (git grep shows direct call to chunk_step), processing camera movement per frame.  
  lead: Reading terrain_ready.txt every tick | Disk I/O per tick (every frame) is heavy | open(os.path.join(TAM, "terrain_ready.txt"))
- **YES** | perf | plugin/src/main.cpp:976 | YES - NormalizeModel is called per frame for the same equipped weapon path without caching, causing redundant string normalization every frame.  
  lead: Repeated NormalizeModel: `const std::string m = NormalizeModel(mp);` | String normalization called multiple times for same path in gear processing | Cache normalized results in map
- **YES** | perf | tools/tamriel_terrain.py:321 | YES - Called per chunk in line 405's loop where 'skip' is passed as None each iteration, re-reading static whiterun_cells() data instead of caching.  
  lead: repeated disk read for whiterun_cells() | called per chunk, but the file is static during the run | cache the result
- **YES** | perf | unreal/SkyBridge/live_bridge.py:1025 | YES - Called every frame (tick_body called from tick in main game loop) causing unnecessary disk I/O per frame.  
  lead: Reading debug_flags.txt every frame | Unnecessary disk I/O per frame | Cache flags and reload on file change
- **YES** | perf | unreal/SkyBridge/npc_live.py:751 | YES - The function is called every frame (per the caller lines 710/738 in the context of a game loop), and sorting the entire list of actors within RADIUS (O(n log n)) is unnecessary when only MAX_NPCS are needed; a min-heap would reduce this to O(n log MAX_NPCS) per frame.  
  lead: Sorting actors within RADIUS by distance every frame | O(n log n) operation per frame could become heavy with many actors | Replace with min-heap to track nearest MAX_NPCS actors during building
- **YES** | perf | unreal/SkyBridge/npc_live.py:787 | YES - Called every frame (per game tick) from _read_and_spawn, processing all actor IDs in _state["actors"] for removal, which is O(n) per frame when active actor count grows.  
  lead: Building actor ID removal list from _state["actors"] | O(n) operation proportional to active actor count, which grows with gameplay | Use active set tracking during actor updates to avoid full rebuild
- **YES** | memory | tools/tamriel_terrain.py:180 | YES - The `src` cache in `Baker` class grows unboundedly as new texture paths are processed without removal, potentially consuming all memory for large texture sets.  
  lead: unbounded cache for texture images in `Baker.src` | `src` cache grows without bound, potentially using all memory for large texture sets | limit cache size with `collections.OrderedDict` and maxsize
- **YES** | bug | tools/asset_service.py:7 | YES - The path is hardcoded as a string literal without configuration, violating the requirement to use a config/environment variable for platform-specific paths.  
  lead: hard-coded Steam path | assumes Skyrim at D:\SteamLibrary\... | use config/environment variable
- **YES** | bug | tools/asset_service.py:48 | YES - Hard-coded path D:\blender.exe assumes Blender's location, causing failure if not present or in a different directory; should use system PATH or configuration.  
  lead: hard-coded Blender path | assumes Blender at D:\blender.exe | use system PATH or config
- **YES** | bug | tools/nif2obj.py:78 | YES - Swallowed exception leads to silent failure without error log, causing empty models when npc_skin is missing or fails.  
  lead: Swallowed exception in fallback | Causes silent failure when npc_skin is missing, leading to empty models without error | Raise specific exceptions or log error instead of returning empty
- **YES** | bug | tools/npc_autobuild.py:15 | YES - The hardcoded "3" is a magic number without context, should be defined as a constant like ACTOR_BATCH_SIZE for clarity and maintainability, as it represents the batch size parameter for npc_batch.py.  
  lead: magic number 3 | unclear meaning, risks future changes breaking logic | define constant (e.g., ACTOR_BATCH_SIZE = 3)
- **YES** | bug | tools/offline_import.py:26 | YES - The current code `sys.argv.index(name) + 1` crashes when `name` is the last argument (no value provided) since it doesn't verify `len(sys.argv) > index + 1`, matching the reported bug.  
  lead: `sys.argv.index(name) + 1` | crashes if argument lacks value | add index check: `if name in sys.argv and len(sys.argv) > index+1`
- **YES** | bug | unreal/SkyBridge/npc_live.py:724 | YES - The distance (dist) is capped at RADIUS (<=100m) as shown by the RADIUS check in _read_and_spawn (lines 748-750), making `e.get("dist", 0.0) > 700` always false.  
  lead: Condition `e.get("dist", 0.0) > 700` always false | Distances are capped at RADIUS (<=100m) but condition uses 700m | Remove redundant condition - poses always applied correctly
- **YES** | bug | unreal/SkyBridge/remaster_materials.py:636 | YES - Exception swallowing hides critical configuration failures that would cause foliage materials to render incorrectly without halting processing, and the function is called repeatedly per material in a loop (lines 611, 836).  
  lead: Silent exception swallowing | `try: ... except Exception as e: log(...)` hides critical material configuration failures | Rethrow exception or halt processing
- **YES** | bug | unreal/SkyBridge/weather_fx.py:295 | YES - The exception swallowing without error logging or failing fast could cause silent failures in real-time weather effects as the function is called multiple times per frame during runtime.  
  lead: `except Exception as e: log(...)` | Effect may break silently without user notice | Log as error and fail fast instead of swallowing
- **YES** | robustness | start_bridge.py:150 | YES - 600s lock wait timeout is excessive for serialized execution calls (typical caller frequency: multiple concurrent agents, not per-frame but often), and the actual UE execution timeout (20s) suggests a 30s max lock wait is reasonable.  
  lead: Excessive UE execution lock timeout | 600-second lock wait timeout is unreasonable for typical usage (minutes) | Reduce to 30 seconds max
- **YES** | robustness | start_bridge.py:475 | YES - The 360-second wait is a one-time startup check, not per-frame, and 6 minutes exceeds practical startup times (typically <1 minute) as confirmed by the context and typical game launch durations.  
  lead: Unnecessarily long frame wait | 360-second (6-minute) wait for frame data exceeds practical startup times | Reduce to 60 seconds
- **YES** | robustness | tools/land_terrain.py:38 | YES - Hardcoded path "landscape\\dirt02.dds" is fixed relative to game data but would break if game texture path changes or file missing, violating flexibility best practice.  
  lead: Hardcoded path for default texture | Will break if the texture path changes or if the file is missing | Use a more flexible path or allow the path to be configured
- **YES** | robustness | tools/npc_skin.py:160 | YES - The default path "skeleton_male.json" is hard-coded and lacks error handling for missing files, causing failures when the file is absent or unsuitable, despite allowing a custom path via command-line argument (arg4).  
  lead: hard-coded skeleton file name "skeleton_male.json" | Default assumes male NPCs; fails if skeleton_male.json missing or unsuitable for NPC | Make skeleton path configurable or require explicit argument
- **YES** | robustness | unreal/SkyBridge/tamriel_live.py:76 | YES - Swallowing all exceptions during critical import property setup prevents debugging of failed configuration, as confirmed by the lack of logging and the presence of two explicit, non-looping calls in startup/import paths.  
  lead: Swallowing exceptions when setting import options | Makes it hard to debug import failures | except Exception:
- **YES** | correctness | start_bridge.py:29 | YES - The bridge reads 16-byte block without using the sequence number (seq) for consistency verification, risking partial updates from concurrent plugin writes.  
  lead: Shared memory atomicity risk | Bridge reads 16-byte block without ensuring atomicity, risking partial updates during plugin writes | Plugin should use sequence number to verify consistency or bridge should retry
- **YES** | performance | unreal/SkyBridge/live_bridge.py:522 | YES - The code uses `budget = 3` in `import_ready()` and processes up to 3 imports per call, which matches the review's claim of "3 per tick" potentially causing editor freezes.  
  lead: Asset import blocking editor | Imports assets without throttling beyond 3 per tick, potentially freezing editor | Limit to 2 per tick to be safer
- **YES** | performance | unreal/SkyBridge/live_bridge.py:549 | YES - The code loops over all references (nref) in `apply_world`, which is called per frame (as shown by the caller `self.apply_world(*w)` in the main update loop), resulting in O(n) processing per frame that becomes slow with high reference counts.  
  lead: O(n) reference processing each frame | The code processes all references in the stream each frame (O(n)), which can become slow with many references | Consider batching or prioritizing reference processing
- **YES** | perf | plugin/src/main.cpp:310 | YES - The initial file read in line 310 runs only once during startup (via `init = true`), causing a single stutter when the flag file triggers dumping, validating the performance finding.  
  lead: Initial reference dump file read | Reading large reference dump file during first dump causes noticeable stutter | Store seen set in binary format for faster loading
- **YES** | robustness | tools/tamriel_terrain.py:34 | YES - The hard-coded path "D:\\blender.exe" is non-portable as it assumes a Windows installation on drive D: and fails on non-Windows systems or alternative Blender paths, violating the principle of using environment variables.  
  lead: hard-coded Blender path | the path "D:\\blender.exe" is not portable and will fail on non-Windows systems or if Blender is installed elsewhere | use an environment variable or a configuration
- **YES** | robustness | unreal/SkyBridge/npc_live.py:734 | YES - The path uses a global constant (EXPORT) without configuration, preventing user modification and breaking if the directory structure changes.  
  lead: Hard-coded path `os.path.join(EXPORT, "npc_%08x.fbx" % base)` | EXPORT path is global constant; changing directory breaks bridge | Store path in config with default value for user modification
- **YES** | performance | start_bridge.py:355 | YES - The function reads the entire INI file into memory (as shown in line 355), but INI files are typically small (under 1000 lines) and the function is called only during configuration changes (not per frame or per second), making it acceptable per the review's "not problematic for current file sizes" note.  
  lead: Inefficient INI file read | `set_ini` reads entire file into memory for line-by-line processing (small files only) | Not problematic for current file sizes
- **NO** | perf | unreal/SkyBridge/land_terrain_live.py:310 | NO - The sort is performed only when spawning tiles (during initialization and per tile placement), not every frame, as confirmed by the one-time module spawn call and lack of per-frame invocation in callers.  
  lead: todo.sort(...) | Sorting entire pending tile list every frame | O(n log n) sort per frame for n pending tiles, scaling poorly with area size | Maintain a priority queue (heap) of pending tiles for efficient nearest-neighbor retrieval
- **NO** | perf | unreal/SkyBridge/live_bridge.py:748 | NO - The function uses a 2-second cache (line 744-746) so the loop isn't run every frame, only at most every 2 seconds.  
  lead: Looping over all seen IDs for interior voting | Counts votes per interior over thousands of objects every frame | O(n) per frame | Maintain incremental vote counts
- **NO** | memory | tools/land_terrain.py:464 | NO - The code's comment "# one Blender at a time, short command lines" indicates batch size is for command-line length constraints, not memory usage.  
  lead: Processing 40 files at once with Blender | Can cause memory issues as each Blender instance may use significant memory | Process files in smaller batches (e.g., 5-10 files at a time)
- **NO** | memory | unreal/SkyBridge/live_bridge.py:561 | NO - The code removes unused actors via `self.actors.pop(rid)` in lines 575-577 when `rid` is not in the current `seen` set built from incoming references.  
  lead: Actors dictionary unbounded growth | Actors dictionary grows as new references are added but old ones aren't removed | Implement removal of actors no longer present in the stream
- **NO** | memory | unreal/SkyBridge/live_bridge.py:565 | NO - The spawn queue is pruned at the end of each apply_world call (line 593) to remove entries for references no longer present in the current frame.  
  lead: Spawn queue unbounded growth | Spawn queue grows indefinitely as references are added but never removed | Add a mechanism to remove entries after processing
- **NO** | bug | tools/grass_placement.py:300 | NO - Weight w exceeding 1.0 increases probability (keeping more points), not causing omissions as claimed; floating point rounding errors would not reduce probability below 1.0 when w>1.0 for density=100%.  
  lead: Unclamped weight w causing floating point precision issues: `keep = rng.random(len(fx)) < (g["density"] / 100.0) * w` | Weight w can exceed 1.0 due to texture blending, causing floating-point rounding errors where points should be kept at 100% probability but are omitted | Clamp w = min(w, 1.0) befo
- **NO** | bug | unreal/SkyBridge/atmosphere.py:165 | NO - The error is logged to the console (via `log()`) so it's not hidden from developers, and the error handling does not prevent the user from seeing the issue.  
  lead: `except Exception as e:` hiding cloud quality setting failures | Could result in unapplied cloud quality settings with no user feedback | Remove try-except block to propagate errors
- **NO** | bug | unreal/SkyBridge/remaster_materials.py:211 | NO - Code correctly checks if texture exists before setting it (if ptex: pn.set_editor_property(...)), so missing texture is handled by not setting the property, preventing null texture assignment.  
  lead: Missing puddle noise texture not handled | Would cause material to use null texture, breaking rendering | Check texture import result before setting
- **NO** | robustness | shared/BridgeShared.h:59 | NO - 128 is sufficient as mod paths (e.g., relative to "meshes/") are typically under 70 characters (e.g., "meshes/armor/leather/leather_armor.nif" ≈ 35 chars), well below 128.  
  lead: Hard-coded max path length 128 for model paths (kModelLen) | Truncation of long mod paths may cause missing models or incorrect rendering | Increase kModelLen to 256
- **NO** | robustness | shared/BridgeShared.h:129 | NO - kGearPathLen=112 is sufficient as Skyrim armor paths rarely exceed 70 characters, and the review's assumption of frequent truncation is unfounded based on typical mod path lengths.  
  lead: Hard-coded max path length 112 for gear paths (kGearPathLen) | Truncation of long armor/weapon paths may cause missing or incorrect gear (e.g., in high-quality armor mods) | Increase kGearPathLen to 256
- **NO** | robustness | tools/offline_import.py:10 | NO - The path uses dynamic ROOT based on script location, not a hard-coded absolute path, so moving the project folder maintains relative structure.  
  lead: `PROJ = os.path.join(ROOT, "unreal", "SkyBridge", "SkyBridge.uproject")` | hard-coded path breaks if project moves | use relative paths or config
- **NO** | robustness | unreal/SkyBridge/remaster_materials.py:556 | NO - The path uses `os.path.join(AREA, ...)` with `AREA` likely set relative to the project root (not hard-coded absolute), and `lod_water()` is called only once at startup (line 810), so the issue is not a hard-coded absolute path.  
  lead: Hard-coded absolute path in lod_water import | Breaks if project directory is moved or shared | Use relative path instead of absolute
- **NO** | perf | plugin/src/main.cpp:678 | NO - The code uses s.modelIndex to cache normalized paths within the same frame, avoiding redundant processing for the same path during a single execution.  
  lead: Repeated model path normalization | Normalization done per reference without caching, causing redundant string processing | Cache normalized paths in a map
- **NO** | perf | plugin/src/main.cpp:941 | NO - The loop is bounded by SkyBridge::kMaxGear (likely 5), as checked in line 942 (g->n >= kMaxGear), preventing unbounded iteration.  
  lead: Unbounded armor addon loop: `for (auto* arma : skin->armorAddons)` | Potential O(n) processing per creature actor (1Hz) for skin addons | Limit to max 5 addons
- **NO** | perf | unreal/SkyBridge/live_bridge.py:1045 | NO - The code correctly checks file existence per frame (as part of the game loop), and file reads only occur when the file exists (not unnecessarily on every frame when absent).  
  lead: Reading exec_request.py every frame | Unnecessary disk I/O per frame | Check file existence once per frame and delete after processing
- **NO** | bug | plugin/src/main.cpp:965 | NO - The null check at line 965 (if (!eq) continue;) correctly prevents potential null pointer access and aligns with safe pointer usage practices.  
  lead: Null pointer access: `if (!eq) continue;` | Missing validation for armor addon access in shield processing | Add null check before access
- **NO** | bug | unreal/SkyBridge/live_bridge.py:212 | NO - Code explicitly returns False when water material (wmat) is missing, preventing further execution without handling the error, so the error is properly handled and the finding is incorrect.  
  lead: Water material loading failure | Fails to load water material with error but continues without handling | Add proper error handling for missing materials
- **NO** | bug | unreal/SkyBridge/live_bridge.py:492 | NO - Code marks cache as failure with self.mesh_cache[name] = False on line 493, contradicting the finding's claim of not marking cache failure.  
  lead: Incorrect mesh rendering check | Skips meshes with no render data but logs as "mesh has no render data", not handling failure properly | Log as error, skip mesh load without marking cache as failure
- **NO** | bug | unreal/SkyBridge/live_bridge.py:531 | NO - The log("imported " + name) is inside the try block, executing only after ue_assets.import_model() succeeds without exception, confirming actual import success before logging.  
  lead: Import log doesn't indicate success | Logs "imported" without confirming actual import success | Confirm import completed before logging
- **NO** | robustness | unreal/SkyBridge/remaster_materials.py:842 | NO - The script reimport_textures.py is a fixed, trusted project file located relative to the current file, so the exec poses no security risk in this context.  
  lead: Dangerous exec of local script | `exec(open(...).read(), ...)` poses security risk | Replace with direct module import
- **NO** | cleanup | tools/npc_batch.py:37 | NO - Line 37 is necessary to initialize `creature` as an empty dictionary when the gear mapping (gh) is not found, preventing a NameError when accessed later (line 54), and is not redundant because it handles a separate code path.  
  lead: Redundant 'creature = {}' after line 25 | Duplicate assignment with no effect | Remove line 37
- **NO** | correctness | play.py:9 | NO - The hard-coded path is defined on line 9 but never referenced in the provided code snippet, making the finding incorrect as the code does not use this path.  
  lead: Hard-coded Unreal Editor path | Fails if Unreal Editor not at exact path D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe | Use config file or environment variable
- **NO** | correctness | play.py:12 | NO - The variable PLUGINS is defined but never referenced in the provided code (lines 1-42), so the hard-coded path does not affect runtime behavior or cause failures when Skyrim's install location changes.  
  lead: Hard-coded SKSE plugins path | Fails if Skyrim install location differs from D:\SteamLibrary\steamapps\common\Skyrim Special Edition\ | Use config file or environment variable
- **NO** | robustness | unreal/SkyBridge/live_bridge.py:208 | NO - The code checks if water_wide.csv exists at line 211 and returns False if missing, preventing crashes; it's not called frequently (only once during setup as shown in callers).  
  lead: Missing water data file | Code doesn't handle missing water_wide.csv file gracefully, potentially causing crashes | Add null check and fallback to alternative water rendering
- **NO** | robustness | unreal/SkyBridge/live_bridge.py:514 | NO - The code checks file existence at line 515 (os.path.exists(p)) and returns early, preventing any exception when ready.txt is missing.  
  lead: Missing ready.txt file | The import_ready method assumes ready.txt exists, causing exception if file is missing | Check file existence before reading
- **NO** | performance | start_bridge.py:168 | NO - The 0.3s sleep is in a per-command execution loop with a timeout (not per-frame), making it acceptable for infrequent command processing rather than continuous polling.  
  lead: Busy-wait in UE execution | 0.3-second sleep in `_ue_exec_locked` loop is inefficient for file check | Use event-based waiting (e.g., `wait_for_file_change`)
- **?** | perf | tools/land_textures.py:362 | not verified yet  
  lead: Cache size too small (24 entries) | Causes repeated processing of same layer data for different cell resolutions | Increase cache size or use LRU cache

Verified: 87 of 89 leads; YES: 61, UNSURE: 0, NO: 26
