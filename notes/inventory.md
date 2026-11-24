# SkyrimUnrealBridge Project Inventory

## Root Files
.cursorrules - Cursor configuration settings
.gitignore - Git ignore patterns
AGENTS.md - Agent coordination instructions
CMakeLists.txt - CMake build configuration file
COORDINATION.md - Project coordination guidelines
Codex.bat - Codex executable launcher
Codex_Local.bat - Local Codex executable launcher
GRUNT_TASKS_FOR_LOCAL_MODEL.md - Local model grunt task definitions
HANDOFF_FOR_CHATGPT.md - Handoff instructions for ChatGPT agent
HANDOFF_FOR_CURSOR.md - Handoff instructions for cursor agent
Import_Assets_Offline.bat - Offline asset import utility
Launch_Demo.bat - Demo launch script
Play.bat - Gameplay execution script
README.md - Project overview documentation
Stop.bat - Process termination script
vcpkg.json - vcpkg dependency manager configuration

## area2/
area2/apply_dt.py - Applies data transformation pipelines
area2/cap.py - Captures scene data for analysis
area2/cap_root.py - Root-level capture processing
area2/cap_walkers.py - Walker capture operations
area2/check_npc_mod.py - Checks NPC modification status
area2/fix_audit.py - Fixes audit issues in assets
area2/fix_audit2.py - Fixes second-generation audit issues
area2/fix_detail.py - Fixes texture detail issues
area2/fix_dup.py - Fixes duplicate asset issues
area2/fix_interior.py - Fixes interior space issues
area2/fix_interior2.py - Fixes second-generation interior issues
area2/fix_night.py - Fixes night mode issues
area2/fix_npc_mats.py - Fixes NPC material assignments
area2/fix_prefetch.py - Fixes texture prefetch behavior
area2/fix_trees.py - Fixes tree rendering issues
area2/fix_water_nanite.py - Fixes water nanite rendering
area2/fix_wet.py - Fixes wet surface rendering
area2/gpu_prof.py - GPU performance profiling
area2/hot_atmos.py - Hotpath atmosphere analysis
area2/hot_memgov.py - Memory governor hotpath analysis
area2/list_windows.py - Lists rendering windows
area2/memgov_dry.py - Dry memory governor analysis
area2/memrep.py - Memory representation analysis
area2/night_test.py - Night lighting test
area2/npc_capture.py - NPC capture operations
area2/npc_live_before_cursor.py - NPC state before cursor
area2/npc_live_before_cursor_frozen.py - Frozen NPC state before cursor
area2/patch_rain_occ.py - Rain occlusion patching
area2/preview_sky.py - Sky preview generation
area2/probe.py - General probing operations
area2/probe_arms.py - Arm probing operations
area2/probe_arms2.py - Second-generation arm probing
area2/probe_arms3.py - Third-generation arm probing
area2/probe_arms4.py - Fourth-generation arm probing
area2/probe_arms5.py - Fifth-generation arm probing
area2/probe_arms6.py - Sixth-generation arm probing
area2/probe_bake.py - Baking probe data
area2/probe_bounds.py - Bounds probing operations
area2/probe_btr.py - BTR (bounding triangle) probing
area2/probe_caps.py - Capsule probing
area2/probe_cmp.py - Comparison probing
area2/probe_dup.py - Duplicate probing
area2/probe_fog.py - Fog effect probing
area2/probe_gpu.py - GPU resource probing
area2/probe_ground.py - Ground probing
area2/probe_hist.py - Probe history analysis
area2/probe_light_props.py - Light properties probing
area2/probe_limbs_live.py - Live limb probing
area2/probe_lod.py - Level-of-detail probing
area2/probe_np.py - NPC probe operations
area2/probe_npc.py - NPC data probing
area2/probe_npc2.py - Second NPC data probe
area2/probe_npc3.py - Third NPC data probe
area2/probe_npc_mats.py - NPC material probing
area2/probe_perf.py - Performance probing
area2/probe_pf.py - Probe flow analysis
area2/probe_plan.py - Probe planning operations
area2/probe_player.py - Player probe operations
area2/probe_pose_cost.py - Pose cost analysis
area2/probe_pose_rate.py - Pose rate analysis
area2/probe_rain_mine.py - Rain mining operations
area2/probe_refresh.py - Refresh probe operations
area2/probe_refresh2.py - Second refresh probe
area2/probe_render2.py - Second rendering probe
area2/probe_render_pose.py - Render pose analysis
area2/probe_rot.py - Rotation probing
area2/probe_scale.py - Scale probing
area2/probe_sky.py - Sky probe operations
area2/probe_smooth.py - Smoothing analysis
area2/probe_sp.py - Spatial probing
area2/probe_state.py - State probing
area2/probe_stream_limbs.py - Streamed limbs probing
area2/probe_tex.py - Texture probing
area2/probe_vis.py - Visibility probing
area2/probe_water_nanite.py - Water nanite probing
area2/prof_apply.py - Profiler data application
area2/prof_npc.py - NPC profiling
area2/prof_npc2.py - Second NPC profiling
area2/quit_editor.py - Unloads editor
area2/reload_npc_keep.py - Reloads NPC with state
area2/sbperf_cprof.py - SkyBridge performance with cprof
area2/sbperf_csv.py - SkyBridge performance CSV
area2/sbperf_long.py - Long-term performance metrics
area2/sbperf_read.py - SkyBridge performance reading
area2/sbperf_start.py - SkyBridge performance start
area2/sky_capture.py - Sky capture operations
area2/swap_npc.py - NPC swapping operations
area2/swap_reset.py - NPC swap reset
area2/tam_test1.py - Tamriel test 1
area2/test_interior.py - Interior test
area2/test_npc_frozen.py - Frozen NPC test
area2/test_npc_math.py - NPC math test
area2/test_refpose.py - Reference pose test
area2/test_spaced_names.py - Spaced name test
area2/undo_rain_mine.py - Undoes rain mining
demo.py - Demo script
play.py - Gameplay play script

