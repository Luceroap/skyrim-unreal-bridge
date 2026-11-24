# Handoff: Skyrim SE -> Unreal Engine 5.8 live bridge ("Skyrim remaster")

Read this first, then README.md. Project root: `C:\Users\Aidan\SkyrimUnrealBridge`.

## The idea
The owner wants to build their own Skyrim remaster in Unreal Engine 5 (like Oblivion Remastered) that looks better than
their heavily modded Skyrim. A running Skyrim SE (1.6.1170, SKSE 2.2.6, game at
`D:\SteamLibrary\steamapps\common\Skyrim Special Edition`) streams live data to Unreal, and Unreal re-renders the world
with Lumen, Nanite, PBR materials, a real sun/sky and water. Skyrim stays the "brain" (position, camera, time, weather,
which objects/lights are loaded); Unreal is the renderer.

## Architecture (all working)
- `plugin/` SKSE plugin (C++, CommonLibSSE-NG). Writes two Windows shared-memory blocks:
  - `Local\SkyrimUnrealBridge_v1`: camera/player/time/weather packet.
  - `Local\SkyrimUnrealBridge_world_v1`: world stream (refs, model names, lights), seqlock. Layout in `shared/BridgeShared.h`.
- `unreal/SkyBridge/live_bridge.py`: runs inside the Unreal editor. Reads both blocks (ctypes), mirrors the camera,
  builds sun/sky/fog/exposure, spawns a StaticMeshActor per Skyrim reference, point lights, terrain and water.
- `unreal/SkyBridge/Content/Python/init_unreal.py`: starts live_bridge ~240 ticks after the editor is up.
- `unreal/SkyBridge/ue_assets.py`: imports a converted FBX and builds PBR materials from textures.
- `tools/asset_service.py`: background converter. The editor writes needed model names to `area2/requests.txt`;
  the service converts NIF -> OBJ -> FBX (+DDS -> PNG textures) and lists finished names in `area2/ready.txt`.
- Rotation/position conversion is validated: Skyrim->UE position (y,x,z)*1.4287; orientation in `ue_rotation()`.
- One-click launcher: `demo.py` (desktop shortcut "Skyrim Unreal Demo", also `Launch_Demo.bat`). Starts the converter,
  Skyrim (via `start_bridge.py --no-overlay --skyrim-only`), then the Unreal editor.

## What was just fixed
- Editor kept quitting by itself (`Cmd: QUIT_EDITOR` in `unreal/SkyBridge/Saved/Logs/SkyBridge.log`). Cause was the
  `-ExecutePythonScript=` command-line flag (plain editor stays up). Now launched without it; `init_unreal.py` starts the
  bridge instead. Verified: stays up, 1386 actors + 93 lights spawned.
- Launcher showed a blue screen because `start_bridge.py` also started an old game-mode Unreal build. Added `--skyrim-only`.
- Skyrim froze when Unreal had focus. Set `bAlwaysActive=1` in
  `C:\Users\Aidan\OneDrive\Documents\My Games\Skyrim Special Edition\SkyrimPrefs.ini` (backup in `C:\Users\Aidan\SkyrimBackups`).

- Terrain was standing on its side and the sun/moon pointed the wrong way: `unreal.Rotator(a, b, c)` in Python is
  **(roll, pitch, yaw)**, not (pitch, yaw, roll). `live_bridge.py` now uses keyword args (`Rotator(yaw=90)` etc.).
  Always use keywords. Verified: terrain lies under the objects, sun low in the east at dawn, camera matches Skyrim's view.
- "Can't see the demo": the editor window sat behind fullscreen Skyrim / on the left monitor, and its viewport stopped
  rendering in the background. Now:
  - **Remaster view** (`start_bridge.py --remaster`, run automatically at the end of `demo.py`; undo `--remaster-off`):
    the editor goes windowed-fullscreen on Skyrim's monitor with an immersive, toolbar-less viewport
    (C++ `USkyBridgeViewLibrary::SetRemasterView` in `Source/SkyBridge/SkyBridgeViewLibrary.cpp`, called from Python as
    `unreal.SkyBridgeViewLibrary.set_remaster_view(True)`), then made topmost + click-through + no-activate, and focus
    is handed back to Skyrim. You play Skyrim and see Unreal. Editor popups (Message Log) are hidden.
  - `live_bridge.py` turns off "Use Less CPU when in Background" (`bThrottleCPUWhenNotForeground` on the
    `Default__EditorPerformanceSettings` object; also in `Config/DefaultEditorSettings.ini`), sets game view, realtime,
    FOV = Skyrim's FOV (both are horizontal; verified by comparing screenshots) and motion blur off.
  - Weather was read from the wrong packet field (cell name, v[28]); now v[27], so rain/fog/overcast reach the sky.
