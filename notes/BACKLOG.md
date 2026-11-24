# BACKLOG.md

1. Ground/roads texture detail
files: unreal/SkyBridge/land_terrain_live.py, area2/landterrain/tex/, unreal/SkyBridge/{land_terrain_live,tamriel_live}.py
do: Complete land_terrain_live.py implementation, fix missing material compilation, ensure all terrain textures load from area2/landterrain/tex/
verify: Run tools/healthcheck.py, observe road/terrain detail in game, check for grey checkerboard using tools/debug/probe_ground.py

2. Flame placement height and coals
files: unreal/SkyBridge/fire_fx.py
do: Lower flame position by 30 cm, add coals to braziers in fire_fx.py
verify: Run tools/ue_run.py fire_fx.py, check flame position with tools/debug/npc_view_cow.py, verify coals visible

3. Editor memory growth
files: unreal/SkyBridge/memory_governor.py, unreal/SkyBridge/live_bridge.py, area2/prefetch_on.txt
do: Implement more aggressive memory monitoring and cleanup in memory_governor.py, fix prefetch management
verify: Run tools/memrep.py, monitor memory growth rate (< 100 MB/min) with tools/healthcheck.py

4. Mountain haze culling
files: unreal/SkyBridge/mountain_mist.py
do: Implement culling of far geometry behind mountain haze
verify: Run tools/gpu_profile.py, measure GPU load reduction, check performance with tools/perf_profile.py

5. NPC weapon visibility
files: unreal/SkyBridge/npc_live.py, area2/fix_npc_mats.py
do: Fix material slot assignment for weapon meshes in npc_live.py
verify: Run tools/ue_run.py npc_live.py, check weapon visibility with tools/debug/npc_diag.py

6. Night torches height adjustment
files: unreal/SkyBridge/weather_fx.py
do: Lower light positions by 1 meter in weather_fx.py
verify: Run tools/ue_run.py weather_fx.py, check light position with tools/debug/probe_ground.py

7. Night torches coals
files: unreal/SkyBridge/fire_fx.py
do: Add coals to brazier bowls, adjust lighting to match real-world behavior
verify: Run tools/ue_run.py fire_fx.py, check coals visible in close-up shots

8. Sun color validation
files: tools/showcase_shot.py, tools/photo_keys.py
do: Validate and update sun color values based on real-world references
verify: Run tools/showcase_shot.py --night, compare with reference images

9. DLSS integration
files: unreal/SkyBridge/*.py
do: Integrate NVIDIA's official DLSS 5 plugin into Unreal project
verify: Run tools/max_quality.py, check "DLSS Enabled" in Unreal Engine console

10. Grass placement optimization
files: unreal/SkyBridge/grass_live.py, tools/grass_placement.py
do: Optimize grass density calculation and culling
verify: Run tools/grass_placement.py, check performance with tools/perf_profile.py

11. NPC pose synchronization
files: unreal/SkyBridge/npc_live.py
do: Fix pose synchronization by comparing with reference data
verify: Run tools/probe_pose_rate.py, measure pose transition rates

12. Terrain LOD seam fixes
files: tools/land_terrain.py, tools/land_textures.py
do: Improve terrain LOD seam handling in terrain processing
verify: Run tools/lod_horizon_preview.py, check horizon seams

13. Water Nanite compatibility
files: unreal/SkyBridge/fire_fx.py, tools/fix_water_nanite.py
do: Fix water material Nanite compatibility in all water assets
verify: Run tools/fix_water_nanite.py, check for Nanite rendering in tools/probe_water_nanite.py

14. NPC memory footprint
files: unreal/SkyBridge/npc_live.py
do: Implement better NPC memory management
verify: Run tools/memrep.py, measure NPC memory usage per 10 NPCs

15. Lighting scatter reduction
files: unreal/SkyBridge/atmosphere.py
do: Decrease light scattering to prevent washed-out appearance
verify: Run tools/max_quality.py, compare with tools/showcase_shot.py

16. City prefetched data optimization
files: unreal/SkyBridge/live_bridge.py
do: Improve city prefetched data management
verify: Run tools/probe_prefetch.py, check prefetch queue status

17. Dynamic weather transitions
files: unreal/SkyBridge/weather_fx.py
do: Implement smoother weather transitions
verify: Run tools/ue_run.py weather_fx.py, observe weather changes

18. Bone container crash fix
files: unreal/SkyBridge/npc_live.py
do: Add skeleton check before assigning to PoseableMeshComponent
verify: Run tools/debug/npc_reload.py, test long session with tools/healthcheck.py

19. Material parameter names
files: tools/fix_detail.py
do: Fix material parameter naming for better debugging
verify: Run tools/fix_detail.py, check parameter names in tools/debug/npc_diag.py

20. Terrain texture baking
files: tools/land_textures.py
do: Complete terrain texture baking pipeline
verify: Run tools/land_textures.py, check area2/landterrain/tex/ content

21. Rain effect visibility
files: unreal/SkyBridge/weather_fx.py
do: Adjust rain particle density and visibility settings
verify: Run tools/ue_run.py weather_fx.py, check rain visibility

22. Water flow visualization
files: tools/debug/water_view.py
do: Implement proper water flow visualization
verify: Run tools/debug/water_view.py, check river flow visualization

23. NPC animation smoothness
files: unreal/SkyBridge/npc_live.py
do: Improve NPC animation transition smoothness
verify: Run tools/probe_smooth.py, measure animation smoothness

24. Texture resolution for close-ups
files: tools/detail_noise.py
do: Add texture resolution improvements for close-up materials
verify: Run tools/detail_noise.py, check detail texture quality

25. Sky color realism
files: tools/sky_extras.py
do: Implement more accurate sky color based on elevation
verify: Run tools/sky_extras.py --night, observe sky color changes