## tools/
tools/asset_service.py - Handles asset service operations
tools/auto_build.py - Auto-build processing
tools/blender_export.py - Blender export functions
tools/blender_preview.py - Blender preview generation
tools/bsa.py - BSA (Bethesda Archive) processing
tools/build_area.py - Area build processing
tools/capture_window.py - Window capture functions
tools/check_rotation.py - Rotation validation
tools/check_tex_keys.py - Texture key validation
tools/compare_refs.py - Reference comparison
tools/debug/README.md - Debug tools documentation
tools/debug/npc_api.py - NPC API debugging
tools/debug/npc_creature_diag.py - NPC creature diagnostics
tools/debug/npc_creature_test.py - NPC creature testing
tools/debug/npc_diag.py - NPC diagnostics
tools/debug/npc_diag2.py - Second NPC diagnostics
tools/debug/npc_diag3.py - Third NPC diagnostics
tools/debug/npc_dump_rest.py - NPC REST dump
tools/debug/npc_names.py - NPC name processing
tools/debug/npc_probe.py - NPC probe functions
tools/debug/npc_reload.py - NPC reloading
tools/debug/npc_try.py - NPC try operations
tools/debug/npc_view.py - NPC viewing functions
tools/debug/npc_view2.py - Second NPC viewing
tools/debug/npc_view3.py - Third NPC viewing
tools/debug/npc_view_cow.py - NPC view (cow mode)
tools/debug/walk_check.py - Walk check operations
tools/debug/walk_check_lib.py - Walk check library
tools/debug/walk_watch.py - Walk monitoring
tools/debug/water_diag.py - Water diagnostics
tools/debug/water_fix.py - Water issue fixing
tools/debug/water_recompile.py - Water recompiling
tools/debug/water_view.py - Water viewing
tools/derive_spec.py - Specification derivation
tools/detail_noise.py - Detail noise generation
tools/distant_world.py - Distant world processing
tools/editor_watchdog.py - Editor watchdog
tools/esm_area.py - ESM (Elder Scrolls Mesh) area processing
tools/esm_land.py - ESM land processing
tools/esm_land_tex.py - ESM land texture processing
tools/esm_persistence.py - ESM persistence
tools/esm_refs.py - ESM reference processing
tools/esm_water.py - ESM water processing
tools/fill_textures.py - Texture filling
tools/find_decals.py - Decal finding
tools/find_lod.py - LOD (Level of Detail) finding
tools/find_overrides.py - Override finding
tools/find_tex.py - Texture finding
tools/gpu_profile.py - GPU profiling
tools/grass_blender.py - Grass in Blender
tools/grass_placement.py - Grass placement
tools/grass_world.py - Grass world processing
tools/land_terrain.py - Land terrain processing
tools/land_textures.py - Land textures
tools/land_textures_blender.py - Land textures in Blender
tools/large_refs_preview.py - Large references preview
tools/lod_horizon_preview.py - LOD horizon preview
tools/lod_objects.py - LOD objects
tools/lod_terrain.py - LOD terrain
tools/merge_area.py - Area merging
tools/mesh_index.py - Mesh indexing
tools/nif2obj.py - NIF to OBJ conversion
tools/npc_autobuild.py - NPC auto-build
tools/npc_batch.py - NPC batch processing
tools/npc_blender.py - NPC in Blender
tools/npc_build.py - NPC building
tools/npc_build_creature.py - NPC creature building
tools/npc_extract.py - NPC extraction
tools/npc_hair_tint.py - NPC hair tinting
tools/npc_preview.py - NPC preview
tools/npc_skin.py - NPC skinning
tools/npc_tex_alias.py - NPC texture aliasing
tools/offline_import.py - Offline import
tools/overlay.ps1 - PowerShell overlay
tools/perf_gpu_share.py - GPU sharing for performance
tools/projected_snow.py - Projected snow
tools/puddle_noise.py - Puddle noise
tools/queue_large_refs.py - Queue large references
tools/read_actors.py - Actor reading
tools/read_bridge.py - Bridge reading
tools/read_gear.py - Gear reading
tools/read_world.py - World reading
tools/shutdown_after_import.py - Shutdown after import
tools/skyrim_lightweight.py - Skyrim lightweight processing
tools/skyrim_plugins.py - Skyrim plugins
tools/stream_coverage.py - Stream coverage
tools/tamriel_terrain.py - Tamriel terrain
tools/tamriel_world.py - Tamriel world
tools/textures.py - Texture processing
tools/textures_pbr.py - PBR textures
tools/truth_to_area.py - Truth to area conversion
tools/ue_run.py - Unreal Engine runner
tools/upscale_textures.py - Texture upscaling
tools/verify_models.py - Model verification
tools/verify_unreal.py - Unreal verification
tools/water_flow.py - Water flow
tools/water_flow_run.py - Water flow runner
tools/weatherfx_build.py - Weather effects build
tools/weatherfx_check.py - Weather effects check
tools/weatherfx_splash.py - Weather effects splash
tools/weatherfx_test.py - Weather effects test