- The C++ build needs the stub .NET SDK registry key; it had disappeared and was recreated
  (`HKCU\SOFTWARE\Microsoft\Microsoft SDKs\NETFXSDK\4.6.2` `KitsInstallationFolder` = `stub\NETFXSDK\4.6.2\`).
  Known-good module binaries are in `unreal/SkyBridge/Binaries/known_good`.
- Whiterun's walls, towers, castle, stone stairs and cobblestone road pieces were missing: they are worldspace **large
  references** (WRLD RNAM), which Skyrim SE attaches separately, so they are not in the grid cells' reference lists the plugin
  walked. Plugin now also visits `worldSpace->largeRefData.formIDCellMap` and `worldSpace->persistentCell` (only refs
  with loaded 3D, de-duplicated; status bit 0x800 if that pass faults). That build is in `build/Release` and is installed by
  `start_bridge.py` (`install_plugin`: backup to `C:\Users\Aidan\SkyrimBackups`, test-load, copy) the next time it starts
  Skyrim; it can't be copied while Skyrim runs. Until then `live_bridge.py` places the large refs from
  `area2/large_preview.json` (made by `tools/large_refs_preview.py` from Skyrim.esm, folder SkyBridge/LargeRefs) and
  removes each one as soon as the stream delivers the same form ID. Verified visually at the Whiterun gate.
- Editor GPU crash ("Too many residency sets", in point-light cubemap shadows): shadow-casting point lights cut 24 -> 8.
  Do NOT set `D3D12.ResidencyManagement=0`: tried, the GPU hung at startup.
- **Photoreal lighting pass** (UE5 physically based setup, like Oblivion Remastered's renderer; the assets are still
  Skyrim's): `build_environment`/`update_sky` now use a real-strength sun (100000 lux x weather factor, angular size
  0.53 deg, cloud shadows), a moon as atmosphere light 1, SkyAtmosphere + **VolumetricCloud**, real-time sky light,
  height fog with **volumetric fog**, histogram auto-exposure in EV100 (-3..16; needs
  `r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange=True`, without it the image is white), higher Lumen quality,
  light bloom/vignette, no grain/motion blur. Point lights are in candelas. `DefaultEngine.ini` now enables **virtual
  shadow maps** and **hardware ray-traced Lumen** (RTX 5080), TSR, finer volumetric fog grid (backup:
  `DefaultEngine.ini.bak_prephoto`). Verified by screenshot in Whiterun (rain weather).
- Editor crash `StaticMesh->GetRenderData()->IsInitialized()`: `import_ready` re-imported every model in `ready.txt`
  on each start, replacing meshes already in use. Now skips existing assets; new C++
  `USkyBridgeViewLibrary::EnsureMeshRenderable` (Python `ensure_mesh_renderable`) gates every mesh before use.
  `Editor.AsyncStaticMeshCompilation=0` is set in `[ConsoleVariables]`.
- **Performance / input lag** (measured with `stat unit`): was 30 fps, 113 ms input latency. Causes: Unreal frame
  pipelining, Lumen quality 2, and Skyrim rendering an invisible Ultra frame at 180 Hz on the same GPU (50-65% of it).
  Fixes: `r.OneFrameThreadLag=0` + `r.GTSyncType=1` (latency 113 -> 45 ms), Lumen quality 1, spawned actors static until
  they move, lights only updated when changed. `start_bridge.py` applies a **Skyrim remaster profile** when it launches
  Skyrim (60 fps cap, 1024 shadows, no SSAO/SSR/DOF/volumetrics/grass, `iTexMipMapSkip=2`; originals in
  `C:\Users\Aidan\SkyrimBackups\remaster_profile_original.json` + full file copies). Undo: `--skyrim-profile-off`;
  skip: `--full-skyrim-graphics`. Only applied when no backup exists. **Do not set SSE Display Tweaks
  `Resolution=960x540` + `BorderlessUpscale=true`**: Skyrim deadlocked at the main menu twice (no crash log, ~0 CPU);
  removed, and Skyrim starts normally with the same plugin build.
- **Flicker + "mossy cobblestone"**: Skyrim decal shapes (`BSLightingShaderProperty` flags1 bit 26/27; e.g.
  `wrmossalpha01` on 20 wall models) z-fought and, unmasked, drew as solid moss sheets. `tools/find_decals.py` writes
  `area2/tex/decal_textures.txt`; `remaster_materials.configure` masks them and sets static switch `IsDecal` (world
  position offset 1 cm toward the camera; only set on decals to avoid extra permutations). `apply_world` drops
  large-ref preview pieces whose position matches a streamed ref (they were drawn twice).
- **Mountain backdrop**: `tools/lod_terrain.py` converts Skyrim's terrain LOD (`meshes\terrain\tamriel\*.btr`, level 8
  near Whiterun, 16 farther; textures from `Skyrim - Textures7.bsa`), skipping the detailed cells and sinking 60 units;
  Blender exports `area2/export/lodterrain.fbx`; `remaster_materials.py` imports it (`SKY_LOD_TERRAIN=1` to redo);
  `spawn_static_world` places it. Object LOD (.bto: distant buildings/trees) not done yet.
- **Master material** `M_SkyMaster` + `MI_<key>` instances (`unreal/SkyBridge/remaster_materials.py`; run headless with
  `UnrealEditor-Cmd.exe SkyBridge.uproject -run=pythonscript -script=unreal/SkyBridge/remaster_materials.py`, editor
  closed; also re-imports upscaled textures). Roughness from Skyrim's specular mask (normal-map alpha, extracted by
  `tools/textures_pbr.py` to `<key>_s.png`, 111 textures), `_rmaos` PBR where present, foliage via shading-model
  override, global **wetness** and **snow cover** from `MPC_Weather`. `ue_assets.material_for` now creates instances.
- **Weather**: per weather family (`Live.WEATHER`) cloud coverage/density/storm on a dynamic volumetric-cloud material,
  fog, sun factor; wetness builds over ~1 min of rain, dries over ~4 min; rain curtains (`M_RainCurtain`, texture
  `area2/tex/rainstreaks.png`) follow the camera. Night exposure floor EV100 1.5 (lower made night look like day).
  Interior cells (empty worldspace in the packet) switch off sun/moon/clouds/rain. Verified: rain (wet roads), night.
- **Water**: `M_SkyWater` (Single Layer Water, Skyrim's `defaultwater.dds` normal panning in world space).
- **Textures**: `tools/upscale_textures.py` (Real-ESRGAN x2 via PyTorch CUDA + spandrel, model in `tools/models`)
  upscaled the 54 diffuse maps <= 1024 px; originals in `area2/tex_orig`. Most textures are already 2K/4K (mods).
- **Packet v2** (`shared/BridgeShared.h`, appended so v1 readers still work; `PKT_FMT "<4I21f2I64s64s64sI11fI21f"`):
  v[30] uiFlags (bit0 show Skyrim: paused/menu/dialogue/loading/main menu or player not loaded; bit1 main menu,
  bit2 loading, bit3 combat, bit4 sneaking, bit5 weapon drawn, bit6 in world), v[31:37] health/magicka/stamina
  (current, max), v[37:41] rain/snow/cloudy/pleasant (TESWeather DATA flags blended by `currentWeatherPct`),
  v[41] weatherPct, v[42] last weather, v[43:46] sun disc world pos (`Sky::sun->sunBaseNode`), v[46:61]
  Sky::skyColor sunlight/ambient/fogNear/skyUpper/horizon, v[61:64] fogNear/fogFar/windSpeed. uiFlags are written even
  at the main menu (frame stays 0).
- **`remaster_watch.py`** (background, `pythonw`, started by `start_bridge.start_watch()` from `--remaster`, killed by
  `--remaster-off`): Unreal window alpha 255 only when in the world AND Skyrim is the foreground window, else 0 (menus,
  loading, main menu, alt-tab show Skyrim). HUD = three layered click-through topmost windows (compass from camera
  rotation column 1, bars shown in combat/weapon drawn/not full, crosshair), PIL-rendered. Needs packet v2.
  Black screen cause: the remaster view went up while Skyrim sat at the main menu (hour 0 -> Unreal renders midnight).
- **Weather from Skyrim's data** (`Live.streamed_weather`): sun factor/fog/clouds from the blended classification, fog
  density from `fogFar`, sun rotation from the sun disc direction, sun light colour = normalized `skyColor[kSunlight]`,
  fog inscattering = `skyColor[kFogNear]`. Falls back to the weather-name table with a v1 plugin.
- **Rain**: C++ `USkyBridgeViewLibrary::SpawnRainField` (ISM, 12000 instances of `SM_RainStreak` = engine cylinder with
  huge bounds extension, otherwise instances are culled at their spawn position) + `M_RainDrops` (Custom HLSL WPO:
  world-locked wrap into a `RAIN_BOX` 16 m x 12 m box around the camera, fall 8.5-12 m/s, opacity = MPC Rain x 0.28,
  fades within 2.5 m of the camera). The actor is moved in whole box periods. Verified by screenshot. Rain is not
  occluded by roofs yet.
- **Rivers/lakes**: `tools/lod_terrain.py` also writes the btr water shape of every tile (`area2/lodwater_obj`), exported
  with Blender to `area2/export/lodwater.fbx`, imported by `remaster_materials.lod_water()` (`SKY_LOD_WATER=1` to redo)
  with `M_SkyWater`; replaces the `water.csv` planes. Verified: the White River channel south of Whiterun has water
  (water -4700, terrain dips to -4750, i.e. shallow). Most btr water sits at -14000 (default, under the terrain).
- **Skyrim profile v2**: `skyrim_profile(True)` now applies keys not yet recorded in the backup JSON (so additions take
  effect without undoing first) and handles JSON files: Community Shaders `SettingsUser.json` effects off and
  `Upscaling/qualityMode` 3 (exact DLSS preset index unverified; check in the CS menu, End key), plus shorter Skyrim LOD
  distances, no LOD water reflections, fewer particles/decals.
- **Textures**: Whiterun's wood/roof/trim textures are 2K with Community Shaders PBR `_rmaos` maps already. The blur was
  Unreal's texture streaming pool (1000 MB default): now `r.Streaming.PoolSize=5000`, `r.MaxAnisotropy=16`,
  `r.Tonemapper.Sharpen=0.6`. `tools/derive_spec.py` derives specular masks for textures with neither (19).
- `tools/ue_run.py <script.py>` runs a script in the live editor through the exec hook and prints the output.
- Live material/texture imports open the Content Browser drawer over the remaster view; re-run `--remaster` to close it.
  `--remaster` now toggles the view off/on (the editor restores windowed-fullscreen from the last session).
- Diagnostics: `tools/stream_coverage.py` (stream vs imported assets), `tools/esm_persistence.py`, `tools/find_overrides.py`
  (which plugins override given refs), `tools/queue_large_refs.py` (pre-convert large-ref models), `tools/capture_window.py`.

## Debug hooks (inside the running editor)
- Screenshot: create `area2\shot_request.txt`; the editor tick saves `shot_ue.png` in the project root.
- Run code: write a script to `area2\exec_request.py`; the tick executes it (globals `unreal`, `live` = the Live
  instance, `V`, `U`) and writes stdout/tracebacks to `area2\exec_out.txt`.

## Open issues / tasks (in priority order)
1. **Visual check** done for camera, terrain and sun (Whiterun gate, dawn). Still to check: water, night, rain/fog.
   The terrain looks sandy at dawn because of the strong orange sun + auto-exposure; the baked tile textures are right.
   Map Check lists `M_terrain_tile_*` as missing at startup; the materials exist and are assigned (load-order warning).
2. **NPCs/characters** are the biggest missing piece; not started. Plan: (a) plugin: third world-stream mapping with
   each loaded actor near the player (ref id, race/sex, worn ArmorAddon model paths for that race, FaceGen head nif
   `meshes\actors\character\facegendata\facegeom\<plugin>\<formid>.nif`, and ~60 skeleton node world transforms from
   `actor->Get3D()` by bone name) at 30 Hz; (b) converter: skinned NIF (BSTriShape + skin partitions) -> FBX against the
   shared Skyrim skeleton (no NIF importer is installed in Blender 5.1; PyNifly is the usual one); (c) Unreal: import as
   skeletal meshes on one skeleton, spawn per actor, C++ drives a PoseableMeshComponent from the stream each tick. Also: verify interiors in game, splashes/puddle
   ripples, wet foliage, stars/aurora, Nanite foliage/grass.
3. **Performance:** thousands of Python-spawned actors; consider instancing (HISM) per model.
4. **Missing content:** NPCs/characters (needs pose streaming from the plugin), rain/mist/aurora/stars, doors and other
   dynamic objects, better water, higher-quality terrain textures, DLSS only via NVIDIA's official UE plugin.
5. Models with spaces in names are skipped; a few suspicious models (hanging elves ear mirror-Y, fence gate door).
6. Keep README.md updated.

## Run it manually
```
python C:\Users\Aidan\SkyrimUnrealBridge\demo.py
```
Debug: `python tools\read_bridge.py`, `python tools\read_world.py` (shows header, refs, lights, status bits).
Disable autostart of the bridge in the editor by creating `area2\no_autostart.txt`.

## Rules / constraints (keep these)
- Windows Smart App Control intermittently blocks freshly built unsigned DLLs (error 4551). Do NOT disable or alter
  security settings; rebuild with a trivial change and test-load via `ctypes.WinDLL`, keep known-good copies.
- Never create accounts or enter passwords/keys. Back up game files before editing them.
- Do not install the "leaked DLSS 5" Nexus tool, and do not extract assets from Oblivion Remastered/NBA 2K; use official NVIDIA plugin.
- Plugin build: `cmake --build build --config Release` in `plugin/`; check the build succeeded before copying
  `build/Release/SkyrimUnrealBridge.dll` to `Data\SKSE\Plugins`.
- Owner preference: build end to end, do not stop to ask or announce next steps.
