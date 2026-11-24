# Glossary

## Technical Terms

**SKSE plugin** - A mod for Skyrim that streams game data to shared memory. The SkyrimUnrealBridge plugin (SkyrimUnrealBridge.dll) handles position, camera, and game data streaming via Windows shared memory (`Local\SkyrimUnrealBridge_v1`), verified to work with Skyrim 1.6.1170.

**Shared memory** - A Windows IPC mechanism used for communication between Skyrim and Unreal Engine. The plugin writes data to `Local\SkyrimUnrealBridge_v1` and Unreal reads it every tick, allowing camera motion mirroring between the two applications.

**Whiterun** - The main town in Skyrim being reconstructed. The project has exported 8 buildings (Bannered Mare, Breezehome, etc.) from Skyrim's BSA files, converted to FBX/GLB, and imported into Unreal as static meshes.

**ESM** - Elder Scrolls Mesh files (Skyrim.esm) that contain the game's base data. The project uses these files to extract references for building a detailed reconstruction of Whiterun and other locations.

**BSA** - Bethesda Software Archive (file format). The project extracts NIF models from Skyrim's Meshes0.bsa using tools like `bsa.py`, then processes them into OBJ files with `nif2obj.py`.

**NIF** - Bethesda's 3D model file format (NiForm). Skyrim uses NIF for most meshes, which are converted to OBJ using `nif2obj.py` as part of the mesh pipeline.

**OBJ** - Wavefront 3D model format. The project converts NIFs to OBJ for processing, using tools like `nif2obj.py` before further conversion to FBX.

**FBX** - Autodesk's 3D model format. The final mesh format exported to Unreal Engine (via `blender_export.py`), with materials assigned based on Skyrim's textures.

**GLB** - GL Transmission Format (binary format for 3D assets). Used in the mesh pipeline to store FBX assets in a more compact binary form for processing.

**UV mapping** - The process of applying 2D textures to 3D models. The project maps Skyrim's diffuse textures to the exported models with UV coordinates preserved during the conversion pipeline.

**Nanite** - Unreal Engine's virtualized geometry system. The project enables Nanite for terrain and meshes, though it requires special handling (Nanite rejects certain materials like Single Layer Water).

**Lumen** - Unreal Engine's real-time global illumination and reflection system. The project uses Lumen with ray reconstruction (DLSS Ray Reconstruction) for better reflections on wet ground surfaces.