## unreal/SkyBridge/
unreal/SkyBridge/Config/DefaultEditorSettings.ini - Editor configuration
unreal/SkyBridge/Config/DefaultEngine.ini - Engine configuration
unreal/SkyBridge/Config/DefaultEngine.ini.bak_predlss - Pre-DLSS backup
unreal/SkyBridge/Config/DefaultEngine.ini.bak_prephoto - Pre-photo backup
unreal/SkyBridge/Config/DefaultInput.ini - Input configuration
unreal/SkyBridge/Content/Python/init_unreal.py - Unreal Python initialization
unreal/SkyBridge/SkyBridge.uproject - Unreal project file
unreal/SkyBridge/SkyBridge.uproject.bak_predlss - Pre-DLSS project backup
unreal/SkyBridge/Source/SkyBridge.Target.cs - SkyBridge target configuration
unreal/SkyBridge/Source/SkyBridge/SkyBridge.Build.cs - Build configuration
unreal/SkyBridge/Source/SkyBridge/SkyBridge.cpp - Main implementation
unreal/SkyBridge/Source/SkyBridge/SkyBridgeGameMode.cpp - Game mode implementation
unreal/SkyBridge/Source/SkyBridge/SkyBridgeGameMode.h - Game mode header
unreal/SkyBridge/Source/SkyBridge/SkyBridgeViewLibrary.cpp - View library implementation
unreal/SkyBridge/Source/SkyBridge/SkyBridgeViewLibrary.h - View library header
unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.cpp - Skyrim camera implementation
unreal/SkyBridge/Source/SkyBridge/SkyrimCameraActor.h - Skyrim camera header
unreal/SkyBridge/Source/SkyBridgeEditor.Target.cs - Editor target configuration
unreal/SkyBridge/apply_textures.py - Texture application
unreal/SkyBridge/atmosphere.py - Atmosphere handling
unreal/SkyBridge/audit_slots.py - Slot auditing
unreal/SkyBridge/fix_slots.py - Slot fixing
unreal/SkyBridge/grass_live.py - Live grass processing
unreal/SkyBridge/import_area.py - Area import
unreal/SkyBridge/import_area2.py - Second area import
unreal/SkyBridge/import_terrain.py - Terrain import
unreal/SkyBridge/import_terrain2.py - Second terrain import
unreal/SkyBridge/import_terrain3.py - Third terrain import
unreal/SkyBridge/import_whiterun.py - Whiterun import
unreal/SkyBridge/land_terrain_live.py - Live land terrain
unreal/SkyBridge/live_bridge.py - Live bridge
unreal/SkyBridge/memory_governor.py - Memory governance
unreal/SkyBridge/npc_live.py - Live NPC handling
unreal/SkyBridge/offline_import.py - Offline import
unreal/SkyBridge/probe_bounds.py - Bounds probing
unreal/SkyBridge/reimport_textures.py - Reimport textures
unreal/SkyBridge/remaster_materials.py - Remastered materials
unreal/SkyBridge/tamriel_live.py - Live Tamriel processing
unreal/SkyBridge/ue_assets.py - Unreal assets handling
unreal/SkyBridge/upgrade_materials.py - Material upgrading
unreal/SkyBridge/water_flow_apply.py - Water flow application
unreal/SkyBridge/water_setup.py - Water setup
unreal/SkyBridge/weather_fx.py - Weather effects

## plugin/
plugin/src/PCH.h - Precompiled header
plugin/src/main.cpp - Main plugin implementation

## shared/
shared/BridgeShared.h - Bridge shared data header

## Other
ue_search.txt - Unreal Engine search index
