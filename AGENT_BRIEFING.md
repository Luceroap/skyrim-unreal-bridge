# AGENT BRIEFING - read this first (saves you ~20k tokens of exploration)

Project: **Skyrim SE -> Unreal Engine 5.8 live bridge** ("Skyrim remaster in Unreal"). A running Skyrim (SKSE plugin) streams camera, world objects, lights,
NPC poses and gear through shared memory; an Unreal editor (driven by Python) mirrors it with better lighting and materials. Owner: a single user on one PC
(RTX 5080 16 GB, 31 GB RAM, Windows 11). Local git only: **never push**.  Last updated 2026-10-29.

## 0. Hard rules (break these and you hurt the user)
- **Starting the game: only `python play.py` (stop: `python play.py --stop`).** It gets past the main menu by itself (the plugin loads the newest save because `Data/SKSE/Plugins/SkyrimUnrealBridge.autoload` exists; keep that file). Never click through Skyrim's menus and never start Skyrim by another route.
- **Never minimize/hide Skyrim** (Community Shaders crashes: zero-size render target). Do not use computer-use screenshots while Skyrim runs (they hide windows). Use logs, `tools/ue_run.py`, shared memory.
- **One `UnrealEditor.exe` at a time.** Memory commit exhaustion froze the PC before (editor private commit 35-50 GB). Check free commit before starting things: `tools/shot_session.py` has a guard (>= 30 GB).
- **Nothing that needs approval:** no accounts, passwords, installs, security/Smart App Control changes, no deletions of the user's files. Ask before downloads.
- **Do not extract assets/code from Oblivion Remastered or any other game** (study visually / public techniques only). DLSS only through NVIDIA's official UE plugin; do **not** install the "leaked DLSS 5" tool.
- Git: local only. Commit **only your own files** (`git add <paths>`, never `-A`, never reset/checkout/stash/clean others' work). End messages with `Co-Authored-By: <your model> <noreply@anthropic.com>`.
- Back up game files before editing them. Skyrim physics plugins (hdtSMP64, SMP-NPC crash fix, cbp) must stay enabled.
- English ASCII names for files. Short status updates to the user; the user often reads on a phone (files > 30 MB do not reach it: send JPEG).

## 1. Layout (paths: the project lives on D: via junctions; C:\Users\Aidan\SkyrimUnrealBridge still works)
| where | what |
|---|---|
| `plugin/src/main.cpp`, `shared/BridgeShared.h` | SKSE plugin (CommonLibSSE-NG, AE only). Mappings: `Local\SkyrimUnrealBridge_v1` camera packet v3, `_world_v1`, `_actors_v1` (96 actors x 320 bones, seqlock), `_gear_v1`. Remote control file `Data/SKSE/Plugins/SkyrimUnrealBridge.sky` (`hour N`, `weather <EditorID>|release`). |
| `unreal/SkyBridge/live_bridge.py` | the live editor tick (camera, sky, lights, water, rain, hooks). Debug hooks: `area2/shot_request.txt`, `area2/exec_request.py` (use `tools/ue_run.py script.py`). |
| `unreal/SkyBridge/npc_live.py` | NPC/creature spawn + pose (PoseableMeshComponent), armor swaps, weapons |
| `unreal/SkyBridge/{atmosphere,weather_fx,grass_live,tamriel_live,land_terrain_live,memory_governor,...}.py` | add-on layers (see `area2/addons.txt`, `area2/debug_flags.txt`) |
| `unreal/SkyBridge/{fire_fx,mountain_mist,night_sky}.py` | showcase extras: flames, haze + cloud band, moons/planets/aurora |
| `tools/*.py` | converters (nif->obj->fbx->Unreal), asset service, importers, photo tools |
| `area2/` | generated data + control files (huge; do not list it blindly) |
| `notes/index/` | **exact** code index (symbols, imports, entry points, controls, TODO, stats). Start here to find things. |
| `notes/files/<file>.md` | local-model summary of every source file (explanations; may contain mistakes - verify before relying) |
| `COORDINATION.md`, `HANDOFF_FOR_CURSOR.md`, `HANDOFF_FOR_CHATGPT.md`, `README.md` | older context; BRIEFING (this file) wins where they disagree |

## 2. Run it
- `python play.py` (or `Play.bat`): Skyrim (loads latest save by itself, ~1 min) + Unreal live view. `python play.py --stop` closes both.
- `python tools/shot_session.py [--max]` clean photo session; `Photo_Shoot.bat` adds hotkeys (F8 4K, F9 8K, F5 time, F6 weather, F7 release).
- `python tools/perf_profile.py fast|faster|fastest|everyday` live performance profiles (also caps Unreal at 45 fps so Skyrim keeps GPU time).
- `python tools/max_quality.py [--off]` showcase quality (heavy!). `python tools/set_cvar.py "r.X 1"` any console var.
- `python tools/sky_extras.py on|night|off` haze/cloud band, moons+planets+aurora. `python tools/showcase_shot.py ...` pinned-camera 4K/8K shots (`SHOWCASE_DIR` env = output folder).
- `python tools/healthcheck.py` one-screen state check (processes, memory, shared memory, editor heartbeat). Run it before and after risky steps.
- Skyrim clock: write `hour 22` into the `.sky` file (torches/lights follow in ~25 s). Editor exec: `python tools/ue_run.py file.py`.

## 3. Hard-won lessons (each cost us hours)
1. **Memory:** commit, not RAM, is the limit. `llama-server` (the local model) holds ~27 GB; stop it before game sessions. Path tracing (`viewmode pathtracing`) took the editor from 15 to 35 GB and nearly froze the PC: do not enable it on the full scene. Editor memory also grows unexplained to 15+ GB over minutes (prefetch is opt-in via `area2/prefetch_on.txt`).
2. **Editor crash (BoneContainer.cpp:165 AssetSkeletonObj):** a skeleton-less NPC mesh assigned to a PoseableMeshComponent. Guarded in `npc_live.py` (2026-10-29): verify it holds in a long session.
3. **Crash recovery dialog:** after any editor crash the next launch waits on "Restore Packages". Move `unreal/SkyBridge/Saved/Autosaves/PackageRestoreData.json` aside (rename, do not delete) before relaunching. Kill `CrashReportClientEditor.exe` too.
4. **Skyrim not reaching the world** = almost always memory starvation (the local model!) or a second Skyrim start while the editor hangs. Check free commit first.
5. Processes started from a tool shell die when it exits: start long things with WMI `Win32_Process.Create` or a visible `Start-Process cmd /k`. Hotkey tools need the interactive session (not WMI).
6. Smart App Control blocks fresh unsigned binaries intermittently (rebuild + retry later). Never change that setting.
7. Ollama >= 0.40.13 cannot follow a directory junction for its models: `OLLAMA_MODELS=D:\Aidan_Moved\ollama_data\models` is set (user env). Do not point it at the C: junction.
8. PowerShell edits: avoid inline multi-line replace with `\n` in single-quoted strings (it writes literal backslash-n). Write a small Python fixer file instead; never BOM-encode source (`Set-Content -Encoding utf8` adds a BOM).
9. Skyrim is paused whenever another window has focus; the Unreal window sits over Skyrim and Skyrim keeps keyboard focus.

## 4. State of quality (2026-10-29) and what to improve next (highest value first)
1. **Ground/roads look washed out** (pale sand, no cobble/dirt-path detail). Streets are the old baked terrain + low-res atlas (`tamriel_live.py` M_TerrainFar). `land_terrain_live.py` (full-res blended layers, assets in /Game/LandTerrain, 4 tiles imported, tiles.json has 9) was never finished: enabling it showed a grey checkerboard (material not compiled / layer textures missing under `area2/landterrain/tex`). Fixing this is the biggest visual win.
2. **Lighting realism:** Lumen + hardware RT works (see `tools/max_quality.py`); keep scattering low (strong light scattering washed everything out). Sun colour by elevation is hand-tuned in `showcase_shot.py`/`photo_keys.py`: not validated against a reference. Night torches work (22 lit lights streamed) but streamed lights are 1 m above brazier bowls and flames (`fire_fx.py`) float ~30 cm too high; bowls have no coals.
3. **Performance:** GPU saturated by Skyrim (Community Shaders) + Unreal at once; capped Unreal at 45 fps (GPU 90% -> 55%). Next: cull/simplify far geometry behind the new mountain haze (`mountain_mist.py`), instancing (HISM) for thousands of Python-spawned actors, find the editor memory growth.
4. **NPCs:** weapons, helmet hair hiding, dragons never verified live. Creatures: cow works.
5. Missing: dynamic doors/objects, DLSS (official plugin), the one space-named model (`clutter/chopping block/axe01.nif`, 3 refs).
6. Open question list: `notes/open_questions.md` (generated from the local model's notes; treat as leads).

## 5. How to work efficiently (token budget)
- Use `notes/index/SYMBOLS.md` + `rg` to jump to code. Read `notes/files/<file>.md` for orientation, then read only the functions you change.
- Verify live changes with `tools/ue_run.py` and low-res (1280x720) test shots into `screenshots/test/`, not 8K.
- Test one change at a time; keep a rollback (git diff) and restart the editor between experiments if memory > 25 GB.
- When something fails twice, read the editor log: `unreal/SkyBridge/Saved/Logs/SkyBridge.log` (look for `[SkyBridgeLive]`, `Assertion`, `Fatal`), Skyrim crash logs in `OneDrive/Documents/My Games/Skyrim Special Edition/SKSE/crash-*.log`.
