# Skyrim Unreal Bridge

Live bridge from Skyrim Special Edition to Unreal Engine 5: an SKSE plugin streams the player's position, camera, field of view, time of day, weather and location out of the running game through shared memory, and an Unreal 5.8 project follows along every frame, so Skyrim's world can be re-rendered in Unreal in real time. Proof of concept, built by Aidan Lucero with AI coding agents (Claude, Codex, Cursor and local Qwen models).

**What is and is not in this repository:** only original source code and notes. No Skyrim, Bethesda or mod files, and no Unreal Engine files or imported assets are included or will be accepted. You need your own legal copies of Skyrim SE, SKSE, CommonLibSSE-NG and Unreal Engine 5.8. Paths in the scripts assume `C:\Users\Aidan\SkyrimUnrealBridge`; change them for your machine. The local-model task queues point at a private home server (`<homelab-tailscale-ip>`) and will not work as-is.

Not affiliated with Bethesda, Microsoft or Epic Games. Code is MIT licensed (see `LICENSE`).

---

# QUICK START
    python C:\Users\Aidan\SkyrimUnrealBridge\start_bridge.py              # start Skyrim + Unreal + overlay
    python C:\Users\Aidan\SkyrimUnrealBridge\start_bridge.py --overlay-only   # just (re)apply the overlay
    python ...\start_bridge.py --no-overlay --opacity 130                  # options
Uses Python only (no PowerShell scripts, no policy changes). Skyrim must be borderless/windowed. The `.ps1` files are older equivalents.
# Skyrim SE -> Unreal Engine 5 bridge (proof of concept)

An SKSE plugin (CommonLibSSE-NG) streams player position, camera, FOV, game time, weather, cell and worldspace into
Windows shared memory (`Local\SkyrimUnrealBridge_v1`, layout in `shared/BridgeShared.h`). An Unreal 5.8 project reads
it every tick and moves its camera to match.

## Status (2026-10-27)

| Piece | State |
|---|---|
| git, CMake, vcpkg (`C:\vcpkg`), Epic Games Launcher, Unreal 5.8 (`D:\UE_5.8`) | installed from official sources |
| SKSE plugin | builds, loads in Skyrim 1.6.1170, streams live data (verified: Whiterun, game hour advancing, weather CloudyDLC2, positions) |
| Unreal project `unreal/SkyBridge` | compiles; running window shows live on-screen readout (frame counter, hour, weather) |
| Camera motion mirroring | user reports grid lines follow the Skyrim camera when moving; exact axis direction/scale not measured (see `SkyrimCameraActor.cpp`: matrix columns, X/Y swap) |
| Reference grid | faint debug lines; plus a floor and 8 real Whiterun buildings (see below) |
| Whiterun mesh export (stretch) | **done for 8 buildings** (Bannered Mare, Breezehome, Blacksmith, house02, guardhouse, castle tower, bridge, castle main building): BSA -> NIF -> OBJ -> Blender -> FBX/GLB -> Unreal `/Game/WhiterunMeshes`. Vanilla diffuse textures applied (BSA DDS -> PNG -> UE materials via `tools/textures.py` + `unreal/SkyBridge/apply_textures.py`; no normal/specular maps, alpha/transparency ignored); vanilla meshes only, not your mod-list overrides. Buildings are placed at their real Skyrim.esm positions (`tools/esm_refs.py` -> `whiterun/placements.csv`, read by `SkyrimCameraActor::SpawnDemoWorld`). Yaw mapping (skyrim yaw + 90 deg) is derived on paper and NOT verified visually; walls/terrain/props are not exported, so only 10 placed buildings exist. |
| DLSS 5 one-click mod (Nexus site/2241) | not installed (see below) |

## Version control
Local git repo only (no remote; do not push). `.gitignore` excludes generated data (`area/`, `area2/` except `*.py`, `whiterun/`,
`build/`, `deps/`), Unreal `Binaries/Intermediate/Saved/Content/Plugins` (except `Content/Python`), meshes/textures/binaries,
screenshots and logs. Several agents edit concurrently: commit only your own files (`git add <files>; git commit -m "..."`), never
`git add -A`, `reset`, `checkout`, `stash` or `clean` over other agents' work.

## Run it
1. Start Skyrim via `skse64_loader.exe`. (`Data\SKSE\Plugins\SkyrimUnrealBridge.autoload` makes the plugin load your newest save automatically; delete that file to disable.)
2. `python tools\read_bridge.py` prints the live values.
3. Launch Unreal:
   `D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\SkyBridge.uproject -game -windowed -ResX=1280 -ResY=720`

## Rebuild
Plugin:
    cmake -S . -B build -G "Visual Studio 17 2022" -A x64 -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake -DVCPKG_TARGET_TRIPLET=x64-windows-static-md
    cmake --build build --config Release