**HISM** - Hybrid Instanced Static Meshes (Unreal Engine's instancing system). The project uses HISM for rendering large numbers of similar objects efficiently.

**LOD (Level of Detail)** - A technique for optimizing 3D rendering by using simpler versions of models at greater distances. The project processes distant world terrain and trees using LOD, with terrain converted from Skyrim's `.btr` files.

**SkyAtmosphere** - Unreal Engine's system for rendering realistic skies. The project adjusts it to match Skyrim's sea level (`SEA_LEVEL`) and adjusts parameters for cloud coverage and density.

**Volumetric cloud** - Cloud rendering with depth, not just a texture. The project uses Unreal's volumetric cloud system (with proper `Cloud_GlobalCoverage` and `Cloud_GlobalDensity` scaling) to render Skyrim-style weather.

**FaceGen** - Skyrim's system for generating NPC faces. The project handles FaceGen for NPCs, though the documentation notes that facial animation (expression/morph weights) remains a future task.

**Bind pose** - The default, unanimated pose of a 3D model. The project uses this as a reference point for animating NPCs, where streamed bone transforms are compared against the bind pose.

**Bone-name mangling** - A technique used to handle differences in bone naming conventions between Skyrim's NIF and Unreal Engine. The project uses specific naming patterns to match skeleton bones.

**Offline import** - A batch processing method to import 3D models, as opposed to live streaming. The project has an offline import pipeline using `import_area.py` and `import_terrain.py` to process meshes from `area2/`.

**Shared mapping** - A technique for maintaining consistent references between Skyrim's game data and Unreal Engine's representation of that data. The project uses this for city layer placement where streamed references win over ESM references.

**Add-on layer** - Content added by mods. The project uses `area2/` to track content from mods (vs `whiterun/` which only contains base game content), ensuring modded content is displayed correctly.

**Memory governor** - A system controlling memory usage for the engine. The project sets texture streaming pool to 5000 MB (later reduced to 3000 MB) to balance between Skyrim and Unreal's memory requirements.

**WRef** - Likely "World Reference" (used internally by the plugin to track object references). The plugin uses these to stream object data between Skyrim and Unreal.

**Remaster view** - A mode activated with `--remaster` that shows only Unreal's viewport fullscreen over Skyrim (Skyrim keeps keyboard/mouse focus). The project's documentation mentions this was implemented to address UI and HUD rendering issues.

**Seqlock** - A synchronization technique using sequence numbers (odd values indicate writing). The plugin uses seqlock for shared memory writes in its communication system.

**Overlay mode** - A mode where Unreal's viewport is placed exactly over Skyrim's window, with transparency. The project uses `tools/overlay.ps1` to set up a borderless, click-through window that overlaps Skyrim.

**Plugin DLL** - The SKSE plugin DLL (SkyrimUnrealBridge.dll) that handles communication between Skyrim and Unreal. Only Claude Code builds and installs this DLL.

**C++ module** - A component of the Unreal Engine project written in C++ (e.g., `SkyBridgeViewLibrary`). The project uses C++ for specific functionality like applying NPC poses to skeletal meshes.

**Python struct** - A data structure defined in Python for parsing and processing data. The project uses Python structs (e.g., `"<Hh3f4f"`) to handle bone data efficiently.

**Worldspace** - In Skyrim, a section of the world (e.g., WhiterunWorld). The project reconstructs worldspaces like WhiterunWorld from Skyrim's data files.

**Form ID** - A unique identifier for game objects in Skyrim (e.g., `000C430A` for a blacksmith forge). The plugin uses these IDs to track objects between Skyrim and Unreal.

**HUD** - Heads-up display elements. The project adds a Skyrim-style HUD (compass, bars, crosshair) above the Unreal viewport in remaster view.

**Decal** - A texture applied to a surface (e.g., moss on walls). The project handles Skyrim's decals using `IsDecal` switch to remap alpha (0.45-0.9) and dither textures.

**PBR (Physically Based Rendering)** - A rendering technique for materials that simulate real-world lighting. The project uses PBR for materials with normal maps, though the converter sometimes misses diffuse maps.

**Specular** - A property of materials that affects how light reflects. The project handles specular maps for Skyrim's materials, though it notes some meshes were missing normal/PBR maps.

**Normals** - Vector data used for lighting calculations in 3D rendering. The project processes normal maps for Skyrim's meshes to achieve better material representation.

**Vertex alpha** - Alpha channel data stored with vertices (Skyrim uses this for fading decal edges). The converter drops vertex alpha, which the project compensates for with a material remap.

**NPC** - Non-player character. The project implements a streaming system for NPC poses (30 Hz bone transforms) and handles texture name collisions to display correct clothing.

**Distant world** - A system that processes distant objects (mountains, trees) from Skyrim's data. The project uses `distant_world.py` to extract these references for rendering up to 6 km away.

**Washed-out fix** - A rendering adjustment to fix a fog problem where everything was inside dense fog. The project now follows camera height with falloff 0.2 and lower densities.

**Puddle noise** - A texture used to simulate puddles on surfaces. The project uses `tools/puddle_noise.py` to create a noise texture for wet surfaces with mirror roughness.

**Rain curtains** - An effect simulating rain as moving particles. The project implements `M_RainDrops` with 12,000 GPU-animated streaks around the camera.

**HISM** - Hybrid Instanced Static Meshes (used in the Unreal Engine for rendering multiple copies of objects efficiently). The project uses HISM for distant objects like trees and rocks.

**Interiors** - Skyrim's indoor locations. The project processes interiors from Skyrim's data files and places them in Unreal (e.g., `area2/interiors_whiterun.json` contains 27 interior cells).

**City layer** - A system that places buildings in Unreal using streamed references from Skyrim rather than ESM references. The project's city layer now skips pieces the large-ref preview already placed.

**Debug grid** - A grid used for visual debugging. The project's documentation mentions a debug grid in the sky is off (`bDrawDebugGrid` in `SkyBridgeGameMode.cpp`).
