# Pipeline Map

1. Static world model conversion nif -> obj -> fbx -> Unreal
   tools/bsa.py (BSA extraction) -> tools/nif2obj.py (NIF to OBJ conversion) -> tools/textures.py + tools/blender_export.py (Texture patching and FBX export) -> unreal/SkyBridge/import_area.py (FBX import)

2. Textures dds -> png -> material instance
   tools/textures.py (DDS to PNG conversion) -> unreal/SkyBridge/apply_textures.py (Material instance creation)

3. NPC and creature building
   tools/npc_build.py (NPC FBX generation) -> tools/npc_batch.py (Batch NPC build) -> live_bridge.py (NPC pose streaming)

4. Live streaming (plugin -> shared memory -> live_bridge)
   plugin/main.cpp (SKSE plugin streams to Local\SkyrimUnrealBridge_v1) -> live_bridge.py (reads shared memory data)

5. Terrain and water
   tools/esm_land.py (WhiterunWorld heightmap) -> tools/lod_terrain.py (Terrain LOD conversion) -> tools/distant_world.py (Worldspace references dump) -> unreal/SkyBridge/import_terrain.py (Terrain import)

6. Launch and shutdown
   start_bridge.py (Starts Skyrim + Unreal) -> tools/overlay.ps1 (Makes Unreal window overlay Skyrim)
