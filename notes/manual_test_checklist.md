# Manual Test Checklist for Skyrim Unreal Bridge

1. Move Skyrim camera | Unreal viewport camera follows movement | SkyrimCameraActor.cpp
2. View Whiterun buildings | 8 specific buildings (Bannered Mare, Breezehome, Blacksmith, house02, guardhouse, castle tower, bridge, castle main building) visible at real Skyrim positions | SkyrimCameraActor.cpp
3. Change weather to rain | Rain streaks visible in viewport and surfaces wet | SkyBridgeViewLibrary.cpp
4. View White River south of Whiterun | Water visible in river channel (shallow water) | tools/lod_terrain.py
5. Open Skyrim menu (inventory) | Skyrim menu appears without Unreal overlay | remaster_watch.py
6. Check system memory usage | Texture streaming pool set to 3000 MB (configurable) during operation | DefaultEngine.ini
7. Check editor windows | Only one Unreal editor window visible (no duplicates) | init_unreal.py
8. View NPCs | NPCs in correct poses (not A-pose) | npc_live.py
9. Wait for night | Night sky with stars/auroras visible in clear northern weather | remaster_materials.py
10. After rain, view walls | Walls show wet appearance | remaster_materials.py
11. View distant trees | Trees drawn up to 1.6 km distance (distant layer) | distant_world.py
12. View mountains | Mountains with snow on upward faces (not flat) | remaster_materials.py
13. View clear weather sky | Clouds with broken coverage (not flat overcast) | remaster_materials.py
14. View canal water | Water flows with normal maps (not solid slab) | M_SkyWater
15. View White River | Water visible in river channel (not empty) | tools/lod_terrain.py
16. Enter Bannered Mare interior | Interior rendered with correct structures (except known missing objects) | distant_world.py
17. Look for debug grid | No grid lines visible (disabled via bDrawDebugGrid in SkyBridgeGameMode.cpp) | SkyBridgeGameMode.cpp
18. Check Unreal window | Borderless, click-through, ~50% transparent over Skyrim | tools/overlay.ps1
19. Verify remaster view | Editor fullscreen over Skyrim, Skyrim maintains keyboard/mouse focus | SkyBridgeViewLibrary.cpp
20. After rain, view ground | Puddles visible with wetness and rain ripples | tools/puddle_noise.py
21. Check frame rate | Editor runs at 60 FPS consistently | DefaultEngine.ini
22. Test camera movement | Input latency below 50 ms (measured as 45 ms) | DefaultEngine.ini
23. Rain weather | Rain curtains follow camera, sun dimmed appropriately | SkyBridgeViewLibrary.cpp
24. View fog | Fog density and color match Skyrim's weather data | remaster_materials.py
25. View NPC skin | Skin uses Subsurface Profile shading (no flat rendering) | npc_tex_alias.py
26. View NPC hair/eyes | Hair and eyes have correct textures (no overwriting) | npc_tex_alias.py
27. Check sun at noon | Sun at highest point with correct lighting | remaster_materials.py
28. View activation prompt | "E Talk" prompt visible over game (not hidden) | remaster_watch.py
29. Verify texture memory | Texture streaming pool set to 3000 MB (configurable) | DefaultEngine.ini