Unreal module:
    D:\UE_5.8\Engine\Build\BatchFiles\Build.bat SkyBridgeEditor Win64 Development -Project=C:\Users\Aidan\SkyrimUnrealBridge\unreal\SkyBridge\SkyBridge.uproject

## Gotchas
- **Smart App Control** blocks some freshly built unsigned DLLs (WinError 4551). Test a build with
  `python -I -c "import ctypes,sys; ctypes.WinDLL(sys.argv[1])" <dll>` before restarting Skyrim; rebuilding gives a different binary
  that is sometimes allowed. Smart App Control was not changed.
- Unreal needed the .NET Framework SDK registered; I could not run the admin installer, so a stub folder is registered at
  `HKCU\SOFTWARE\Microsoft\Microsoft SDKs\NETFXSDK\4.6.2` -> `stub\NETFXSDK\4.6.2\`. Installing the real "Microsoft.Net.Component.4.8.SDK" via the VS Installer is the proper fix (delete the key afterwards).
- Uninstall plugin: delete `SkyrimUnrealBridge.dll` (and the `.autoload` file) from `Data\SKSE\Plugins`.
- The DLSS 5 one-click mod installs a "leaked" NVIDIA build plus ReShade as `dxgi.dll` into the game folder; skipped because it can conflict with Community Shaders/DLSS and needs a Nexus login to download. Say so if you still want it.


## Mesh pipeline (tools/)
1. `bsa.py` reads `Skyrim - Meshes0.bsa` (v105, LZ4) and extracts NIFs (`whiterun/nif`).
2. `nif2obj.py` parses SSE NIFs (NiNode transforms + BSTriShape) to OBJ (`whiterun/obj`).
3. `textures.py` extracts/converts diffuse textures and patches the MTLs. `blender_export.py` (run with `D:\blender.exe -b -P ... -- <obj_dir> <out_dir>`) joins each building, scales Skyrim units to metres, exports FBX + GLB (`whiterun/export`).
4. `unreal/SkyBridge/import_whiterun.py` imports the FBXs (run via `UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script=...`).
`tools/blender_preview.py` renders a quick preview PNG of a GLB (`whiterun/preview_banneredmare.png`).

## Known state at last test
- Skyrim's frame counter was not advancing at the final check (game paused / in a menu), so Unreal showed the last received position. Unpause and move to see the camera follow.
- A Windows Firewall prompt for UnrealEditor appeared; it is not needed (all traffic is local shared memory) and was left unanswered.

4b. After importing FBXs run pply_textures.py the same way to build materials.
Unreal scene: sky atmosphere + sun + skylight spawned by SkyrimCameraActor::SpawnDemoWorld.



## Full-area rebuild (current state)
`tools/esm_area.py` reads every placed Whiterun architecture reference (statics, doors, etc.) within 65 m... (radius 6500 units) of the Whiterun gate area from `Skyrim.esm` -> `whiterun/area.json`: 155 distinct models, 417 placements.
`tools/build_area.py` converts them (loose files from your mod list win over the BSAs, so PBR mesh overrides are used), `tools/textures.py` converts diffuse textures (DDS -> PNG, SRGB DDS formats patched), `tools/blender_export.py` exports FBX, `unreal/SkyBridge/import_area.py` imports meshes, builds one texture-driven material per texture and assigns them (692/705 slots).
Unreal reads `area/placements.csv` at start (only when Skyrim data first arrives) and spawns every piece at its real position.
Terrain: `tools/esm_land.py` reads the WhiterunWorld heightmap (7 LAND tiles) from Skyrim.esm -> `area/terrain_obj/terrain.obj` -> Blender -> `unreal/SkyBridge/import_terrain.py` (single flat-brown material, no landscape textures/blending); it is placed via the `terrain` row of `area/placements.csv`.
Limits: only architecture/whiterun models within the radius (no landscape textures, trees, NPCs, interior cells, other mods' objects); placement uses yaw only (pitch/roll ignored); diffuse colour only (no normal/PBR maps, alpha ignored); one Unreal warning about two directional lights may show on screen.
Re-run order: esm_area.py -> build_area.py -> textures.py -> blender_export.py -> import_area.py.


## One-step start
`start_bridge.ps1` starts Skyrim via SKSE (auto-loads your newest save), waits for live data, then opens Unreal. If your PowerShell execution policy blocks scripts, run its steps by hand (or change that setting yourself; I did not).
If Skyrim dies right after launch, run `skse64_loader.exe` again (the first attempt after a reboot sometimes fails; a Bethesda launcher window can also block it).
Status (last test): Unreal view followed the player from the Whiterun gate to the main street; the "multiple directional lights" warning is fixed.

## Overlay mode (compare Unreal against Skyrim)
`tools/overlay.ps1` makes the Unreal window borderless, click-through and ~50% transparent, exactly over Skyrim's window (Skyrim must be borderless/windowed). Run it after both are open. To undo, close Unreal and start it again.
## Latest additions
- Area widened to radius 11000 units: 213 models, 790 placements (LOD proxy models dropped).
- Terrain now has the game's vertex colours + a tiling `fielddirtgrass01` ground texture (no real per-cell texture blending).
- Alpha-masked materials for textures with near-binary alpha (12 textures); other transparency still ignored.
- Pitch/roll still ignored (only ~20 placements are tilted, mostly rubble piles).
- Debug grid in the sky is off (`bDrawDebugGrid` in `SkyBridgeGameMode.cpp`).

## Alignment verification and the live-dump workflow
Reconstructing from `Skyrim.esm` alone mixed in copies from other worldspaces (e.g. a second gate) and missed mod-added objects. Now the plugin can dump what the game actually has loaded:
1. Create an empty file `Data\SKSE\Plugins\SkyrimUnrealBridge.dump` while standing in the game (wait ~1 min after loading a save; dumping during loading crashed Skyrim once, so the plugin now waits until the cell has been stable ~20 s).
2. It writes `...\My Games\Skyrim Special Edition\SKSE\SkyrimUnrealBridge_refs.tsv` (every loaded reference with a model: position, rotation, scale, model path) and deletes the flag.
3. `tools/compare_refs.py <tsv> area2/placements.csv` compares truth vs the Unreal placements. Result at the Whiterun gate: 89/120 architecture objects exact, the rest within 2-14 units (animated doors); 40 mod-added objects (Lux braziers etc.) only exist in the live dump.
4. `tools/truth_to_area.py out.json dump1.tsv [dump2.tsv ...]` builds the model/placement list (dumps from different spots merge) -> `build_area.py` -> `textures.py` -> `blender_export.py` -> `import_area2.py` + `import_terrain2.py`. The current Unreal scene (`area2/`) is built from one dump: 254 placements, 66 models, only what was loaded around the Whiterun gate. Walk elsewhere, dump again, merge, rebuild to extend it.
Overlay: `tools/overlay.ps1` now uses WS_EX_NOACTIVATE and hands focus back to Skyrim, because Skyrim pauses whenever it loses window focus.


## Extending coverage (automatic)
- The plugin now records everything the game loads around you as you walk (every time you move >2500 units, once the cell is stable): `...\SKSE\SkyrimUnrealBridge_refs_all.tsv` (cumulative, de-duplicated) and `SkyrimUnrealBridge_centers.txt` (where you have been).
- `python tools\auto_build.py` rebuilds the Unreal scene from that record: where you have been, live data wins (mods, exact transforms); elsewhere `Skyrim.esm` WhiterunWorld refs fill in (`whiterun/area_esm.json`). Only NEW models/textures are converted/exported/imported. It closes and reopens Unreal. Then `python start_bridge.py --overlay-only`.
- Current build: 448 merged refs, 121 models -> 400 placements (shop signs don't convert).
- Tip: "Continue" on the Skyrim main menu loads your newest save; if the Skyrim 'Creations/10th Anniversary' pop-up appears first, dismiss it.
- Known: Skyrim sometimes crashes on exit with this mod list (crash log at the moment of closing); harmless.

## Live editor fixes (2026-10-27 evening)
- Unreal Python's `unreal.Rotator(a, b, c)` is (roll, pitch, yaw). `live_bridge.py` used positional args, so the terrain
  was pitched 90 degrees (objects floated over empty sky) and the sun direction was wrong. Now uses keyword args.
- Debug hook: a script written to `area2\exec_request.py` runs inside the editor; output goes to `area2\exec_out.txt`.
- **Remaster view:** `python start_bridge.py --remaster` (done automatically by `demo.py`) shows only Unreal's viewport,
  fullscreen over Skyrim; Skyrim keeps keyboard/mouse focus, so you play Skyrim and see the Unreal render.
  `python start_bridge.py --remaster-off` gives the normal editor back. Needs the C++ `SkyBridgeViewLibrary` (rebuild the module).
- Editor keeps rendering while in the background; viewport FOV follows Skyrim's; motion blur off; weather now read from the right field.
- City walls/castle/stairs/roads: these are Skyrim "large references" and were not streamed. The plugin now streams them
  (new build installed automatically by `start_bridge.py` the next time it launches Skyrim); meanwhile Unreal places them
  from `area2/large_preview.json` (`tools/large_refs_preview.py`).

## Crash fix (important)
Skyrim crashed ~1 min after loading when the plugin walked the game's cell list (`TES::ForEachReferenceInRange`): with this mod list that list contains a bad pointer (crash log: SkyrimSE.exe+030B0B3 inside SkyrimUnrealBridge.dll). Now:
- Recording is OFF by default. Turn it on by creating an empty file `Data\SKSE\Plugins\SkyrimUnrealBridge.autodump` (delete it to turn it off). An empty `SkyrimUnrealBridge.dump` file does a single one-shot dump.
- The iteration is wrapped in SEH; if it faults, recording disables itself for the session instead of crashing the game.
- Skyrim also tends to crash on exit with this mod list (unrelated to the bridge).

## Photoreal lighting pass (2026-10-27 night)
The Unreal side now uses UE5's physically based setup (what Oblivion Remastered's renderer uses; the meshes/textures are still Skyrim's):
real-strength sun and moon driven by Skyrim's hour and weather, SkyAtmosphere, volumetric clouds, volumetric fog,
real-time sky light, EV100 histogram auto-exposure, hardware ray-traced Lumen GI/reflections, virtual shadow maps and TSR
(`unreal/SkyBridge/Config/DefaultEngine.ini`, backup `DefaultEngine.ini.bak_prephoto`). Point lights use candelas.
If the image turns white, `r.DefaultFeature.AutoExposure.ExtendDefaultLuminanceRange=True` is missing.
Also fixed an editor crash from re-importing meshes that were in use (`import_ready` skips existing assets;
C++ `EnsureMeshRenderable` gates meshes).

## Performance, weather, materials, textures (2026-10-27 late)
- Input latency 113 -> ~45 ms (`r.OneFrameThreadLag=0`, `r.GTSyncType=1`), Lumen quality 1, static actors.
- `start_bridge.py` runs Skyrim with a cheap render profile (its frame is hidden under Unreal's): 60 fps, low shadows,
  no SSAO/SSR/DOF/volumetrics, quarter-res textures (`iTexMipMapSkip=2`), no grass. Backed up; undo with
  `python start_bridge.py --skyrim-profile-off`, skip with `--full-skyrim-graphics`. Do not lower the resolution with
  SSE Display Tweaks (`Resolution`/`BorderlessUpscale`): Skyrim froze at the main menu with it.
- Flicker / "mossy cobblestone": Skyrim decal shapes (moss, road edges, blood) z-fought and rendered as solid sheets. They
  are now alpha-masked and pushed 1 cm toward the camera (`IsDecal` switch; list in `area2/tex/decal_textures.txt`).
  Large-ref preview pieces that duplicate streamed refs are dropped.
- Mountains: Skyrim's terrain LOD (`.btr` from `Skyrim - Meshes1.bsa`) is converted by `tools/lod_terrain.py` and spawned
  as `/Game/Area2/lodterrain` around the detailed area.
- One master material (`M_SkyMaster`) with Skyrim's specular masks, wetness and snow; `remaster_materials.py` converts meshes (headless).
- Weather: volumetric cloud cover per weather, rain curtains, wet surfaces, snow cover, dark nights, interiors without sky.
- Water: Single Layer Water material with Skyrim's water normals.
- `tools/upscale_textures.py`: Real-ESRGAN x2 (PyTorch CUDA) for low-res diffuse textures.
- Not done: NPCs/characters (need skeletal streaming from the plugin).

## Menus, HUD, real weather, rain, rivers (2026-10-27 evening)
- Plugin packet version 2 (appended fields): menu state, player health/magicka/stamina, Skyrim's weather classification
  (rain/snow/cloudy blended over the transition), sun position and colour, fog colour/distance.
- `remaster_watch.py` (started by `--remaster`): menus, dialogue, loading screens and the main menu show Skyrim's own
  frame (inventory, Wait, map work); in the world Unreal covers Skyrim and a Skyrim-style HUD (compass, bars, crosshair)
  is drawn above it. Fixes the black screen at the main menu (Unreal's midnight render was covering it).
- Unreal weather follows Skyrim's own weather data (not the weather name), sun direction/colour come from Skyrim's sun.
- Rain: 12000 GPU-animated streaks around the camera (`SpawnRainField` in the C++ module + `M_RainDrops`).
- Rivers/lakes: water layer of Skyrim's terrain LOD (`tools/lod_terrain.py` -> `/Game/Area2/lodwater`).
- Skyrim profile now also switches off Community Shaders' effects (SSGI, volumetric lighting, wetness, parallax,
  screen-space shadows...), sets its DLSS to a lower internal resolution, and shortens Skyrim's LOD distances.
- Unreal texture streaming pool 1000 -> 5000 MB (textures were drawn at low mips), 16x anisotropy, light sharpening.
- Mods stay installed: Unreal converts its assets from the same Data folder, and Skyrim loads them at quarter resolution.

## Real mountains/trees, clouds, puddles, lighting (2026-10-27 night)
- **Distant world** (`tools/distant_world.py` -> `area2/distant_refs.json`): every mountain, cliff, big rock and tree that
  Skyrim.esm/Update.esm place in Tamriel around Whiterun (43k references, 130 models; mountains up to ~6 km, trees ~1.6 km).
  `live_bridge.distant_some` builds one instanced-mesh actor per model (folder SkyBridge/Distant) and the live stream skips
  those form ids, so loaded cells are not drawn twice. Missing models go through the normal converter queue. Re-run the tool
  to change radii (`RULES`); `nodistant` in `area2/debug_flags.txt` turns the layer off. Skyrim itself only shows low-detail
  LOD for all of this.
- Mountains/cliffs/rocks get permanent snow on upward faces above `SnowLine` (static switch `AltitudeSnow` in `M_SkyMaster`,
  set by `remaster_materials.configure` for mountain/cliff/rock textures).
- Do not toggle Nanite on meshes in the live editor (crashed in `EnsureMeshRenderable`); `nanite_landscape()` in the
  headless pass handles it (imports already build Nanite by default).
- **Sky**: the world is ~70 m below the UE origin, so the default SkyAtmosphere put the camera underground: no clouds, flat
  sky. The atmosphere's planet top is now Skyrim's sea level (`SEA_LEVEL`, transform mode planet-top-at-component), cloud
  layer 2-8 km. Rain coverage capped (0.65-0.7) so clouds keep their shape instead of one grey sheet.
- **Washed-out fix**: the height fog sat at z=0 (far above the world: everything was inside dense fog). It now follows the
  camera height with falloff 0.2 and lower densities; Skyrim's sRGB sun/fog colours are converted to linear and the fog
  colour is dimmed; auto-exposure bias per weather (+0.3 clear .. -0.7 storm) so rain stays dark; contrast 1.08.
- **Clouds were invisible because of wrong parameter scales**: on `m_SimpleVolumetricCloud`, `Cloud_GlobalCoverage` is a
  bias (default -0.2 = cumulus, ~0.18 = broken rain clouds, 0.45 = flat overcast) and `Cloud_GlobalDensity` defaults to
  0.008; the old values (coverage 0.3-1.0, density 0.6-1.4) rendered no clouds at all. `Live.WEATHER`/`streamed_weather`
  now use that scale, and rain no longer dims the sun to 4% (the clouds shadow it themselves; unlit clouds look grey).
- **Water**: one plane per Tamriel cell with the "has water" flag at its XCLW height (`area2/water_wide.csv` from
  `python tools/distant_world.py --water`, 469 cells), replacing the LOD water layer. `M_SkyWater` is murkier (rivers are
  shallow; clear water showed the tan bed). Known issue: where the coarse LOD terrain is lower than the real terrain, a
  plane can show as a flat slab at a cell edge; fix = extend the full-resolution LAND terrain over the water cells.
- **Trees**: the converter missed the colour maps of the PBR pine/aspen/reach trees (only `_n`/`_rmaos` were written), so
  needles drew as white unmasked cards. `tools/fill_textures.py` fetches missing colour maps (loose PBR files or BSAs) and
  lists cut-out ones in `area2/tex/alpha_masked_extra.txt`; the distant layer overrides those slots on its components
  (`Live.fix_slots`), `remaster_materials.fix_missing_slots()` fixes the mesh assets in the headless pass.
- **Moss sheets**: decal alpha (0.45-0.9) is remapped and dithered (`IsDecal` switch), keeping moss in the cracks only.
- **Puddles**: `M_SkyMaster` places world-space puddles (`area2/tex/puddlenoise.png`, `tools/puddle_noise.py`) on flat
  ground as wetness builds, with mirror roughness and rain ripples (Skyrim's water normal map); damp surfaces are
  semi-gloss instead of mirror; wetness fades out 60-160 m away so distant terrain no longer turns white.

## Complete cities from the game files (2026-10-27 late night)
- `python tools\distant_world.py --world whiterunworld` dumps every placed reference with a model in a worldspace
  (Skyrim.esm + Update.esm) to `area2/world_<edid>.json`; done for whiterun/solitude/windhelm/markarth/riften worlds.
- While Skyrim reports that worldspace, `live_bridge` places the enabled references the stream has not delivered
  (World Outliner folder `SkyBridge/City`); a streamed copy with the same form id replaces it. Enable-parented refs
  (civil-war rubble, barricades, quest props) and loose items are left to the stream, so your save's state wins.
  Flag `nocity` in `area2/debug_flags.txt` turns it off.
- Why things were missing: the plugin drops every model with "marker" in its path, and Warmaiden's forge
  (`furniture/blacksmithforgemarkerwr.nif`), the tanning rack, smelter and Skyforge use such names. Requested a narrower
  filter from Claude Code (COORDINATION.md). In Whiterun the layer adds 249 pieces (forge, smelter, tanning rack,
  planters, shrubs, stables, pond walls, training dummies...).
- Effect cards inside meshes (`textures/effects/*`: forge heat haze, vapor) are hidden; as colour maps they rendered
  as rainbow sheets.
- Fixed in the same pass: `apply_world` crashed every second after the ref loop (bad index in the duplicate check),
  which had stopped all streamed lights and preview cleanup; `import_ready` tracks names instead of a line index
  (newly converted models were never imported); `tick` is guarded against re-entry during imports (editor crash).
- Audit (all of whiterunworld vs what is drawn): everything enabled is placed except `genericbannerred01` (x3), which
  fails to convert (reported to Claude Code). Texture keys with spaces (`old wood 24.png`, used by a mod chair whose nif
  stores an absolute texture path) now match slot names; preview spawns (`SkyBridge/LargeRefs`) get `fix_slots` too.

## Flicker, night sky, wet walls, far trees, city prefetch (2026-10-27 late night)
- **Flicker:** 191 Whiterun pieces were spawned twice in the same spot (city layer + `LargeRefs` preview, same form id),
  which z-fights. The preview skips ids the city layer drew; exact twins in the game data (same model/pos/rot) are drawn once.
- **Night sky:** `M_NightSky` on a 1000 km camera-centred sphere (`SkyBridge/Weather/NightSky`). It is an *Is Sky*
  material (a translucent dome gets fogged away): sky atmosphere luminance + sun/moon discs + procedural stars and aurora
  curtains. `Night` fades in once the sun is ~8 degrees down and only through a clear sky; `Aurora` in Skyrim's northern
  clear weathers (`*ClearSN*`, `*Aurora*`). Brightness: scalar `Intensity` (default 6) on the dome's dynamic instance.
- **Wet walls:** master material `WetWalls` (0.35): in rain, walls, trunks and leaves get damp too; undersides stay dry.
- **Far trees:** distant-layer trees drawn to 3 km (was 1.6 km), about +0.6 ms GPU. GPU frame ~16 ms, mostly Lumen;
  geometry is cheap, so per-model instancing of the streamed actors is not worth it yet.
- **Other cities:** ~700 models of Solitude/Windhelm/Markarth/Riften are converted in the background (40 per batch,
  after the previous batch, so live requests are not delayed) and imported only when you enter that city.
- **Doors** still do not open in Unreal (nif animation, not streamed); requested from Claude Code.

## Whiterun interiors (2026-10-27 late night)
- `python tools\distant_world.py --interiors Whiterun` dumps the 27 interior cells whose editor id starts with
  "Whiterun" (Dragonsreach + basement + Jarl's quarters, Jorrvaskr + basement, the Bannered Mare, Breezehome, shops,
  houses, temple, Hall of the Dead + catacombs, jail, Underforge...) with every reference and the cell lighting (XCLL) to
  `area2/interiors_whiterun.json` (10,785 refs). Any `area2/interiors_*.json` is picked up.
- Inside (no worldspace in the packet) `live_bridge` finds the cell from the streamed form ids and places its enabled
  references like the city layer, so crafting stations and other pieces the stream drops are there; streamed copies win.
- Interiors hide terrain, water, the exterior large-ref previews, distant world, sky dome and clouds (interior cells
  overlap outdoor coordinates), and auto-exposure may go down to EV -1.5 so lamp-lit rooms adapt like the eye.
- Also dumped (same command, other prefix): Solitude, Windhelm, Markarth, Riften, Riverwood, Falkreath, Dawnstar,
  Morthal, Winterhold: 188 interior cells, ~86k references in total.
- **Dungeons** (every other interior of Skyrim/Update/Dawnguard/HearthFires/Dragonborn): `python tools\distant_world.py
  --dungeons` -> `area2/interiors_dungeons_1..13.json` (569 cells, 383k refs, ~11 MB each), `area2/dungeon_index.json`
  (64 probe ref ids per cell) and `area2/dungeon_models.txt` (5,587 drawn models, most used first). `live_bridge` keeps
  only the index in memory and loads one cell's file (~0.1 s) when the streamed ids match its probes; dungeon models
  are prefetched last, 40 at a time, after the city ones.
- **Models with spaces in their names** (`clutter/dining set/...`, `architecture/falmer hut/...`, Windhelm's
  `gray quarter` interior walls; 108 models, 10.6k refs, 607 of them placed by the interior/city layers) were dropped:
  `requests.txt`/`ready.txt` are whitespace-separated. Asset names now turn spaces into `_`
  (`clutter_dining_set_basictankard01`); `live_bridge` holds these requests back until the converter writes the same
  names and creates `area2/spaced_names_ok.txt` (request to Claude Code in COORDINATION.md). Test:
  `python area2/test_spaced_names.py`.
- Their models convert in the background (Whiterun's first, then the other interiors and cities) and are imported when you walk in. Imports now
  only happen for models the current session asked for, so prefetched ones survive an editor restart without a flood.

## DLSS, sharpness, black planters/canals (2026-10-27 night)
- **DLSS:** NVIDIA's official DLSS 4.5 plugin for UE 5.8 (v8.9.0, from developer.nvidia.com/rtx/dlss) is in
  `unreal/SkyBridge/Plugins/DLSS` + `StreamlineNGXCommon`, enabled in `SkyBridge.uproject`. Runs as **DLAA**: the
  editor viewport renders at native 2560x1440 (before: "screen percentage based on display resolution" + TSR, soft)
  and DLSS does the anti-aliasing. Log line to check: `Creating NGX DLSS Feature SrcRect=2560x1440 ... DLAA(5)`.
  For more fps: `r.Editor.Viewport.ScreenPercentage 67` (DLSS Quality). Ray Reconstruction (`r.NGX.DLSS.DenoiserMode 1`)
  is supported on this GPU but not enabled yet.
  DLSS 5 "neural rendering" has no official public Unreal plugin; the DLSS 5 tools around use a leaked NVIDIA DLL, which
  this project does not install (see HANDOFF rules).
- **Black see-through planters/beds:** `wrfieldgrass01`, `rocks01`, `road01`, `dirt02`... are on the converter's decal list
  but are ground blend layers (Skyrim fades them with vertex alpha). The decal cut-out made holes. `remaster_materials.
  BLEND_LAYERS` renders them opaque.
- **Canal water:** Whiterun's canal/pool meshes (`wreffects/*river*`, `wrwaterstream`, `water/water1024`) use Skyrim's
  water shader (no texture), so their slot was hidden; `live_bridge.water_slots` gives them `M_SkyWater`.
- City layer no longer duplicates pieces the large-ref preview already placed (191 duplicates were z-fighting).
- **Ground flicker (z-fighting):** blend layers stay opaque but keep `IsDecal` on: the master's IsDecal path also moves
  the surface 1 cm toward the camera (opaque materials ignore its cut-out), so it no longer fights the ground under it.
- Streamed torch lights ignore sub-24-unit / <15% radius jitter (Skyrim animates flicker; re-applying it every second
  popped point-light shadows).
- Cell water is now clipped to Skyrim's real terrain: `distant_world.py --water` also writes `area2/water_quads.csv`
  (128-unit squares where LAND is below the water height, 11k runs) drawn as one instanced actor `CellWater`; whole-cell
  planes floated as see-through dark slabs over lower ground.
- Blend-layer lift is a master parameter `DecalLift` (cm, default 1); ground blend layers use 8 cm because Nanite simplifies the ground and the layer separately, so 1 cm still z-fought at a distance.
- **DLSS Ray Reconstruction** on (`r.NGX.DLSS.DenoiserMode=1`, DefaultEngine.ini + live_bridge): replaces Lumen's denoiser,
  steadier GI/reflections on wet ground. Log shows `DenoiseMode=DLSSRR`.
- Clear-weather exposure: EV bias -0.3 (was +0.3, blew out pale ground/sky), local-exposure highlight contrast 0.6.
- City layer skips/removes a piece when the stream shows the same model within 300 units (mods move/replace refs).
- If the Unreal UI (Outliner/Details) shows over the game after an editor restart, the view is no longer fullscreen and
  renders at ~2033x1296 (soft): `python start_bridge.py --remaster` restores 2560x1440.

## Terminal windows popping up / Skyrim pausing (2026-10-27 late night)
- `remaster_watch.py` (runs windowless) called `tasklist` every second; each call opened a new terminal window that took
  focus, and Skyrim pauses when it loses focus. `start_bridge.running/pids/watch_pids` now run hidden.
- OAR "Major issue detected": `OpenAnimationReplacer-IEDConditionExtensions.dll` (and IED, which it needs) had been
  parked in `Data\SKSE\Plugins\_disabled_for_bridge` by `tools/skyrim_plugins.py`; both are back in Plugins (next start).

## Slow-motion Skyrim fix (2026-10-27 late night)
- The player moved as if over-encumbered: Skyrim's game clock ran at 74% of real time (14.8 game s per real s instead
  of 20; `python area2/probe_player.py` measures it). SSE Display Tweaks' `DynamicMaxTimeScaling` with
  `MinimumFramerate=60` caps each game step at 1/60 s, and Skyrim only reaches ~44 fps while Unreal shares the GPU, so
  the whole game played in slow motion. The remaster profile now sets `MinimumFramerate=20` (backed up / undone like
  the other profile keys); it takes effect the next time Skyrim is started through `play.py` / `start_bridge.py`.

## Smooth NPC movement (2026-10-27 late night)
- NPCs used to jump to a new position 15 times a second, and posing 12 of them took ~70% of the editor's frame
  time (pure-Python matrix math per bone), which also made the whole picture choppy.
- `npc_live.py` now moves every NPC every frame, gliding between the actor-stream samples on a playback clock that runs
  slightly behind the stream: when Skyrim's stream pauses (~0.3 s hitches) NPCs ease to a stop and catch up instead of
  freezing and jumping. Limbs update at the stream rate (~30 Hz) for NPCs within ~21 m, less often further away.
- Same pose math, folded into per-bone quaternion constants (`python area2/test_npc_math.py` checks it against the old
  version). Cost: 720 -> 45 ms per second.

## NPCs: real poses, correct hair/eyes/clothes, skin shading (2026-10-27 late night)
- **Arms out + sliding:** NPCs were drawn in their reference A-pose the whole time. A PoseableMeshComponent only sends
  its bone pose to the renderer from its own tick, and editor-world components do not tick, so the streamed pose was
  stored but never drawn. `SkyBridgeViewLibrary::ApplyPose` (C++, this project's module) sets all bones in one call and
  refreshes the rendered pose; `npc_live._apply_pose` uses it. Check: `area2/probe_arms6.py` prints rendered vs set bone
  positions (they must match).
- **Hair, eyes, clothes:** NPC textures were named by file name only, so mods that reuse a name in different folders
  (hair/eyes/brows all called `Jenassa.dds`, many outfits' `torsof_d.dds`) overwrote each other: black eyes, wrong
  hair maps, outfits wearing another outfit's texture. `python tools/npc_tex_alias.py` converts those 60 textures to
  unique names and writes `area2/npc/tex_alias.json`, which `npc_live` reads when it assigns materials.
- Hair/brow/lash cards are two-sided cut-outs with back-lit (two-sided foliage) shading; skin uses Subsurface Profile.
- **Sliding walkers:** Skyrim does not animate actors it is not drawing (out of its view, occluded, far), so their
  streamed skeleton is frozen (or in the bind A-pose) while they walk. `npc_live` detects that (limbs unchanged while
  moving) and plays a gait cycle recorded from a walker Skyrim is animating. Check: `python area2/probe_stream_limbs.py`.
- Still open: hair colour tint (needs the NPC hair colour from the converter), cloth/hair physics bones.
- Close-up check without moving your camera: `python area2/cap.py "Aela,Carlotta" 230 body` -> `area2/body_all.png`.

## Sharper picture: newer DLSS models, close-range detail (2026-10-27 late night)
- **DLSS models:** Ray Reconstruction now uses **Preset E** (the plugin's "latest transformer model"; the default was RR2
  Preset F) and the plain upscaler, used when RR is off, uses **Preset L** (sharpest and most stable; the plugin notes it is
  at full speed on RTX 40/50, and this PC has an RTX 5080). `r.NGX.DLSSRR.Preset=5`, `r.NGX.DLSS.Preset=12` in
  DefaultEngine.ini + `build_environment`. Log check: `NGXDLSSPreset=Preset L(12), NGXDLSSRRPreset=Preset E(5)`.
  Anisotropic filtering 16x and tonemapper sharpen 0.6 were already on.
- **Close-range grain:** Skyrim textures (512-2048 px, upscaled to 2K) are stretched over metres of mesh, so the ground at your
  feet looked smeared. `M_SkyMaster` now adds a fine tiling detail normal + brightness grain (`tools/detail_noise.py` ->
  `area2/tex/detailgrain_n.png`, `detailgrain.png`) at 8x the mesh UVs, full within 3 m and gone by 18 m. Master parameters
  `DetailTiling` (8) and `DetailStrength` (0.6). Two texture samples; negligible cost.
- Right after an editor restart textures are still streaming in for ~1 min, so the picture is soft until then.
- **Whiterun audit (re-run):** everything placed in the game data is drawn except markers, effects, quest-gated
  (enable-parent) and disabled refs, and still the 6 refs whose models the converter cannot produce
  (`genericbannerred01` x3, `hangingrabbit01`, `spelltomerestorationlowpoly`, `basicbook05`; asked in COORDINATION.md).
  0 untextured slots, 0 materials without a colour map, 93/93 lights.

## Canal water, activation prompt, memory (2026-10-27 late night)
- **Canals/pools had no water:** Whiterun's canal and pool meshes are Nanite, and Nanite cannot render Single Layer Water,
  so `M_SkyWater` was rejected on them (log: "Invalid material [M_SkyWater] used on Nanite static mesh"). `water_slots`
  now sets `disallow_nanite` on the components that get the water material; the mesh assets are unchanged.
- `remaster_materials.water_material(rebuild=True)` builds the flow-aware graph from `water_flow_apply.py` (one water
  output node; the old rebuild left a second, unconnected one and the material failed to compile).
- **Activation prompt:** Skyrim's "E Talk / Aela the Huntress" prompt was hidden under the Unreal view. The plugin's
  packet v3 carries the crosshair target; `remaster_watch.py` draws it under the crosshair in Skyrim's style.
- Texture streaming pool 5000 -> 3000 MB in `DefaultEngine.ini` (same as `play.py`): with Skyrim and the editor both
  running, the PC was down to 0.5 GB of free RAM.
